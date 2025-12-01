from rest_framework import serializers
from .models import Cart, CartItem, Wishlist
from applications.products.serializers import ProductListSerializer
from applications.products.models import Product

class CartItemSerializer(serializers.ModelSerializer):
    """Serializer para items del carrito"""
    product = ProductListSerializer(read_only=True)
    subtotal = serializers.ReadOnlyField()
    unit_price = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'unit_price', 'subtotal', 'added_at']
        read_only_fields = ['added_at']

class CartItemCreateSerializer(serializers.Serializer):
    """Serializer para agregar productos"""
    product_id = serializers.IntegerField(required=True)
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Producto no encontrado o inactivo.")
        return value

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")
        return value

    def validate(self, data):
        try:
            product = Product.objects.get(id=data['product_id'])
            if data['quantity'] > product.stock:
                raise serializers.ValidationError({
                    "quantity": f"Stock insuficiente. Solo hay {product.stock} unidades."
                })
        except Product.DoesNotExist:
            pass
        return data

class CartItemUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar cantidad"""
    class Meta:
        model = CartItem
        fields = ['quantity']

    def validate_quantity(self, value):
        if value < 1:
            raise serializers.ValidationError("La cantidad debe ser al menos 1.")
        return value

    def validate(self, data):
        item = self.instance
        quantity = data.get('quantity', item.quantity)
        if quantity > item.product.stock:
            raise serializers.ValidationError({
                "quantity": f"Stock insuficiente. Solo hay {item.product.stock} unidades."
            })
        return data

class CartSerializer(serializers.ModelSerializer):
    """Serializer completo del carrito"""
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()
    item_count = serializers.ReadOnlyField()
    user = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = ['id', 'user', 'items', 'total_price', 'total_items', 'item_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

    def get_user(self, obj):
        if obj.user:
            return {'id': obj.user.id, 'username': obj.user.username, 'email': obj.user.email}
        return None

class WishlistSerializer(serializers.ModelSerializer):
    """Serializer para wishlist"""
    product = ProductListSerializer(read_only=True)
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Wishlist
        fields = ['id', 'user', 'product', 'notes', 'added_at']
        read_only_fields = ['added_at']

class WishlistCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear wishlist"""
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Wishlist
        fields = ['user', 'product_id', 'notes']

    def validate_product_id(self, value):
        try:
            Product.objects.get(id=value, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Producto no encontrado.")
        return value

    def validate(self, data):
        user = self.context['request'].user
        product_id = data['product_id']
        if Wishlist.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError("Este producto ya está en tu lista de deseos.")
        return data

    def create(self, validated_data):
        product_id = validated_data.pop('product_id')
        product = Product.objects.get(id=product_id)
        wishlist_item = Wishlist.objects.create(product=product, **validated_data)
        return wishlist_item
