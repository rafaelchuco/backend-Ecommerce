#!/bin/bash
# Deploy a Render - Comandos rápidos

echo "🚀 Preparando para deploy en Render..."
echo ""

# 1. Verificar estado de git
echo "📋 Estado del repositorio:"
git status
echo ""

# 2. Agregar todos los cambios
echo "📝 Agregando cambios..."
git add .
echo ""

# 3. Commit
echo "💾 Commitiendo cambios..."
git commit -m "Preparar backend para Render - Django + Gunicorn"
echo ""

# 4. Push
echo "🔼 Subiendo a GitHub..."
git push origin main
echo ""

echo "✅ ¡Listo! Ahora:"
echo "   1. Ir a https://render.com"
echo "   2. Nueva Web Service"
echo "   3. Conectar tu repositorio"
echo "   4. Seguir instrucciones de RENDER_DEPLOY.md"
echo ""
