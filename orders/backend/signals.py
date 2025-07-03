from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django.core.mail import send_mail
from .models import User, ConfirmEmailToken
from django_rest_passwordreset.signals import reset_password_token_created
from django.conf import settings

update_order = Signal()


# Уведомление о регистрации нового пользователя
@receiver(post_save, sender=User)
def new_user_registered(sender, instance, created, **kwargs):
    """
    отправляем письмо с токеном для подтрердждения почты
    """
    if created:
        token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)
        send_mail(
            subject='Подтверждение регистрации',
            message=(
            f"Здравствуйте, {instance.first_name}!\n\n"
            "Спасибо за регистрацию.\n"
            f"Ваш token подтверждения:\n\n"
            f"{token.key}\n\n"
            "Если вы не регистрировались, просто проигнорируйте это письмо."
        ),
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[instance.email],
        )


# Уведомление о формировании заказа
@receiver(update_order)
def process_order(user_id, **kwargs):
    """
    отправяем письмо при изменении статуса заказа
    """
    user = User.objects.get()
    send_mail(
    subject=f"Обновление статуса заказа",
    message='Заказ сформирован',
    from_email=settings.EMAIL_HOST_USER,
    recipient_list=[user.email],
    )


# Сброс пароля
@receiver(reset_password_token_created)
def notify_about_new_cats(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    """
    return send_mail(
        subject=f"Password Reset Token for {reset_password_token.user}",
        message=reset_password_token.key,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[reset_password_token.user.email],
    )
