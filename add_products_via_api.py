"""
Script alternativo para agregar 100 productos usando los serializers
Ejecución: python manage.py shell < add_products_via_api.py
"""
import os
import django
from decimal import Decimal
import random
from faker import Faker

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from applications.products.models import Product, Category, Brand, Material
from applications.products.serializers import ProductCreateSerializer

fake = Faker('es_ES')

# Categorías y datos base
PRODUCT_TEMPLATES = [
    {"category": "Muebles de Sala", "names": ["Sofá", "Silla", "Mesa de Centro", "Reposapié", "Estantería"]},
    {"category": "Muebles de Comedor", "names": ["Comedor", "Silla de Comedor", "Buffet", "Servilleta"]},
    {"category": "Muebles de Dormitorio", "names": ["Cama", "Mesita de Noche", "Armario", "Cómoda"]},
    {"category": "Muebles de Oficina", "names": ["Escritorio", "Silla de Oficina", "Estante", "Cajonera"]},
    {"category": "Accesorios y Decoración", "names": ["Lámpara", "Espejo", "Cuadro", "Tapete", "Cortina"]},
]

COLORS = ["Negro", "Blanco", "Gris", "Marrón", "Beige", "Azul", "Verde", "Rojo", "Champagne", "Oro", "Plateado", "Rosa"]

MATERIALS_DATA = ["Cuero", "Tela", "Madera", "Metal", "Vidrio", "Plástico", "Ratán", "Bambú", "Acero", "MDF"]

BRANDS_DATA = ["IKEA", "Artisan", "Möbel", "Design Studio", "Furniture Plus", "Elite Homes", 
               "Luxury Design", "Modern Life", "Classic Comfort", "Premium Decor", "HomeCo", "Elegancia"]


def setup_base_data():
    """Configura categorías, marcas y materiales"""
    
    # Categorías
    categories_dict = {}
    for template in PRODUCT_TEMPLATES:
        cat, created = Category.objects.get_or_create(
            name=template["category"],
            defaults={'description': f'Categoría {template["category"]}', 'is_active': True}
        )
        categories_dict[template["category"]] = cat
        if created:
            print(f"  ✓ Categoría creada: {template['category']}")
    
    # Marcas
    brands_dict = {}
    for brand_name in BRANDS_DATA:
        brand, created = Brand.objects.get_or_create(
            name=brand_name,
            defaults={'description': f'Marca {brand_name}', 'is_active': True}
        )
        brands_dict[brand_name] = brand
        if created:
            print(f"  ✓ Marca creada: {brand_name}")
    
    # Materiales
    materials_dict = {}
    for material_name in MATERIALS_DATA:
        material, created = Material.objects.get_or_create(name=material_name)
        materials_dict[material_name] = material
        if created:
            print(f"  ✓ Material creado: {material_name}")
    
    return categories_dict, brands_dict, materials_dict


def generate_sku():
    """Genera un SKU único"""
    while True:
        sku = f"SKU-{random.randint(100000, 999999)}"
        if not Product.objects.filter(sku=sku).exists():
            return sku


def create_bulk_products(count=100):
    """Crea productos en lotes usando bulk_create para mejor rendimiento"""
    
    print("\n🔄 Preparando datos base...")
    categories_dict, brands_dict, materials_dict = setup_base_data()
    
    print(f"\n📦 Generando {count} productos...")
    
    products_to_create = []
    
    for i in range(count):
        # Seleccionar template aleatorio
        template = random.choice(PRODUCT_TEMPLATES)
        category = categories_dict[template["category"]]
        product_name = random.choice(template["names"])
        
        # Generar datos
        price = Decimal(random.uniform(50, 5000)).quantize(Decimal('0.01'))
        has_discount = random.random() < 0.4  # 40% de descuento
        discount_price = None
        
        if has_discount:
            discount_pct = random.choice([10, 15, 20, 25, 30])
            discount_price = (price * Decimal(1 - discount_pct / 100)).quantize(Decimal('0.01'))
        
        # Crear instancia de producto
        product = Product(
            name=f"{product_name} - {fake.word().title()} {i+1}",
            sku=generate_sku(),
            description=fake.text(max_nb_chars=200),
            category=category,
            brand=random.choice(list(brands_dict.values())),
            price=price,
            discount_price=discount_price,
            stock=random.randint(0, 150),
            min_stock=5,
            width=Decimal(random.uniform(30, 300)).quantize(Decimal('0.01')),
            height=Decimal(random.uniform(30, 300)).quantize(Decimal('0.01')),
            depth=Decimal(random.uniform(20, 200)).quantize(Decimal('0.01')),
            weight=Decimal(random.uniform(1, 100)).quantize(Decimal('0.01')),
            color=random.choice(COLORS),
            warranty_months=random.choice([12, 24, 36, 60]),
            assembly_required=random.choice([True, False]),
            assembly_time_minutes=random.randint(15, 240) if random.choice([True, False]) else None,
            is_featured=random.random() < 0.25,  # 25% destacados
            is_active=True,
            is_new=random.random() < 0.33,  # 33% nuevos
        )
        products_to_create.append(product)
    
    # Crear todos los productos de una vez
    print(f"  ⏳ Creando {len(products_to_create)} productos en lote...")
    created_products = Product.objects.bulk_create(products_to_create, batch_size=50)
    
    print(f"  ✅ {len(created_products)} productos creados exitosamente")
    
    # Ahora agregar relaciones many-to-many
    print(f"  ⏳ Asignando materiales a productos...")
    for product in created_products:
        selected_materials = random.sample(list(materials_dict.values()), k=random.randint(1, 4))
        product.materials.set(selected_materials)
    
    print(f"\n✨ ¡Proceso completado!")
    print(f"📊 Total de productos en BD: {Product.objects.count()}")
    print(f"🏷️  Productos con descuento: {Product.objects.filter(discount_price__isnull=False).count()}")
    print(f"⭐ Productos destacados: {Product.objects.filter(is_featured=True).count()}")
    print(f"🆕 Productos nuevos: {Product.objects.filter(is_new=True).count()}")


if __name__ == '__main__':
    try:
        create_bulk_products(100)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
