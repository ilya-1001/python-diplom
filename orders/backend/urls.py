from django.urls import path
from django_rest_passwordreset.views import reset_password_request_token, reset_password_confirm

from .views import SupplierUpdate, SignUp, LoginAccount, CategoryView, SupplierView, ProductInfoView, \
    BasketView, AccountDetails, ContactView, OrderView, SupplierState, SupplierOrders, ConfirmAccount

app_name = 'backend'
urlpatterns = [
    path('supplier/update', SupplierUpdate.as_view(), name='supplier-update'),
    path('supplier/state', SupplierState.as_view(), name='supplier-state'),
    path('supplier/orders', SupplierOrders.as_view(), name='supplier-orders'),
    path('user/register', SignUp.as_view(), name='user-register'),
    path('user/register/confirm', ConfirmAccount.as_view(), name='user-register-confirm'),
    path('user/details', AccountDetails.as_view(), name='user-details'),
    path('user/contact', ContactView.as_view(), name='user-contact'),
    path('user/login', LoginAccount.as_view(), name='user-login'),
    path('user/password_reset', reset_password_request_token, name='password-reset'),
    path('user/password_reset/confirm', reset_password_confirm, name='password-reset-confirm'),
    path('categories', CategoryView.as_view(), name='categories'),
    path('supplier', SupplierView.as_view(), name='suppliers'),
    path('products', ProductInfoView.as_view(), name='suppliers'),
    path('basket', BasketView.as_view(), name='basket'),
    path('order', OrderView.as_view(), name='order'),

]