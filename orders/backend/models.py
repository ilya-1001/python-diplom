from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django_rest_passwordreset.tokens import get_token_generator

ORDER_STATE_CHOICES = (
    ('basket', 'Статус корзины'),
    ('new', 'Новый'),
    ('confirmed', 'Подтвержден'),
    ('assembled', 'Собран'),
    ('sent', 'Отправлен'),
    ('delivered', 'Доставлен'),
    ('canceled', 'Отменен'),
)

USER_TYPE_CHOICES = (
    ('supplier', 'Поставщик'),
    ('buyer', 'Покупатель'),
)


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Создает и возвращает пользователя с имэйлом, паролем.
        """
        if not email:
            raise ValueError('Необходимо указать адрес электронной почты')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """
        Создает и возввращет пользователя с привилегиями суперадмина.
        """
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('У суперпользователя должно быть значение is_superuser=True.')
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    """Модель пользователя"""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    email = models.EmailField(_('email address'), unique=True)
    company = models.CharField('Компания', max_length=40, blank=True)
    position = models.CharField('Должность', max_length=40, blank=True)

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={'unique': _("Пользователь с таким именем пользователя уже существует.")},
    )

    type = models.CharField('Тип пользователя', choices=USER_TYPE_CHOICES, max_length=10, default='buyer')

    is_active = models.BooleanField(
        _('active'),
        default=False,
        help_text=_('Указывает, следует ли считать этого пользователя активным. '
                    'Снимите этот флажок вместо удаления учетных записей.'),
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = "Список пользователей"
        ordering = ('email',)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Supplier(models.Model):
    """Модель поставщика"""
    name = models.CharField('Название', max_length=250)
    address = models.CharField('Адрес', max_length=100)
    city = models.CharField('Город', max_length=50)
    url = models.URLField('Ссылка', null=True, blank=True)
    user = models.OneToOneField(User, verbose_name='Пользователь', null=True, blank=True, on_delete=models.CASCADE)
    state = models.BooleanField('статус получения заказов', default=True)

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Список поставщиков'
        ordering = ('-name',)

    def __str__(self):
        return self.name


class Category(models.Model):
    """Модель категорий"""
    name = models.CharField('Название', max_length=100)
    suppliers = models.ManyToManyField(Supplier, verbose_name='Поставщики', related_name='categories', blank=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Список категорий'
        ordering = ['-name']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Модель продукта"""
    name = models.CharField('Название', max_length=80)
    category = models.ForeignKey(Category, verbose_name='Категория', related_name='products', blank=True,
                                 null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = "Список продуктов"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductInfo(models.Model):
    """Модель информации о продукте"""
    model = models.CharField('Модель', max_length=80, blank=True)
    external_id = models.PositiveIntegerField('Внешний ИД')
    product = models.ForeignKey(Product, verbose_name="Продукт", related_name="product_info",
                                blank=True, null=True, on_delete=models.CASCADE)
    supplier = models.ForeignKey(Supplier, verbose_name="Поставщик", related_name="product_info",
                                 blank=True, null=True, on_delete=models.CASCADE)
    quantity = models.IntegerField("Количество в наличии")
    price = models.IntegerField("Цена")
    price_rrc = models.IntegerField("Рекомендованная цена")

    class Meta:
        verbose_name = "Информация о продукте"
        verbose_name_plural = "Информационный список о продуктах"
        constraints = [
            models.UniqueConstraint(fields=['product', 'supplier', 'external_id'], name='unique_product_info'),
        ]

    def __str__(self):
        return f"{self.product.name} {self.supplier.name}"


class Parameter(models.Model):
    """Модель параметров"""
    name = models.CharField('Название', max_length=40)

    class Meta:
        verbose_name = 'Имя параметра'
        verbose_name_plural = "Список имен параметров"
        ordering = ('-name',)

    def __str__(self):
        return self.name


class ProductParameter(models.Model):
    """Модель параметров продукта"""
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='product_parameters',
                                     blank=True, null=True, on_delete=models.CASCADE)
    parameter = models.ForeignKey(Parameter, verbose_name='Параметр', related_name='product_parameters',
                                  blank=True, null=True, on_delete=models.CASCADE)
    value = models.CharField('Значение', max_length=100)

    class Meta:
        verbose_name = 'Параметр'
        verbose_name_plural = "Список параметров"
        constraints = [
            models.UniqueConstraint(fields=['product_info', 'parameter'], name='unique_product_parameter'),
        ]

    def __str__(self):
        return f'{self.parameter.name}: {self.value}'


class Contact(models.Model):
    """Модель контактов пользователя"""
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='contacts',
                             blank=True, null=True, on_delete=models.CASCADE)
    city = models.CharField('Город', max_length=50)
    street = models.CharField('Улица', max_length=100)
    house = models.CharField('Дом', max_length=15, blank=True)
    structure = models.CharField('Корпус', max_length=15, blank=True)
    building = models.CharField('Строение', max_length=15, blank=True)
    apartment = models.CharField('Квартира', max_length=15, blank=True)
    phone = models.CharField('Телефон', max_length=20)

    class Meta:
        verbose_name = 'Контакты пользователя'
        verbose_name_plural = "Список контактов пользователя"

    def __str__(self):
        return f'{self.city} {self.street} {self.house}'


class Order(models.Model):
    """Модель заказов"""
    user = models.ForeignKey(User, verbose_name='Пользователь', related_name='orders',
                             blank=True, null=True, on_delete=models.CASCADE)
    dt = models.DateTimeField(auto_now_add=True)
    state = models.CharField('Статус', choices=ORDER_STATE_CHOICES, max_length=15)
    contact = models.ForeignKey(Contact, verbose_name='Контакт', blank=True, null=True, on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = "Список заказ"
        ordering = ('-dt',)

    def __str__(self):
        return str(self.dt)


class OrderItem(models.Model):
    """Модель позиции заказа"""
    order = models.ForeignKey(Order, verbose_name='Заказ', related_name='ordered_items',
                              blank=True, null=True, on_delete=models.CASCADE)
    product_info = models.ForeignKey(ProductInfo, verbose_name='Информация о продукте',
                                     related_name='ordered_items', blank=True, null=True, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Количество')

    class Meta:
        verbose_name = 'Заказанная позиция'
        verbose_name_plural = "Список заказанных позиций"
        constraints = [
            models.UniqueConstraint(fields=['order_id', 'product_info'], name='unique_order_item'),
        ]


class ConfirmEmailToken(models.Model):
    """модель подтверждения электронной почты"""
    user = models.ForeignKey(
        User,
        related_name='confirm_email_tokens',
        on_delete=models.CASCADE,
        verbose_name=_("Пользователь, связанный с этим токеном сброса пароля")
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Когда был сгенерирован этот токен"))
    key = models.CharField(_("Key"), max_length=64, db_index=True, unique=True)

    class Meta:
        verbose_name = 'Токен подтверждения Email'
        verbose_name_plural = 'Токены подтверждения Email'

    @staticmethod
    def generate_key():
        return get_token_generator().generate_token()

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Password reset token for user {self.user}"