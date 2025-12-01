"""
Script de validación - Verifica que los scripts se pueden ejecutar
Ejecución: python manage.py shell < validar_scripts.py
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from applications.products.models import Product, Category, Brand, Material

def print_section(title):
    """Imprime un encabezado de sección"""
    print("\n" + "="*60)
    print(f"✓ {title}")
    print("="*60)

def print_error(message):
    """Imprime un mensaje de error"""
    print(f"  ❌ {message}")

def print_success(message):
    """Imprime un mensaje de éxito"""
    print(f"  ✅ {message}")

def validate_models():
    """Valida que los modelos están disponibles"""
    print_section("VALIDANDO MODELOS")
    
    try:
        Product.objects.count()
        print_success("Modelo Product accesible")
    except Exception as e:
        print_error(f"Modelo Product: {str(e)}")
        return False
    
    try:
        Category.objects.count()
        print_success("Modelo Category accesible")
    except Exception as e:
        print_error(f"Modelo Category: {str(e)}")
        return False
    
    try:
        Brand.objects.count()
        print_success("Modelo Brand accesible")
    except Exception as e:
        print_error(f"Modelo Brand: {str(e)}")
        return False
    
    try:
        Material.objects.count()
        print_success("Modelo Material accesible")
    except Exception as e:
        print_error(f"Modelo Material: {str(e)}")
        return False
    
    return True

def check_current_products():
    """Muestra información de productos actuales"""
    print_section("ESTADO ACTUAL DE LA BD")
    
    total_products = Product.objects.count()
    total_categories = Category.objects.count()
    total_brands = Brand.objects.count()
    total_materials = Material.objects.count()
    
    print(f"  📦 Productos: {total_products}")
    print(f"  📂 Categorías: {total_categories}")
    print(f"  🏷️  Marcas: {total_brands}")
    print(f"  🔨 Materiales: {total_materials}")
    
    if total_products > 0:
        avg_price = Product.objects.aggregate(
            avg=django.db.models.Avg('price')
        )['avg']
        print(f"\n  💰 Precio promedio: ${avg_price:.2f}")
        
        with_discount = Product.objects.filter(
            discount_price__isnull=False
        ).count()
        print(f"  🏷️  Con descuento: {with_discount}")
        
        featured = Product.objects.filter(is_featured=True).count()
        print(f"  ⭐ Destacados: {featured}")
        
        new_products = Product.objects.filter(is_new=True).count()
        print(f"  🆕 Nuevos: {new_products}")
    
    return total_products

def check_django_setup():
    """Verifica la configuración de Django"""
    print_section("CONFIGURACIÓN DE DJANGO")
    
    try:
        from django.conf import settings
        print_success(f"Base de datos: {settings.DATABASES['default']['ENGINE']}")
        print_success(f"Aplicaciones instaladas: {len(settings.INSTALLED_APPS)} apps")
        
        # Verificar que nuestras apps están instaladas
        if 'applications.products' in settings.INSTALLED_APPS:
            print_success("Aplicación 'products' instalada")
        else:
            print_error("Aplicación 'products' NO está instalada")
            return False
        
        return True
    except Exception as e:
        print_error(f"Error en configuración: {str(e)}")
        return False

def check_file_structure():
    """Verifica la estructura de archivos"""
    print_section("ESTRUCTURA DE ARCHIVOS")
    
    base_path = "/home/dev/ecomerce/Ecommerce-BackEnd/backend"
    files_to_check = [
        "add_products.py",
        "add_products_via_api.py",
        "script_interactivo_productos.py",
        "add_products_via_api.sh",
        "SCRIPTS_PRODUCTOS.md",
        "README_SCRIPTS.md",
        "ENDPOINTS_REFERENCIA.md",
        "EJEMPLOS_JSON.md",
        "INICIO_RAPIDO.md",
        "INDICE.md",
    ]
    
    all_exist = True
    for filename in files_to_check:
        filepath = os.path.join(base_path, filename)
        if os.path.exists(filepath):
            print_success(f"Existe: {filename}")
        else:
            print_error(f"Falta: {filename}")
            all_exist = False
    
    return all_exist

def test_product_creation():
    """Prueba crear un producto simple"""
    print_section("TEST DE CREACIÓN")
    
    try:
        # Obtener o crear categoría
        category, _ = Category.objects.get_or_create(
            name="Test Category",
            defaults={"description": "Categoría de prueba"}
        )
        
        # Crear producto
        test_product = Product.objects.create(
            name="Producto Test",
            sku=f"TEST-{Product.objects.count()}",
            description="Producto de prueba para validar scripts",
            category=category,
            price=100.00,
            stock=5
        )
        
        print_success(f"Producto creado: {test_product.name}")
        print_success(f"Nombre normalizado (slug): {test_product.slug}")
        
        # Limpiar
        test_product.delete()
        print_success("Producto eliminado (limpieza)")
        
        return True
    except Exception as e:
        print_error(f"Error al crear producto: {str(e)}")
        return False

def show_next_steps():
    """Muestra los próximos pasos"""
    print_section("PRÓXIMOS PASOS")
    
    print("""
1. Si TODO está ✅:
   → Ejecuta: python manage.py shell < add_products.py
   
2. Si hay ❌ errores:
   → Revisa SCRIPTS_PRODUCTOS.md sección "Troubleshooting"
   
3. Para verificar después:
   → Abre shell: python manage.py shell
   → Ejecuta: from applications.products.models import Product
   → Cuenta: Product.objects.count()
   
4. Para explorar la API:
   → Inicia servidor: python manage.py runserver
   → Abre: http://localhost:8000/api/products/products/
   """)

def main():
    """Función principal"""
    print("\n" + "🔍 "*20)
    print("     VALIDACIÓN DE SCRIPTS DE PRODUCTOS")
    print("🔍 "*20)
    
    all_ok = True
    
    # Validar modelos
    if not validate_models():
        all_ok = False
    
    # Verificar Django
    if not check_django_setup():
        all_ok = False
    
    # Verificar archivos
    if not check_file_structure():
        all_ok = False
    
    # Verificar estado actual
    current_products = check_current_products()
    
    # Test de creación
    if not test_product_creation():
        all_ok = False
    
    # Resumen final
    print_section("RESUMEN")
    
    if all_ok and current_products == 0:
        print_success("✨ TODO ESTÁ LISTO - BD vacía, puedes ejecutar los scripts")
        print("\n🚀 Comando recomendado:")
        print("   python manage.py shell < add_products.py")
    elif all_ok:
        print_success("✨ TODO FUNCIONA CORRECTAMENTE")
        print(f"\n📊 Base de datos tiene {current_products} productos")
        print("\n📝 Para agregar más productos:")
        print("   python manage.py shell < add_products.py")
        print("\n🧹 Para limpiar antes:")
        print("   python manage.py shell")
        print("   >>> from applications.products.models import Product")
        print("   >>> Product.objects.all().delete()")
    else:
        print_error("❌ Hay problemas - Revisa los errores arriba")
        sys.exit(1)
    
    show_next_steps()
    
    print("\n" + "="*60)
    print("✓ Validación completada")
    print("="*60 + "\n")

if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error fatal: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
