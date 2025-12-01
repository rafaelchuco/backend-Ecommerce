# Create your views here.
from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Count, Avg
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes


from .models import Category, Brand, Material, Product, Review
from .serializers import (
    CategoryListSerializer, CategoryDetailSerializer,
    BrandSerializer, MaterialSerializer,
    ProductListSerializer, ProductDetailSerializer,
    ProductCreateSerializer, ProductUpdateSerializer,
    ReviewSerializer, ReviewCreateSerializer
)
from .filters import ProductFilter
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdmin

@extend_schema(tags=['Products'])
class CategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de categorías
    GET /api/products/categories/ - Listar categorías
    GET /api/products/categories/{slug}/ - Detalle de categoría
    POST /api/products/categories/ - Crear (admin)
    """
    queryset = Category.objects.filter(is_active=True)
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return CategoryDetailSerializer
        return CategoryListSerializer
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='slug',
                description='Slug de la categoría (en la URL)',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
        description='Obtener subcategorías de una categoría específica'
    )
    def subcategories(self, request, slug=None):
        """
        Obtener subcategorías de una categoría
        GET /api/products/categories/{slug}/subcategories/
        """
        category = self.get_object()
        subcategories = category.subcategories.filter(is_active=True)
        serializer = CategoryListSerializer(subcategories, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='slug',
                description='Slug de la categoría (en la URL)',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
            OpenApiParameter(
                name='page',
                description='Número de página para paginación',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        description='Obtener productos de una categoría específica'
    )
    def products(self, request, slug=None):
        """
        Obtener productos de una categoría
        GET /api/products/categories/{slug}/products/
        """
        category = self.get_object()
        products = Product.objects.filter(
            category=category,
            is_active=True
        ).select_related('category', 'brand').prefetch_related('images', 'materials')
        
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)

@extend_schema(tags=['Products'])
class BrandViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de marcas
    """
    queryset = Brand.objects.filter(is_active=True)
    serializer_class = BrandSerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                description='Buscar por nombre o descripción de la marca',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='ordering',
                description='Ordenar por: name, -name, created_at, -created_at',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='page',
                description='Número de página para paginación',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        description='Listar todas las marcas activas con búsqueda y ordenamiento'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=['Products'])
class MaterialViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet solo lectura para materiales
    """
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                description='Buscar materiales por nombre',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='page',
                description='Número de página para paginación',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ],
        description='Listar todos los materiales disponibles'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


@extend_schema(tags=['Products'])
class ProductViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para productos con filtros y búsqueda
    """
    queryset = Product.objects.filter(is_active=True).select_related(
        'category', 'brand'
    ).prefetch_related(
        'materials', 'images', 'specifications', 'reviews'
    )
    permission_classes = [IsAdminOrReadOnly]
    lookup_field = 'slug'
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = ProductFilter
    search_fields = ['name', 'description', 'sku']
    ordering_fields = ['price', 'created_at', 'name', 'views_count']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action in ['create']:
            return ProductCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductUpdateSerializer
        return ProductListSerializer
    
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='search',
                description='Buscar por nombre, descripción o SKU del producto',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                examples=[
                    OpenApiExample('Ejemplo', value='sofá moderno')
                ]
            ),
            OpenApiParameter(
                name='page',
                description='Número de página (paginación por defecto: 20 por página)',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='price_min',
                description='Precio mínimo del producto (filtro)',
                required=False,
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='price_max',
                description='Precio máximo del producto (filtro)',
                required=False,
                type=OpenApiTypes.DECIMAL,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='category',
                description='Filtrar por categoría (slug)',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='brand',
                description='Filtrar por marca (slug)',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='in_stock',
                description='Filtrar solo productos en stock (true/false)',
                required=False,
                type=OpenApiTypes.BOOL,
                location=OpenApiParameter.QUERY,
            ),
            OpenApiParameter(
                name='ordering',
                description='Ordenar por: price, -price, created_at, -created_at, name, views_count',
                required=False,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
            ),
        ],
        description='Listar productos con filtros, búsqueda y ordenamiento'
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
    
    def retrieve(self, request, *args, **kwargs):
        """
        Incrementa contador de vistas al ver detalle
        """
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    @extend_schema(
        description='Obtener hasta 12 productos destacados (is_featured=true)',
        parameters=[
            OpenApiParameter(
                name='page',
                description='Número de página (opcional)',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    def featured(self, request):
        """
        Productos destacados
        GET /api/products/featured/
        """
        products = self.get_queryset().filter(is_featured=True)[:12]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    @extend_schema(
        description='Obtener hasta 12 productos nuevos (is_new=true), ordenados por fecha de creación',
        parameters=[
            OpenApiParameter(
                name='page',
                description='Número de página (opcional)',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    def new(self, request):
        """
        Productos nuevos
        GET /api/products/new/
        """
        products = self.get_queryset().filter(is_new=True).order_by('-created_at')[:12]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    @extend_schema(
        description='Obtener hasta 12 productos más vendidos (ordenados por vistas, actualizado cuando se integren ordenes reales)',
        parameters=[
            OpenApiParameter(
                name='page',
                description='Número de página (opcional)',
                required=False,
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
            ),
        ]
    )
    def best_sellers(self, request):
        """
        Productos más vendidos (por ahora por vistas)
        GET /api/products/best-sellers/
        TODO: Implementar basado en ventas reales cuando se integre orders
        """
        products = self.get_queryset().order_by('-views_count')[:12]
        serializer = ProductListSerializer(products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='slug',
                description='Slug del producto (en la URL)',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
        description='Obtener hasta 6 productos relacionados (misma categoría)'
    )
    def related(self, request, slug=None):
        """
        Productos relacionados (misma categoría)
        GET /api/products/{slug}/related/
        """
        product = self.get_object()
        related_products = self.get_queryset().filter(
            category=product.category
        ).exclude(id=product.id)[:6]
        
        serializer = ProductListSerializer(related_products, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def increment_view(self, request, slug=None):
        """
        Incrementar contador de vistas
        POST /api/products/{slug}/increment-view/
        """
        product = self.get_object()
        product.increment_views()
        return Response({'views_count': product.views_count})
    
    @action(detail=True, methods=['get'])
    @extend_schema(
        parameters=[
            OpenApiParameter(
                name='slug',
                description='Slug del producto (en la URL)',
                required=True,
                type=OpenApiTypes.STR,
                location=OpenApiParameter.PATH,
            ),
        ],
        description='Obtener reviews aprobadas de un producto, ordenadas por fecha descendente'
    )
    def reviews(self, request, slug=None):
        """
        Obtener reviews de un producto
        GET /api/products/{slug}/reviews/
        """
        product = self.get_object()
        reviews = product.reviews.filter(is_approved=True).order_by('-created_at')
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)


@extend_schema(tags=['Products'])
class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de reviews
    """
    queryset = Review.objects.filter(is_approved=True)
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrAdmin]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReviewCreateSerializer
        return ReviewSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        product_slug = self.request.query_params.get('product', None)
        if product_slug:
            queryset = queryset.filter(product__slug=product_slug)
        return queryset
    
    def perform_create(self, serializer):
        """
        Crear review y verificar si es compra verificada
        TODO: Implementar verificación real con orders
        """
        serializer.save(
            user=self.request.user,
            is_verified_purchase=False  # Cambiar cuando se integre con orders
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def my_reviews(self, request):
        """
        Obtener reviews del usuario autenticado
        GET /api/products/reviews/my-reviews/
        """
        reviews = Review.objects.filter(user=request.user)
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)