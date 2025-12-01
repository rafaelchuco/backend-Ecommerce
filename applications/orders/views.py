from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http import HttpResponse
from reportlab.pdfgen import canvas
import io
import stripe
from django.conf import settings
from drf_spectacular.utils import extend_schema

from .models import Order, Coupon
from .serializers import (
    OrderListSerializer, OrderDetailSerializer, OrderCreateSerializer, CouponSerializer
)
from .permissions import IsOwner
from .utils import get_user_orders

# Config Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


@extend_schema(tags=['Orders'])
class OrderViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.AllowAny]
    serializer_class = OrderListSerializer
    lookup_field = 'order_number'

    def get_queryset(self):
        # Si está autenticado, mostrar solo sus órdenes
        # Si no está autenticado, devolver vacío (para POST funciona igual)
        user = self.request.user
        if user and user.is_authenticated:
            return Order.objects.filter(user=user).order_by('-created_at')
        # Para POST de invitados, get_queryset no se usa
        # Para GET, devolvemos vacío
        return Order.objects.none()

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return OrderDetailSerializer
        elif self.action == 'create':
            return OrderCreateSerializer
        return OrderListSerializer

    def perform_create(self, serializer):
        # El serializer ya maneja usuarios en su método create
        serializer.save()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Retornar los datos completos de la orden creada
        order = serializer.instance
        return_serializer = OrderDetailSerializer(order)
        headers = self.get_success_headers(serializer.data)
        return Response(return_serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['put'], url_path='cancel')
    def cancel_order(self, request, order_number=None):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        if order.status not in ['pending', 'confirmed']:
            return Response({"error": "No se puede cancelar esta orden"}, status=status.HTTP_400_BAD_REQUEST)
        order.status = 'cancelled'
        order.save()
        for item in order.items.all():
            if item.product:
                item.product.stock += item.quantity
                item.product.save()
        return Response({"message": "Orden cancelada y stock restaurado"}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='invoice')
    def get_invoice(self, request, order_number=None):
        order = get_object_or_404(Order, order_number=order_number, user=request.user)
        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        p.setFont("Helvetica-Bold", 16)
        p.drawString(100, 800, f"Factura: {order.order_number}")
        p.setFont("Helvetica", 12)
        p.drawString(100, 780, f"Cliente: {order.full_name}")
        p.drawString(100, 760, f"Fecha: {order.created_at.strftime('%d/%m/%Y')}")
        y = 740
        p.setFont("Helvetica-Bold", 11)
        p.drawString(100, y, "Producto     Cantidad     Precio")
        y -= 20
        p.setFont("Helvetica", 11)
        for item in order.items.all():
            p.drawString(100, y, f"{item.product_name[:15]:<15}{item.quantity:<10}{item.product_price:<8}")
            y -= 18
        p.setFont("Helvetica-Bold", 12)
        p.drawString(100, y - 10, f"Total: S/ {order.total}")
        p.showPage()
        p.save()
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')


@extend_schema(tags=['Orders'])
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def validate_coupon(request):
    code = request.data.get('code')
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
        return Response({
            "valid": True,
            "discount": str(coupon.discount_value),
            "type": coupon.discount_type
        })
    except Coupon.DoesNotExist:
        return Response({"valid": False, "discount": "0"})


@extend_schema(tags=['Payments'])
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def create_payment_intent(request):
    """
    Crea un PaymentIntent de Stripe.
    Body: { "amount": 20000 }  # centavos
    """
    try:
        amount = int(request.data.get('amount'))
        
        # Definir metadata según si está logueado o no
        metadata = {}
        if request.user.is_authenticated:
            metadata["user_id"] = request.user.id
            metadata["username"] = request.user.username
        else:
            metadata["user_id"] = "guest"
            metadata["username"] = "guest"

        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency='pen', # Asegúrate que coincida con tu cuenta Stripe (pen/usd)
            automatic_payment_methods={"enabled": True},
            metadata=metadata,
        )
        return Response(
            {"clientSecret": intent.client_secret, "paymentIntentId": intent.id},
            status=status.HTTP_200_OK,
        )
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Payments'])
@api_view(['POST'])
@permission_classes([permissions.AllowAny]) 
def confirm_payment(request):
    """
    Confirma el pago y crea la orden.
    Espera:
    {
        "payment_intent_id": "pi_..." or "sim_...",
        "order": { ...datos para OrderCreateSerializer... }
    }
    """
    try:
        payment_intent_id = request.data.get('payment_intent_id')
        order_data = request.data.get('order', {})

        # Si es un pago simulado (modo test), saltamos la verificación en Stripe
        if not payment_intent_id.startswith('sim_'):
            # Verificar estado en Stripe (para pagos reales)
            try:
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                if intent.status != 'succeeded':
                    return Response({"error": "Pago no completado"}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as stripe_error:
                # Si Stripe no está configurado correctamente, permitir simulación
                if 'Invalid API Key' in str(stripe_error):
                    print(f"⚠️ Stripe no configurado, aceptando pago simulado: {payment_intent_id}")
                else:
                    raise

        order_data['is_paid'] = True
        order_data['payment_method'] = 'credit_card' if payment_intent_id.startswith('sim_') or payment_intent_id.startswith('pi_') else 'credit_card'
        order_data['payment_id'] = payment_intent_id

        serializer = OrderCreateSerializer(data=order_data, context={'request': request})
        
        if serializer.is_valid():
            # Guardar la orden pasando el usuario explícitamente
            user_to_save = request.user if request.user.is_authenticated else None
            order = serializer.save(user=user_to_save)
            
            return Response(
                {
                    "message": "Orden creada exitosamente",
                    "order_number": order.order_number,
                    "order": OrderDetailSerializer(order).data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

