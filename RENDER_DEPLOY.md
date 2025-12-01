# 🚀 Guía: Desplegar Backend Django en Render

## ✅ Lo que ya está preparado

✓ `Procfile` - Configuración para Render  
✓ `requirements.txt` - Con gunicorn incluido  
✓ `settings.py` - Configurado para CORS y variables de entorno  

---

## 📋 Paso a paso

### 1️⃣ Subir a GitHub

```bash
git add .
git commit -m "Preparar para Render"
git push origin main
```

### 2️⃣ Crear cuenta en Render

👉 [https://render.com](https://render.com)

### 3️⃣ Conectar repo y crear Web Service

1. Click en **"New"** → **"Web Service"**
2. Selecciona tu repo `Ecommerce-BackEnd`
3. Configura:
   - **Name**: `ecommerce-backend` (o el que prefieras)
   - **Language**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn backend.wsgi`

### 4️⃣ Configurar Variables de Entorno

En Render, ve a **"Environment"** y agrega:

```
DEBUG=False
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=your-render-url.onrender.com
DB_ENGINE=postgresql
DB_NAME=your_db_name
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=your_db_host.render.com
DB_PORT=5432
CORS_ALLOWED_ORIGINS=https://tu-frontend-url.vercel.app,https://tu-frontend-url.netlify.app
```

### 5️⃣ Base de datos (PostgreSQL)

**Opción A: Usar PostgreSQL de Render**
- En Render, crea una nueva instancia PostgreSQL
- Copia las credenciales a las variables de entorno

**Opción B: Conectar PostgreSQL externa**
- Si tienes una BD existente, agrega las credenciales

### 6️⃣ Configurar CORS en settings.py

Ya está configurado en `backend/settings.py`:

```python
CORS_ALLOWED_ORIGINS = [
    "https://tu-frontend.vercel.app",
    "https://tu-frontend.netlify.app",
]
```

### 7️⃣ Deploy

Una vez configurado todo, Render automáticamente:
1. ✓ Clona tu repo
2. ✓ Instala dependencias (`pip install -r requirements.txt`)
3. ✓ Ejecuta migraciones (agregar en `Procfile` si es necesario)
4. ✓ Inicia el servidor con gunicorn

---

## 🔗 URLs importantes

- **Backend API**: `https://tu-render-url.onrender.com/api/products/`
- **Swagger Docs**: `https://tu-render-url.onrender.com/swagger/`
- **Admin**: `https://tu-render-url.onrender.com/admin/`

---

## ⚠️ Notas importantes

1. **Base de datos**: Render solo da almacenamiento **gratuito limitado**. Para producción, usa una BD externa.

2. **Migraciones**: Si necesitas ejecutar migraciones antes del deploy:
   ```
   python manage.py migrate
   ```
   Agrégalo al `Procfile` antes de gunicorn.

3. **Archivos estáticos**: Render necesita que hagas:
   ```bash
   python manage.py collectstatic --noinput
   ```
   Esto está en `settings.py` configurado con `STATIC_ROOT`.

4. **Variables de entorno**: **NO commitees** el `.env` con credenciales reales.

---

## 🛠️ Troubleshooting

**Error: "ModuleNotFoundError"**
- Verifica que `requirements.txt` tiene todas las dependencias
- Ejecuta: `pip install -r requirements.txt` localmente

**Error: "Database connection failed"**
- Verifica las credenciales de DB
- Revisa que PostgreSQL está accesible desde Render

**Error: "ALLOWED_HOSTS"**
- Agrega tu URL de Render: `https://tu-backend.onrender.com`

---

## ✔️ Comandos útiles después del deploy

```bash
# Ver logs en Render
# (Desde dashboard → tu servicio → "Logs")

# Ejecutar migraciones en producción
# (Crear un "One-Off" job en Render)
```

¡Listo para desplegar! 🚀
