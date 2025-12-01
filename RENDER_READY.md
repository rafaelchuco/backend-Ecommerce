# ✅ BACKEND LISTO PARA RENDER

Todo está preparado para desplegar tu backend en Render. Aquí va el resumen:

---

## 📦 Archivos creados/actualizados

✅ **Procfile** - Configuración para Render (migraciones + gunicorn)  
✅ **requirements.txt** - Incluye `gunicorn`  
✅ **build.sh** - Script de build automático  
✅ **.env.example** - Variables de entorno necesarias  
✅ **RENDER_DEPLOY.md** - Guía completa paso a paso  
✅ **settings.py** - Configurado para CORS dinámico y producción  

---

## 🚀 Pasos rápidos para desplegar

### 1. Subir a GitHub
```bash
git add .
git commit -m "Preparar para Render"
git push origin main
```

### 2. En Render Dashboard

1. Click **"New"** → **"Web Service"**
2. Conecta tu repositorio
3. Configura:
   - **Name**: `ecommerce-backend`
   - **Language**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend.wsgi`

### 3. Variables de entorno

En **"Environment"**, agrega (copia desde `.env.example`):

```
DEBUG=False
SECRET_KEY=tu-clave-super-larga-y-segura
ALLOWED_HOSTS=tu-app.onrender.com
DB_ENGINE=postgresql
DB_NAME=tu_db
DB_USER=tu_user
DB_PASSWORD=tu_password
DB_HOST=tu-db-host.render.com
DB_PORT=5432
CORS_ORIGINS=https://tu-frontend.vercel.app
```

### 4. Base de datos

- Opción A: Crear PostgreSQL en Render (en el dashboard)
- Opción B: Conectar una BD externa (Atlas, RDS, etc.)

### 5. Deploy

¡Listo! Render automáticamente:
- ✓ Clona tu repo
- ✓ Instala dependencias
- ✓ Ejecuta migraciones (Procfile)
- ✓ Recolecta estáticos
- ✓ Inicia el servidor

---

## 🔗 URLs después del deploy

```
API:        https://tu-app.onrender.com/api/products/
Swagger:    https://tu-app.onrender.com/swagger/
Admin:      https://tu-app.onrender.com/admin/
```

---

## ⚠️ Cosas importantes

1. **SECRET_KEY**: Genera una nueva en Render, NO uses la del .env local
2. **DEBUG**: Siempre `False` en producción
3. **BD**: Render da almacenamiento limitado. Para producción usa BD externa
4. **CORS**: Configura las URLs de tu frontend
5. **Migraciones**: Se ejecutan automáticamente (Procfile)

---

## 📚 Ver logs en Render

Dashboard → Tu servicio → **"Logs"** tab

---

## ✔️ Checklist antes de pushear

- [ ] Subí a GitHub
- [ ] Creé variable SECRET_KEY en Render
- [ ] Configuré base de datos
- [ ] Agregué URLs de frontend en CORS_ORIGINS
- [ ] DEBUG=False en Render

---

¡Todo listo! 🎉 Ahora solo conecta tu repo y espera el deploy.

Cualquier duda, revisa `RENDER_DEPLOY.md` para más detalles.
