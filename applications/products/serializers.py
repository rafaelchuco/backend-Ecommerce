from rest_framework import serializers
from django.db.models import Avg
from .models import Category, Brand, Material, Product, ProductImage, ProductSpecification, Review


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer básico para listar categorías
    """
    product_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'image', 'product_count', 'is_active']


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado con subcategorías
    """
    subcategories = CategoryListSerializer(many=True, read_only=True)
    parent = CategoryListSerializer(read_only=True)
    product_count = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'image',
            'parent', 'subcategories', 'is_active', 'order',
            'product_count', 'created_at', 'updated_at'
        ]


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer para marcas
    """
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'logo', 'description', 'is_active', 'product_count']
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class MaterialSerializer(serializers.ModelSerializer):
    """
    Serializer para materiales
    """
    class Meta:
        model = Material
        fields = ['id', 'name', 'description']


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer para imágenes de productos
    """
    image = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'is_primary', 'alt_text', 'order']
    
    def get_image(self, obj):
        request = self.context.get('request')
        if obj.image and hasattr(obj.image, 'url'):
            return request.build_absolute_uri(obj.image.url) if request else obj.image.url
        return None


class ProductSpecificationSerializer(serializers.ModelSerializer):
    """
    Serializer para especificaciones
    """
    class Meta:
        model = ProductSpecification
        fields = ['id', 'name', 'value', 'order']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer resumido para listados de productos
    """
    category = CategoryListSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    final_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'sku',
            'category', 'brand',
            'price', 'discount_price', 'final_price', 'discount_percentage',
            'primary_image', 'stock', 'is_in_stock',
            'is_featured', 'is_new',
            'average_rating', 'review_count',
            'created_at'
        ]
    
    def get_primary_image(self, obj):
        request = self.context.get('request')
        image = obj.images.filter(is_primary=True).first()
        if image and hasattr(image.image, 'url'):
            return request.build_absolute_uri(image.image.url) if request else image.image.url
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer completo para detalle de producto
    """
    category = CategoryDetailSerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    materials = MaterialSerializer(many=True, read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    specifications = ProductSpecificationSerializer(many=True, read_only=True)
    final_price = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = '__all__'


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear productos (admin)
    """
    class Meta:
        model = Product
        exclude = ['slug', 'views_count', 'created_at', 'updated_at']
    
    def validate_discount_price(self, value):
        """
        Valida que el precio con descuento sea menor al precio normal
        """
        if value and 'price' in self.initial_data:
            price = float(self.initial_data['price'])
            if value >= price:
                raise serializers.ValidationError(
                    "El precio con descuento debe ser menor al precio normal."
                )
        return value
    
    def validate_stock(self, value):
        """
        Valida que el stock sea positivo
        """
        if value < 0:
            raise serializers.ValidationError("El stock no puede ser negativo.")
        return value


class ProductUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer para actualizar productos
    """
    class Meta:
        model = Product
        exclude = ['slug', 'created_at', 'updated_at']


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer para mostrar reviews
    """
    user = serializers.SerializerMethodField()
    
    class Meta:
        model = Review
        fields = [
            'id', 'product', 'user', 'rating', 'title', 'comment',
            'is_verified_purchase', 'is_approved',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['is_verified_purchase', 'is_approved']
    
    def get_user(self, obj):
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'first_name': obj.user.first_name,
        }


class ReviewCreateSerializer(serializers.ModelSerializer):
    """
    Serializer para crear/actualizar reviews
    """
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())
    
    class Meta:
        model = Review
        fields = ['product', 'user', 'rating', 'title', 'comment']
    
    def validate_rating(self, value):
        """
        Valida que el rating esté entre 1 y 5
        """
        if not 1 <= value <= 5:
            raise serializers.ValidationError("El rating debe estar entre 1 y 5.")
        return value
    
    def validate(self, attrs):
        """
        Valida que el usuario no haya hecho review previamente
        """
        user = self.context['request'].user
        product = attrs['product']
        
        if self.instance is None:  # Solo en creación
            if Review.objects.filter(user=user, product=product).exists():
                raise serializers.ValidationError(
                    "Ya has hecho una review de este producto."
                )
        
        return attrs