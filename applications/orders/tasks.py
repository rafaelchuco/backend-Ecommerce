from celery import shared_task
from django.core.mail import send_mail

@shared_task
def send_order_confirmation_email(user_email, order_number):
    subject = f"Confirmación de Orden {order_number}"
    message = f"Gracias por su compra. Su orden número {order_number} ha sido recibida."
    send_mail(subject, message, 'no-reply@ecommerce.com', [user_email])

@shared_task
def clean_old_carts():
    # Aquí la lógica para limpiar carritos antiguos
    pass
