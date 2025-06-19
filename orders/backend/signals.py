from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.core.mail import send_mail
from .models import User, ConfirmEmailToken, Order
from django_rest_passwordreset.signals import reset_password_token_created
from typing import Type
from django.conf import settings


# Уведомление о регистрации нового пользователя
@receiver(post_save, sender=User)
def new_user_registered(sender: Type[User], instance: User, created: bool, **kwargs):
    if created and not instance.is_active:
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)
        send_mail(
            subject=f"Password Reset Token for {instance.email}",
            message=token.key,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.email],
        )


# Обработка заказа
new_order = Signal()

@receiver(new_order)
def process_order(user_id, **kwargs):
    user = User.objects.get(id=user_id)

    return send_mail(
            subject=f"Обновление статуса заказа",
            message='Заказ сформирован',
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[user.email],
        )


# Сброс пароля
@receiver(reset_password_token_created)
def notify_about_new_cats(sender, instance, reset_password_token, **kwargs):
        return send_mail(
            subject=f"Password Reset Token for {reset_password_token.user}",
            message=reset_password_token.key,
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[reset_password_token.user.email],
        )
