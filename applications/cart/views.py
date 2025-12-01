from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Prefetch
from .models import Cart, CartItem, Wishlist
from .serializers import (
    CartSerializer, CartItemSerializer, CartItemCreateSerializer,
    CartItemUpdateSerializer, WishlistSerializer, WishlistCreateSerializer
)
from drf_spectacular.utils import extend_schema
from applications.products.models import Product

@extend_schema(tags=['Cart'])
class CartViewSet(viewsets.ViewSet):
    """ViewSet para gestionar el carrito"""
    
    def get_permissions(self):
        return [AllowAny()]
    
    def get_cart(self, request):
        if request.user.is_authenticated:
            cart, created = Cart.objects.prefetch_related(
                Prefetch('items__product')
            ).get_or_create(user=request.user, is_active=True)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart, created = Cart.objects.prefetch_related(
                Prefetch('items__product')
            ).get_or_create(session_id=session_id, is_active=True)
        return cart
    
    def list(self, request):
        cart = self.get_cart(request)
        serializer = CartSerializer(cart, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], url_path='items')
    def add_item(self, request):
        serializer = CartItemCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        cart = self.get_cart(request)
        product_id = serializer.validated_data['product_id']
        quantity = serializer.validated_data['quantity']
        
        try:
            cart_item = CartItem.objects.select_related('product').get(cart=cart, product_id=product_id)
            new_quantity = cart_item.quantity + quantity
            product = cart_item.product
            if new_quantity > product.stock:
                return Response({
                    "error": f"Stock insuficiente. Solo hay {product.stock} unidades."
                }, status=status.HTTP_400_BAD_REQUEST)
            cart_item.quantity = new_quantity
            cart_item.save()
            message = "Cantidad actualizada"
        except CartItem.DoesNotExist:
            product = Product.objects.get(id=product_id)
            cart_item = CartItem.objects.create(cart=cart, product=product, quantity=quantity)
            message = "Producto agregado al carrito"
        
        item_serializer = CartItemSerializer(cart_item, context={'request': request})
        return Response({
            "message": message,
            "item": item_serializer.data,
            "cart_total": cart.total_price,
            "cart_items_count": cart.total_items
        }, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put', 'patch'], url_path='update')
    def update_item(self, request, pk=None):
        cart = self.get_cart(request)
        try:
            cart_item = CartItem.objects.select_related('product').get(id=pk, cart=cart)
        except CartItem.DoesNotExist:
            return Response({"error": "Item no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CartItemUpdateSerializer(cart_item, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response({
            "message": "Cantidad actualizada",
            "item": CartItemSerializer(cart_item, context={'request': request}).data,
            "cart_total": cart.total_price
        })
    
    @action(detail=True, methods=['delete'], url_path='remove')
    def remove_item(self, request, pk=None):
        cart = self.get_cart(request)
        try:
            cart_item = CartItem.objects.get(id=pk, cart=cart)
            product_name = cart_item.product.name
            cart_item.delete()
            return Response({
                "message": f"{product_name} eliminado del carrito",
                "cart_total": cart.total_price,
                "cart_items_count": cart.total_items
            })
        except CartItem.DoesNotExist:
            return Response({"error": "Item no encontrado."}, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['delete'], url_path='clear')
    def clear_cart(self, request):
        cart = self.get_cart(request)
        items_count = cart.items.count()
        cart.items.all().delete()
        return Response({
            "message": f"Carrito vaciado. {items_count} productos eliminados.",
            "cart_total": 0,
            "cart_items_count": 0
        })

@extend_schema(tags=['Cart'])
class WishlistViewSet(viewsets.ModelViewSet):
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product')
    
    def get_serializer_class(self):
        if self.action == 'create':
            return WishlistCreateSerializer
        return WishlistSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'], url_path='move-to-cart')
    def move_to_cart(self, request, pk=None):
        try:
            wishlist_item = self.get_queryset().get(pk=pk)
            cart, _ = Cart.objects.get_or_create(user=request.user, is_active=True)
            cart_item, created = CartItem.objects.get_or_create(
                cart=cart,
                product=wishlist_item.product,
                defaults={'quantity': 1}
            )
            if not created:
                cart_item.quantity += 1
                cart_item.save()
            wishlist_item.delete()
            return Response({
                "message": f"{cart_item.product.name} movido al carrito",
                "cart_total": cart.total_price
            })
        except Wishlist.DoesNotExist:
            return Response({"error": "Producto no encontrado en wishlist."}, status=status.HTTP_404_NOT_FOUND)
