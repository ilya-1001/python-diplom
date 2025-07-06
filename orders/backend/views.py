from rest_framework import generics, permissions, status, views
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.db import IntegrityError, transaction
from django.db.models import Q, Sum, F
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import json
from requests import get
from yaml import load as load_yaml, Loader

from .models import (Supplier, Category, ProductInfo, ProductParameter, Order, OrderItem,
                     Contact, ConfirmEmailToken, Product, Parameter)
from .serializers import (UserSerializer, SupplierSerializer, CategorySerializer, ProductInfoSerializer,
                          OrderItemSerializer, OrderSerializer, ContactSerializer)
from .permissions import IsAuthenticatedAndSupplier
from .signals import update_order


class BaseAPIView(views.APIView):
    """
    Базовый класс для вью с общими методами для обработки ошибок и парсинга JSON.
    """
    def error_response(self, errors, status_code=status.HTTP_400_BAD_REQUEST):
        """
        Упрощенный ответ с ошибкой в едином формате.
        """
        return Response({'status': False, 'errors': errors}, status=status_code)

    def parse_json(self, data):
        """
        Преобразование переданных данных в Python-объект.
        Возвращает кортеж (данные, ошибка). Если ошибка не None — её нужно вернуть клиенту.
        """
        if not data:
            return None, self.error_response('Не указаны все необходимые аргументы')
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except json.JSONDecodeError:
                return None, self.error_response('Неверный формат запроса')
        return data, None


class SignUpView(generics.CreateAPIView):
    """
    Вью для регистрации пользователя.
    Использует UserSerializer, разрешает запросы без авторизации.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]


class ConfirmAccountView(BaseAPIView):
    """
    Вью подтверждения аккаунта через email и токен.
    При успешной верификации активирует пользователя и удаляет токен.
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email, token_key = request.data.get('email'), request.data.get('token')

        if not email or not token_key:
            return self.error_response('Не указаны все необходимые аргументы')

        token = ConfirmEmailToken.objects.filter(user__email=email, key=token_key).first()
        if token:
            user = token.user
            user.is_active = True
            user.save()
            token.delete()
            return Response({'status': True})
        return self.error_response('Неверный email или токен')


class AccountDetailsView(generics.RetrieveUpdateAPIView):
    """
    Просмотр и редактирование деталей учётной записи.
    Возвращает и обновляет данные текущего пользователя.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class LoginAccountView(BaseAPIView):
    """
    Авторизация пользователя — проверка email и пароля.
    Если успешно, возвращает токен (DRF TokenAuthentication).
    """
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email, password = request.data.get('email'), request.data.get('password')

        if not email or not password:
            return self.error_response('Не указаны все необходимые аргументы')

        user = authenticate(request, username=email, password=password)
        if user and user.is_active:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({'status': True, 'token': token.key})
        return self.error_response('Неправильный email или пароль')


class CategoryListView(generics.ListAPIView):
    """
    Просмотр всех категорий.
    Доступ для всех пользователей (даже без авторизации).
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]


class SupplierListView(generics.ListAPIView):
    """
    Просмотр поставщиков, у которых включен статус активности.
    Доступ открыт всем.
    """
    queryset = Supplier.objects.filter(state=True)
    serializer_class = SupplierSerializer
    permission_classes = [permissions.AllowAny]


class ProductInfoView(generics.ListAPIView):
    """
    Поиск товаров с фильтрацией по поставщику и категории.
    Используются оптимизации запросов (select_related и prefetch_related).
    """
    serializer_class = ProductInfoSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        params = self.request.query_params
        query = Q(supplier__state=True)  # только активные поставщики
        for key, field in [('supplier_id', 'supplier_id'), ('category_id', 'product__category_id')]:
            val = params.get(key)
            if val:
                query &= Q(**{field: val})
        return (ProductInfo.objects.filter(query)
                .select_related('supplier', 'product__category')
                .prefetch_related('product_parameters__parameter')
                .order_by('id')
                .distinct())


