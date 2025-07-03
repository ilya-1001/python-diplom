from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

from .views import SupplierUpdateView, SignUpView, LoginAccountView, CategoryListView, SupplierListView, ProductInfoView, \
    BasketView, AccountDetailsView, ContactView, OrderView, SupplierStateView, SupplierOrdersView, ConfirmAccountView

app_name = 'backend'
urlpatterns = [
    path('supplier/update', SupplierUpdateView.as_view(), name='supplier-update'),
    path('supplier/state', SupplierStateView.as_view(), name='supplier-state'),
    path('supplier/orders', SupplierOrdersView.as_view(), name='supplier-orders'),
    path('user/register', SignUpView.as_view(), name='user-register'),
    path('user/register/confirm', ConfirmAccountView.as_view(), name='user-register-confirm'),
    path('user/details', AccountDetailsView.as_view(), name='user-details'),
    path('user/contact', ContactView.as_view(), name='user-contact'),
    path('user/login', LoginAccountView.as_view(), name='user-login'),
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
    path('categories', CategoryListView.as_view(), name='categories'),
    path('supplier', SupplierListView.as_view(), name='suppliers'),
    path('products', ProductInfoView.as_view(), name='suppliers'),
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),

]