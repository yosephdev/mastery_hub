from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from celery import shared_task
from .models import Order

@shared_task
def send_order_confirmation(order_id):
    """
    Task to send an order confirmation email
    """
    try:
        order = Order.objects.get(id=order_id)
        subject = f'MasteryHub - Order Confirmation #{order.order_number}'                
       
        recipient_email = order.email or order.user.email
        
        context = {
            'order': order,
            'contact_email': settings.DEFAULT_FROM_EMAIL,
            'site_name': 'MasteryHub',
        }        
        
        message = render_to_string(
            'checkout/confirmation_emails/confirmation_email.txt',
            context
        )        
       
        html_message = render_to_string(
            'checkout/confirmation_emails/confirmation_email.html',
            context
        )        
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [recipient_email],
            fail_silently=False,
            html_message=html_message
        )
        
        return f"Confirmation email sent for order {order.order_number}"
        
    except Order.DoesNotExist:
        return f"Order {order_id} not found"
    except Exception as e:
        return f"Error sending confirmation email: {str(e)}" 