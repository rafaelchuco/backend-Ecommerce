#!/bin/bash
# Script para agregar 100 productos vía API HTTP
# Requisitos: curl, jq
# Uso: bash add_products_via_api.sh

# Configuración
API_URL="http://localhost:8000/api/products/products/"
TOKEN="your-admin-token-here"  # Reemplazar con token real
NUM_PRODUCTS=100

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Arrays de datos
PRODUCT_NAMES=("Sofá de Cuero" "Silla Ergonómica" "Mesa de Centro" "Escritorio" "Estantería" 
               "Lámpara LED" "Espejo Decorativo" "Tapete Persa" "Almohada" "Cortina"
               "Armario" "Cama King" "Mesita de Noche" "Comedor" "Reposapié")

CATEGORIES=("Muebles de Sala" "Muebles de Comedor" "Muebles de Dormitorio" "Muebles de Oficina" "Accesorios")

COLORS=("Negro" "Blanco" "Gris" "Marrón" "Beige" "Azul" "Verde" "Rojo")

MATERIALS=("Cuero" "Tela" "Madera" "Metal" "Vidrio")

# Función para generar SKU único
generate_sku() {
    echo "SKU-$(od -An -N4 -tu4 /dev/urandom | tr -d ' ' | cut -c1-6)"
}

# Función para generar datos de producto
generate_product() {
    local index=$1
    local name="${PRODUCT_NAMES[$((RANDOM % ${#PRODUCT_NAMES[@]}))]}"
    local category="${CATEGORIES[$((RANDOM % ${#CATEGORIES[@]}))]}"
    local color="${COLORS[$((RANDOM % ${#COLORS[@]}))]}"
    local material="${MATERIALS[$((RANDOM % ${#MATERIALS[@]}))]}"
    local price=$((RANDOM % 4950 + 50))
    local stock=$((RANDOM % 150))
    local has_discount=$((RANDOM % 10))
    
    # Crear JSON del producto
    cat <<EOF
{
    "name": "$name - $index",
    "sku": "$(generate_sku)",
    "description": "Producto de alta calidad con características premium. Descripción del artículo $index.",
    "category": "$category",
    "brand": "Premium Decor",
    "price": "$price.99",
    "discount_price": $([ $has_discount -lt 4 ] && echo "$((price * 75 / 100)).99" || echo "null"),
    "stock": $stock,
    "min_stock": 5,
    "width": 100.00,
    "height": 150.00,
    "depth": 80.00,
    "weight": 25.50,
    "color": "$color",
    "warranty_months": 12,
    "assembly_required": false
}
EOF
}

echo -e "${YELLOW}🚀 Iniciando creación de $NUM_PRODUCTS productos...${NC}"
echo -e "${YELLOW}📍 API: $API_URL${NC}\n"

created=0
failed=0

for ((i=1; i<=NUM_PRODUCTS; i++)); do
    # Generar datos del producto
    product_json=$(generate_product $i)
    
    # Enviar request
    response=$(curl -s -X POST "$API_URL" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$product_json")
    
    # Verificar respuesta
    if echo "$response" | grep -q '"id"'; then
        ((created++))
        echo -e "${GREEN}✓${NC} Producto $i/$NUM_PRODUCTS creado"
    else
        ((failed++))
        echo -e "${RED}✗${NC} Error al crear producto $i/$NUM_PRODUCTS"
        echo "   Respuesta: $(echo $response | head -c 100)..."
    fi
    
    # Mostrar progreso cada 10 productos
    if [ $((i % 10)) -eq 0 ]; then
        echo -e "${YELLOW}  Progreso: $i/$NUM_PRODUCTS${NC}"
    fi
done

echo -e "\n${YELLOW}=== RESUMEN ===${NC}"
echo -e "${GREEN}✅ Creados: $created${NC}"
echo -e "${RED}❌ Fallidos: $failed${NC}"
echo -e "${YELLOW}📊 Total: $NUM_PRODUCTS${NC}"
