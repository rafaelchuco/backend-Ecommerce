# ❓ FAQ: Preguntas sobre Deploy en Render

## P: ¿Qué costo tiene Render?

**R:** Render tiene plan gratuito:
- ✅ Web Services (backend): $0/mes (sleep después 15 min inactividad)
- ✅ PostgreSQL: $7/mes (mínimo) o gratuito con limitaciones
- 💡 Para desarrollo/testing: Gratis total

Para producción (sin sleep): Desde $7/mes

---

## P: ¿Qué pasa cuando no hay tráfico?

**R:** En el plan gratuito:
- Tu servidor "duerme" después de 15 min sin solicitudes
- Primera solicitud tarda 1-2 segundos (wake up)
- Después funciona normal

Solución: Upgrade a plan pagado o mantén servicio "activo"

---

## P: ¿Necesito modificar mi código?

**R:** **NO**. Todo está configurado automáticamente:
- ✓ CORS dinámico (lee desde variables)
- ✓ Settings para producción (DEBUG=False)
- ✓ Migraciones automáticas (Procfile)
- ✓ Estáticos recolectados (Procfile)

Solo necesitas: **Variables de entorno en Render**

---

## P: ¿Cómo puedo probar localmente antes de subir?

**R:**
```bash
# Simular producción localmente
export DEBUG=False
export SECRET_KEY=test-secret-key-123
export ALLOWED_HOSTS=localhost,127.0.0.1
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py runserver
```

---

## P: ¿Cómo subo migraciones después de cambiar modelos?

**R:**
```bash
# En tu máquina (local)
python manage.py makemigrations
python manage.py migrate

# Commit y push a GitHub
git add .
git commit -m "Nueva migración"
git push origin main

# En Render: Se ejecuta automáticamente (Procfile)
```

---

## P: ¿Puedo usar SQLite en Render?

**R:** **NO es recomendable**. Render reinicia contenedores frecuentemente y perderías datos.

**Usa PostgreSQL** (Render lo proporciona)

---

## P: ¿Cómo conecto mi BD local a Render?

**R:** Usar un tunel SSH (no recomendado para producción):
```bash
# Tunnel local
ssh -L 5432:localhost:5432 user@render-machine

# Luego conectar localmente
psql postgresql://user:pass@localhost:5432/dbname
```

**Mejor**: Usa postgresql en Render (mismo pricing)

---

## P: ¿Cómo cambio variables de entorno después de deploy?

**R:**
1. Dashboard → Tu servicio → **"Environment"**
2. Edita variables
3. Click **"Save"** → Automático redeploy

---

## P: ¿Qué pasa si subo un `.env` real a GitHub?

**R:** **¡PROBLEMA!** Tus credenciales quedan públicas.

**Solución**:
```bash
# Borrar historio
git rm --cached .env
git commit -m "Remove .env"
git push

# Cambiar credenciales (IMPORTANTE)
# - Stripe: rotate keys
# - DB: cambiar contraseña
# - Secret key: generar nueva
```

---

## P: ¿Cómo mantengo sincronizado mi BD local con Render?

**R:** PostgreSQL permite backups:
```bash
# Backup desde Render
pg_dump postgresql://user:pass@host/dbname > backup.sql

# Restaurar localmente
psql -U user -d local_db < backup.sql
```

---

## P: ¿Puedo desplegar desde una rama que no sea main?

**R:** **SÍ**. En Render:
1. Environment → Seleccionar rama
2. Default es `main`, puedes cambiar a `develop`, `staging`, etc.

---

## P: ¿Qué monitoreo tiene Render?

**R:**
- 📊 Logs en tiempo real
- 📈 CPU/Memoria usage
- 🔔 Health checks
- 📬 Notificaciones por email

Dashboard → Servicio → **"Logs"** y **"Analytics"**

---

## P: ¿Cómo configuro dominio propio?

**R:**
1. Comprar dominio (GoDaddy, Namecheap, etc.)
2. En Render: **"Custom domain"** → ingresa `tu-dominio.com`
3. Copiar DNS records
4. En proveedor del dominio: agregar registros DNS
5. ✅ Esperar propagación (15 min - 24h)

---

## P: ¿Cómo hago redeploy sin cambios?

**R:**
1. Dashboard → Tu servicio
2. Click **"Manual Deploy"** → **"Deploy"**

O desde CLI:
```bash
git commit --allow-empty -m "Trigger redeploy"
git push
```

---

## P: ¿Qué pasa si hace error en migraciones?

**R:**
1. El deploy falla
2. Revisa logs (Dashboard → Logs)
3. Soluciona localmente:
   ```bash
   python manage.py migrate --fake-initial
   # O rollback manual
   ```
4. Commit y push nuevamente

---

## P: ¿Puedo usar Redis/Celery en Render?

**R:** **SÍ** pero en plan pagado. Opciones:
- Redis en Render ($7/mes)
- Redis Cloud (gratuito con limitaciones)
- AWS ElastiCache

---

## P: ¿Cómo reviso si mi API funciona?

**R:**
```bash
# Después de deploy
curl https://tu-app.onrender.com/api/products/

# Con autenticación
curl -H "Authorization: Bearer TOKEN" \
  https://tu-app.onrender.com/api/admin/
```

O usa Postman/Insomnia.

---

## P: ¿Cómo escalo si tengo mucho tráfico?

**R:** Render escalada automática (plan pagado):
- Aumenta recursos (CPU/RAM)
- Múltiples instancias
- Load balancer incluido

---

## P: ¿Puedo deployar sin GitHub?

**R:** Render requiere Git + repo (GitHub, GitLab, Bitbucket).

Si no tienes: Crea repo público/privado en GitHub.

---

## 🆘 ¿Problemas durante deploy?

1. **Error en logs**: Revisa `Dashboard → Logs`
2. **Problema de DB**: Verifica credenciales de PostgreSQL
3. **Import error**: Falta dependencia en `requirements.txt`
4. **CORS error**: Falta URL en `CORS_ORIGINS`

**Si no te funciona**: Revisa `RENDER_DEPLOY.md` o contacta soporte Render.

---

¿Preguntas? Revisa la documentación completa 📖
