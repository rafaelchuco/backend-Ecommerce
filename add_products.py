"""
Script para agregar 100 productos de prueba a la base de datos
Ejecución: python manage.py shell < add_products.py
"""
import os
import django
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from applications.products.models import Product, Category, Brand, Material

# Datos de prueba
PRODUCT_NAMES = [
    "Sofá de Cuero Premium", "Silla Ergonómica", "Mesa de Centro", "Escritorio Moderno",
    "Estantería Flotante", "Lámpara LED", "Espejo Decorativo", "Tapete Persa",
    "Almohada Ortopédica", "Cortina Blackout", "Armario Empotrado", "Cama King Size",
    "Mesita de Noche", "Comedor para 6", "Reposapié", "Estante Industrial",
    "Cajonera de Madera", "Cómoda Vintage", "Zapatero Moderno", "Baúl Decorativo",
    "Silla de Oficina", "Escritorio Standing", "Estantería Metálica", "Perchero de Pared",
    "Sinfonier Clásico", "Banco de Cocina", "Taburete Bar", "Silla Gaming",
    "Puerta Corredera", "Moldura Decorativa", "Panel Acústico", "Estante Colgante",
    "Repisa Flotante", "Vitrina de Cristal", "Espejo de Pared", "Cuadro Decorativo",
    "Lámpara de Pie", "Candelabro Moderno", "Aplique de Pared", "Lámpara de Escritorio",
    "Cesto Organizador", "Caja de Almacenaje", "Organizador de Gaveta", "Perchero Plegable",
    "Marco Flotante", "Soporte de TV", "Estante Giratorio", "Puerta Espejo",
    "Tablero Pegboard", "Clave de Pared", "Gancho Decorativo", "Repisa Esquinera",
    "Espejos Hexagonales", "Panel 3D", "Estante Asimétrico", "Closet Modular",
    "Divisor de Espacios", "Biombo Plegable", "Puerta Plegable", "Cortina Corrediza",
    "Persiana Enrollable", "Estor Vertical", "Doble Cortina", "Cenefa Decorativa",
    "Mantel de Tela", "Runner de Pasillo", "Felpudo Entrada", "Alfombra Geométrica",
    "Tejido de Lino", "Cortina Sheer", "Velo Translúcido", "Tela Laminada",
    "Piel Sintética", "Tela de Algodón", "Terciopelo Premium", "Brocado Dorado",
    "Encaje Blanco", "Jacquard", "Microsueda", "Cuerda Natural",
    "Ratán Tejido", "Bambú Laminado", "Caoba Maciza", "Roble Blanco",
    "Nogal Americano", "Fresno Natural", "Pino Macizo", "Arce Canadiense",
    "Cerezo Oscuro", "Teca Asiática", "Ebonita Negra", "Nogal Claro"
]

COLORS = ["Negro", "Blanco", "Gris", "Marrón", "Beige", "Azul", "Verde", "Rojo", "Champagne", "Oro"]

MATERIALS_DATA = ["Cuero", "Tela", "Madera", "Metal", "Vidrio", "Plástico", "Ratán", "Bambú"]

BRANDS_DATA = ["IKEA", "Artisan", "Möbel", "Design Studio", "Furniture Plus", "Elite Homes", 
               "Luxury Design", "Modern Life", "Classic Comfort", "Premium Decor"]

def get_or_create_test_data():
    """Crea o obtiene datos básicos para los productos"""
    
    # Crear categorías si no existen
    categories = []
    category_names = [
        "Muebles de Sala",
        "Muebles de Comedor",
        "Muebles de Dormitorio",
        "Muebles de Oficina",
        "Accesorios y Decoración"
    ]
    
    for name in category_names:
        cat, created = Category.objects.get_or_create(
            name=name,
            defaults={'description': f'Categoría de {name}'}
        )
        categories.append(cat)
    
    # Crear marcas si no existen
    brands = []
    for brand_name in BRANDS_DATA:
        brand, created = Brand.objects.get_or_create(
            name=brand_name,
            defaults={'description': f'Marca {brand_name}'}
        )
        brands.append(brand)
    
    # Crear materiales si no existen
    materials = []
    for material_name in MATERIALS_DATA:
        material, created = Material.objects.get_or_create(name=material_name)
        materials.append(material)
    
    return categories, brands, materials


def create_products(count=100):
    """Crea 'count' productos de prueba"""
    
    print("🔄 Obteniendo o creando datos base...")
    categories, brands, materials = get_or_create_test_data()
    
    print(f"✅ Categorías: {len(categories)}")
    print(f"✅ Marcas: {len(brands)}")
    print(f"✅ Materiales: {len(materials)}")
    
    print(f"\n🚀 Creando {count} productos...")
    
    products_created = 0
    
    for i in range(count):
        # Generar datos únicos
        product_name = random.choice(PRODUCT_NAMES)
        sku = f"SKU-{random.randint(100000, 999999)}"
        
        # Verificar que el SKU no exista
        while Product.objects.filter(sku=sku).exists():
            sku = f"SKU-{random.randint(100000, 999999)}"
        
        # Datos del producto
        price = Decimal(random.uniform(50, 5000)).quantize(Decimal('0.01'))
        has_discount = random.choice([True, False])
        discount_price = None
        
        if has_discount:
            discount_percentage = random.choice([10, 15, 20, 25, 30])
            discount_price = (price * Decimal(1 - discount_percentage / 100)).quantize(Decimal('0.01'))
        
        # Crear producto
        try:
            product = Product.objects.create(
                name=f"{product_name} {i+1}",
                sku=sku,
                description=f"Descripción del producto {i+1}. Producto de alta calidad con características premium.",
                category=random.choice(categories),
                brand=random.choice(brands),
                price=price,
                discount_price=discount_price,
                stock=random.randint(0, 100),
                min_stock=5,
                width=Decimal(random.uniform(30, 300)).quantize(Decimal('0.01')),
                height=Decimal(random.uniform(30, 300)).quantize(Decimal('0.01')),
                depth=Decimal(random.uniform(20, 200)).quantize(Decimal('0.01')),
                weight=Decimal(random.uniform(1, 100)).quantize(Decimal('0.01')),
                color=random.choice(COLORS),
                warranty_months=random.choice([12, 24, 36]),
                assembly_required=random.choice([True, False]),
                assembly_time_minutes=random.randint(15, 240) if random.choice([True, False]) else None,
                is_featured=random.choice([True, False, False, False]),  # 25% destacados
                is_active=True,
                is_new=random.choice([True, False, False]),  # 33% nuevos
            )
            
            # Agregar materiales aleatorios
            selected_materials = random.sample(materials, k=random.randint(1, 3))
            product.materials.set(selected_materials)
            
            products_created += 1
            
            if (i + 1) % 10 == 0:
                print(f"  ✓ {i + 1} productos creados...")
        
        except Exception as e:
            print(f"  ❌ Error al crear producto {i+1}: {str(e)}")
            continue
    
    print(f"\n✨ ¡Proceso completado!")
    print(f"✅ Total de productos creados: {products_created}/{count}")
    print(f"📊 Total de productos en BD: {Product.objects.count()}")


if __name__ == '__main__':
    # Ejecutar el script
    create_products(100)
