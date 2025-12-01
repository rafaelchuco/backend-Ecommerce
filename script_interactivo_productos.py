#!/usr/bin/env python
"""
Script interactivo para agregar productos
Uso: python manage.py shell < script_interactivo_productos.py
"""
import os
import django
from decimal import Decimal
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from applications.products.models import Product, Category, Brand, Material

class ProductCreator:
    """Clase para crear productos de forma interactiva"""
    
    PRODUCT_TEMPLATES = {
        "Sofá de Cuero": {
            "price_range": (800, 3000),
            "category": "Muebles de Sala",
            "width": 200,
            "height": 90,
            "depth": 100,
            "weight": 50,
        },
        "Silla Ergonómica": {
            "price_range": (150, 500),
            "category": "Muebles de Oficina",
            "width": 65,
            "height": 120,
            "depth": 70,
            "weight": 15,
        },
        "Mesa de Centro": {
            "price_range": (200, 800),
            "category": "Muebles de Sala",
            "width": 120,
            "height": 45,
            "depth": 80,
            "weight": 25,
        },
        "Cama King": {
            "price_range": (1000, 4000),
            "category": "Muebles de Dormitorio",
            "width": 180,
            "height": 50,
            "depth": 210,
            "weight": 80,
        },
        "Escritorio": {
            "price_range": (300, 1200),
            "category": "Muebles de Oficina",
            "width": 160,
            "height": 75,
            "depth": 80,
            "weight": 35,
        },
        "Estantería": {
            "price_range": (100, 600),
            "category": "Muebles de Sala",
            "width": 100,
            "height": 200,
            "depth": 40,
            "weight": 20,
        },
        "Lámpara LED": {
            "price_range": (30, 200),
            "category": "Accesorios y Decoración",
            "width": 30,
            "height": 60,
            "depth": 30,
            "weight": 2,
        },
        "Espejo Decorativo": {
            "price_range": (50, 400),
            "category": "Accesorios y Decoración",
            "width": 80,
            "height": 120,
            "depth": 5,
            "weight": 5,
        },
        "Cortina Blackout": {
            "price_range": (40, 150),
            "category": "Accesorios y Decoración",
            "width": 150,
            "height": 250,
            "depth": 1,
            "weight": 1,
        },
        "Comedor para 6": {
            "price_range": (500, 2000),
            "category": "Muebles de Comedor",
            "width": 180,
            "height": 75,
            "depth": 100,
            "weight": 60,
        },
    }
    
    COLORS = ["Negro", "Blanco", "Gris", "Marrón", "Beige", "Azul", "Verde", "Rojo", "Champagne", "Oro"]
    
    def __init__(self):
        self.setup_base_data()
    
    def setup_base_data(self):
        """Configura datos base"""
        print("\n" + "="*60)
        print("🔄 CONFIGURANDO DATOS BASE")
        print("="*60)
        
        # Categorías
        self.categories = {}
        categories_list = [
            "Muebles de Sala",
            "Muebles de Comedor",
            "Muebles de Dormitorio",
            "Muebles de Oficina",
            "Accesorios y Decoración"
        ]
        
        for cat_name in categories_list:
            cat, created = Category.objects.get_or_create(
                name=cat_name,
                defaults={"description": f"Categoría de {cat_name}", "is_active": True}
            )
            self.categories[cat_name] = cat
            status = "✓ Creada" if created else "✓ Existe"
            print(f"  {status}: {cat_name}")
        
        # Marcas
        self.brands = {}
        brands_list = [
            "Premium Decor", "Design Studio", "Furniture Plus",
            "Elite Homes", "Modern Life", "Luxury Design"
        ]
        
        for brand_name in brands_list:
            brand, created = Brand.objects.get_or_create(
                name=brand_name,
                defaults={"description": f"Marca {brand_name}", "is_active": True}
            )
            self.brands[brand_name] = brand
            status = "✓ Creada" if created else "✓ Existe"
            print(f"  {status}: {brand_name}")
        
        # Materiales
        self.materials = {}
        materials_list = ["Cuero", "Tela", "Madera", "Metal", "Vidrio", "Plástico"]
        
        for material_name in materials_list:
            material, created = Material.objects.get_or_create(name=material_name)
            self.materials[material_name] = material
            status = "✓ Creado" if created else "✓ Existe"
            print(f"  {status}: {material_name}")
        
        print()
    
    def generate_sku(self):
        """Genera un SKU único"""
        while True:
            sku = f"SKU-{random.randint(100000, 999999)}"
            if not Product.objects.filter(sku=sku).exists():
                return sku
    
    def create_product_batch(self, count=100):
        """Crea un lote de productos"""
        print("\n" + "="*60)
        print(f"📦 CREANDO {count} PRODUCTOS")
        print("="*60 + "\n")
        
        created_count = 0
        failed_count = 0
        
        for i in range(count):
            try:
                # Seleccionar template
                template_name = random.choice(list(self.PRODUCT_TEMPLATES.keys()))
                template = self.PRODUCT_TEMPLATES[template_name]
                
                # Generar precio
                min_price, max_price = template["price_range"]
                price = Decimal(random.uniform(min_price, max_price)).quantize(Decimal('0.01'))
                
                # Descuento (40% de probabilidad)
                discount_price = None
                if random.random() < 0.4:
                    discount_pct = random.choice([10, 15, 20, 25, 30])
                    discount_price = (price * Decimal(1 - discount_pct / 100)).quantize(Decimal('0.01'))
                
                # Crear producto
                product = Product.objects.create(
                    name=f"{template_name} - {random.choice(self.COLORS)} {i+1}",
                    sku=self.generate_sku(),
                    description=f"Producto de alta calidad y diseño premium. {template_name} en perfecto estado.",
                    category=self.categories[template["category"]],
                    brand=random.choice(list(self.brands.values())),
                    price=price,
                    discount_price=discount_price,
                    stock=random.randint(0, 150),
                    min_stock=5,
                    width=Decimal(template["width"]),
                    height=Decimal(template["height"]),
                    depth=Decimal(template["depth"]),
                    weight=Decimal(template["weight"]),
                    color=random.choice(self.COLORS),
                    warranty_months=random.choice([12, 24, 36]),
                    assembly_required=random.choice([True, False]),
                    assembly_time_minutes=random.randint(15, 240) if random.choice([True, False]) else None,
                    is_featured=random.random() < 0.25,
                    is_active=True,
                    is_new=random.random() < 0.33,
                )
                
                # Agregar materiales
                selected_materials = random.sample(
                    list(self.materials.values()),
                    k=random.randint(1, 3)
                )
                product.materials.set(selected_materials)
                
                created_count += 1
                
                # Mostrar progreso
                if (i + 1) % 10 == 0:
                    print(f"  ✓ {i+1}/{count} productos creados...")
                
            except Exception as e:
                failed_count += 1
                print(f"  ✗ Error en producto {i+1}: {str(e)}")
        
        # Resumen
        print("\n" + "="*60)
        print("📊 RESUMEN")
        print("="*60)
        print(f"✅ Productos creados:    {created_count}")
        print(f"❌ Errores:              {failed_count}")
        print(f"📈 Total en BD:          {Product.objects.count()}")
        
        # Estadísticas
        print(f"\n🏷️  Con descuento:        {Product.objects.filter(discount_price__isnull=False).count()}")
        print(f"⭐ Destacados:           {Product.objects.filter(is_featured=True).count()}")
        print(f"🆕 Nuevos:              {Product.objects.filter(is_new=True).count()}")
        
        # Por categoría
        print(f"\n📂 Por categoría:")
        for cat in self.categories.values():
            count = Product.objects.filter(category=cat).count()
            print(f"   • {cat.name}: {count} productos")
        
        print("\n✨ ¡Proceso completado!\n")
    
    def show_menu(self):
        """Muestra menú interactivo"""
        print("\n" + "="*60)
        print("🛋️  GENERADOR DE PRODUCTOS")
        print("="*60)
        print("\n¿Cuántos productos deseas crear?")
        print("  1. 10 productos")
        print("  2. 50 productos")
        print("  3. 100 productos (recomendado)")
        print("  4. Cantidad personalizada")
        print("  5. Salir")
        
        choice = input("\nOpción (1-5): ").strip()
        
        if choice == "1":
            self.create_product_batch(10)
            self.show_menu()
        elif choice == "2":
            self.create_product_batch(50)
            self.show_menu()
        elif choice == "3":
            self.create_product_batch(100)
            self.show_menu()
        elif choice == "4":
            try:
                num = int(input("Cantidad de productos: ").strip())
                if num > 0:
                    self.create_product_batch(num)
                else:
                    print("❌ Cantidad inválida")
                self.show_menu()
            except ValueError:
                print("❌ Cantidad inválida")
                self.show_menu()
        elif choice == "5":
            print("\n👋 ¡Hasta luego!\n")
            return
        else:
            print("❌ Opción no válida")
            self.show_menu()


if __name__ == '__main__':
    try:
        creator = ProductCreator()
        creator.show_menu()
    except KeyboardInterrupt:
        print("\n\n👋 Programa interrumpido por el usuario\n")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
