#!/bin/bash
# Script de build para Render

# Instalar dependencias
pip install -r requirements.txt

# Recolectar archivos estáticos
python manage.py collectstatic --noinput

# Ejecutar migraciones
python manage.py migrate --noinput

echo "✅ Build completado"