class BasketView(BaseAPIView):
    """
    Управление корзиной пользователя: просмотр, добавление, удаление и редактирование товаров.
    Все операции доступны только авторизованным пользователям.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        """
        Получить корзину текущего пользователя.
        Суммирует стоимость всех товаров в корзине.
        """
        basket_qs = (Order.objects.filter(user=request.user, state='basket')
                     .prefetch_related('ordered_items__product_info__product__category',
                                       'ordered_items__product_info__product_parameters__parameter')
                     .annotate(total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price')))
                     .distinct())
        serializer = OrderSerializer(basket_qs, many=True)
        return Response(serializer.data)

    def post(self, request):
        """
        Добавить позиции в корзину.
        Ожидает поле 'items' — список словарей.
        Валидация и сохранение с обработкой ошибок.
        """
        items, error = self.parse_json(request.data.get('items'))
        if error:
            return error

        basket, _ = Order.objects.get_or_create(user=request.user, state='basket')
        created = 0
        for order_item in items:
            order_item['order'] = basket.id
            serializer = OrderItemSerializer(data=order_item)
            if not serializer.is_valid():
                return self.error_response(serializer.errors)
            try:
                serializer.save()
                created += 1
            except IntegrityError as e:
                return self.error_response(str(e))

        return Response({'status': True, 'created_objects': created})

    def delete(self, request):
        """
        Удаление товаров из корзины по переданным id.
        Проверка корректности переданных id.
        """
        items_str = request.data.get('items', '')
        basket, _ = Order.objects.get_or_create(user=request.user, state='basket')
        valid_ids = [item_id for item_id in items_str.split(',') if item_id.isdigit()]
        if not valid_ids:
            return self.error_response('Некорректные ID для удаления')
        query = Q()
        for order_item_id in valid_ids:
            query |= Q(order=basket, id=order_item_id)
        deleted_count, _ = OrderItem.objects.filter(query).delete()
        return Response({'status': True, 'deleted_objects': deleted_count})

    def put(self, request):
        """
        Редактирование количества товаров в корзине.
        Ожидаются 'id' и 'quantity' в каждом объекте из 'items'.
        """
        items, error = self.parse_json(request.data.get('items'))
        if error:
            return error
        basket, _ = Order.objects.get_or_create(user=request.user, state='basket')
        updated = 0
        for order_item in items:
            item_id, quantity = order_item.get('id'), order_item.get('quantity')
            if isinstance(item_id, int) and isinstance(quantity, int):
                updated += OrderItem.objects.filter(order=basket, id=item_id).update(quantity=quantity)
        return Response({'status': True, 'updated_objects': updated})


class SupplierUpdateView(BaseAPIView):
    """
    Обновление информации о поставщике через загрузку YAML файла по URL.
    Валидация url, загрузка и парсинг, создание обновленных данных о товарах и категориях.
    """
    permission_classes = [IsAuthenticatedAndSupplier]

    def validate_url(self, url):
        """
        Проверка корректности URL.
        """
        try:
            URLValidator()(url)
            return True, None
        except ValidationError as e:
            return False, str(e)

    def load_yaml_data(self, url):
        """
        Загрузка и парсинг YAML с URL.
        """
        try:
            stream = get(url).content
            data = load_yaml(stream, Loader=Loader)
            return data, None
        except Exception as e:
            return None, f"Ошибка загрузки данных: {e}"

    def post(self, request):
        url = request.data.get('url')
        if not url:
            return self.error_response('Не указаны все необходимые аргументы')

        valid, error = self.validate_url(url)
        if not valid:
            return self.error_response(error)

        data, error = self.load_yaml_data(url)
        if error:
            return self.error_response(error)

        # Создание или получение поставщика
        supplier, _ = Supplier.objects.get_or_create(name=data['supplier'], user=request.user)

        # Создание категорий и установка связи с поставщиком
        for category in data.get('categories', []):
            cat_obj, _ = Category.objects.get_or_create(id=category['id'], defaults={'name': category['name']})
            cat_obj.suppliers.add(supplier)
            cat_obj.save()

        # Удаление старой информации по продуктам данного поставщика
        ProductInfo.objects.filter(supplier=supplier).delete()

        # Добавление новой информации о продуктах и их параметрах
        for item in data.get('goods', []):
            product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])
            product_info = ProductInfo.objects.create(
                product=product,
                external_id=item['id'],
                model=item.get('model', ''),
                price=item['price'],
                price_rrc=item['price_rrc'],
                quantity=item['quantity'],
                supplier=supplier,
            )
            ProductParameter.objects.bulk_create([
                ProductParameter(
                    product_info=product_info,
                    parameter=Parameter.objects.get_or_create(name=name)[0],
                    value=value
                ) for name, value in item.get('parameters', {}).items()
            ])

        return Response({'status': True})


class SupplierStateView(BaseAPIView):
    """
    Получение и изменение статуса поставщика.
    """
    permission_classes = [IsAuthenticatedAndSupplier]

    def get(self, request):
        """
        Получение текущего статуса поставщика.
        """
        serializer = SupplierSerializer(request.user.supplier)
        return Response(serializer.data)

    def post(self, request):
        """
        Изменение статуса: принимает параметры, переводит строковые представления True/False в булевые значения.
        """
        state = request.data.get('state')
        if state is None:
            return self.error_response('Не указан параметр state')

        state_bool = 1 if str(state).lower() in ('y', 'yes', 't', 'true', 'on', '1') else 0
        Supplier.objects.filter(user=request.user).update(state=state_bool)
        return Response({'status': True})


class SupplierOrdersView(BaseAPIView):
    """
    Получение заказов, относящихся к поставщику.
    """
    permission_classes = [IsAuthenticatedAndSupplier]

    def get(self, request):
        orders = (Order.objects.filter(ordered_items__product_info__supplier__user=request.user)
                  .exclude(state='basket')
                  .prefetch_related('ordered_items__product_info__product__category',
                                    'ordered_items__product_info__product_parameters__parameter')
                  .select_related('contact')
                  .annotate(total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price')))
                  .distinct())
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class ContactView(BaseAPIView):
    """
    Управление контактной информации пользователя: просмотр, добавление, удаление, изменение.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        contacts = Contact.objects.filter(user=request.user)
        serializer = ContactSerializer(contacts, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = request.data.copy()
        data['user'] = request.user.id
        serializer = ContactSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True})
        return self.error_response(serializer.errors)

    def delete(self, request):
        items_str = request.data.get('items')
        if not items_str:
            return self.error_response('Не указаны все необходимые аргументы')
        valid_ids = [cid for cid in items_str.split(',') if cid.isdigit()]
        if not valid_ids:
            return self.error_response('Некорректные ID')
        query = Q()
        for contact_id in valid_ids:
            query |= Q(id=contact_id, user=request.user)
        deleted_count, _ = Contact.objects.filter(query).delete()
        return Response({'status': True, 'deleted_objects': deleted_count})

    def put(self, request):
        contact_id = request.data.get('id')
        if not contact_id or not str(contact_id).isdigit():
            return self.error_response('Не указан или некорректен ID')
        contact = Contact.objects.filter(id=contact_id, user=request.user).first()
        if not contact:
            return self.error_response('Контакт не найден')
        serializer = ContactSerializer(contact, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': True})
        return self.error_response(serializer.errors)


class OrderView(BaseAPIView):
    """
    Просмотр и размещение заказов пользователем.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        orders = (Order.objects.filter(user=request.user)
                  .exclude(state='basket')
                  .prefetch_related('ordered_items__product_info__product__category',
                                    'ordered_items__product_info__product_parameters__parameter')
                  .select_related('contact')
                  .annotate(total_sum=Sum(F('ordered_items__quantity') * F('ordered_items__product_info__price')))
                  .distinct()
                  .order_by('-dt'))
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def post(self, request):
        order_id = request.data.get('id')
        contact_id = request.data.get('contact')
        if not order_id or not str(order_id).isdigit() or not contact_id:
            return self.error_response('Не указаны все необходимые аргументы')
        try:
            with transaction.atomic():
                updated = Order.objects.filter(user=request.user, id=order_id).update(contact_id=contact_id, state='new')
                if not updated:
                    return self.error_response('Заказ не найден')
                update_order.send(sender=self.__class__, user_id=request.user.id)
                return Response({'status': True})
        except IntegrityError:
            return self.error_response('Ошибка при обновлении заказа')
