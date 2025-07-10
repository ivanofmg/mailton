# 🧾 Bitácora Técnica Complementaria – Control PM2 y Scripts del Backend Mailton

## 🗓️ Fecha: 2025-07-10 - 6:37 PM

---

## 🔍 Propósito

Documentar todos los scripts y comandos estandarizados para el control del backend FastAPI del proyecto *Mailton Kanazo Foot Wear* bajo gestión de procesos con **PM2**, incluyendo:

* Inicio y parada automatizada del backend
* Inicio, parada y monitoreo del gateway WhatsApp
* Registro persistente de logs
* Alias globales del sistema
* Convenciones de commits asociadas
* Control de versiones con tagging oficial (`v1.0.0`)

---

## 📚 Scripts operativos agregados

### 1. `start_backend_pm2.sh`

* Inicia el backend bajo PM2
* Activa entorno virtual y lanza `start.py`
* Borra instancia previa si existe
* Alias global sugerido: `startmailton`

```bash
sudo ln -s /opt/mailton/scripts/start_backend_pm2.sh /usr/local/bin/startmailton
```

---

### 2. `stop_backend_pm2.sh`

* Detiene el backend gestionado por PM2
* No elimina el proceso, permite reinicio posterior
* Alias global: `stopmailton`

```bash
sudo ln -s /opt/mailton/scripts/stop_backend_pm2.sh /usr/local/bin/stopmailton
```

---

### 3. `log_backend_pm2.sh`

* Crea (si no existe) y otorga permisos sobre `/var/log/mailton_backend.log`
* Inicia escritura persistente de logs en tiempo real usando `pm2 logs` con append
* Alias global: `logmailton`

```bash
sudo ln -s /opt/mailton/scripts/log_backend_pm2.sh /usr/local/bin/logmailton
```

---

### 4. `start_whatsapp_gateway.sh`

* Inicia el gateway WhatsApp vía `index.js`
* Borra instancia previa si existe
* Alias global: `startwhatsapp`

```bash
sudo ln -s /opt/mailton/scripts/start_whatsapp_gateway.sh /usr/local/bin/startwhatsapp
```

---

### 5. `stop_whatsapp_gateway.sh`

* Detiene el proceso `mailton-whatsapp` en PM2
* Alias global: `stopwhatsapp`

```bash
sudo ln -s /opt/mailton/scripts/stop_whatsapp_gateway.sh /usr/local/bin/stopwhatsapp
```

---

### 6. `log_whatsapp_gateway.sh`

* Monitorea los logs del gateway WhatsApp (`mailton-whatsapp`)
* Alias global: `logwhatsapp`

```bash
sudo ln -s /opt/mailton/scripts/log_whatsapp_gateway.sh /usr/local/bin/logwhatsapp
```

---

## 👍 Comandos clave PM2 para mantenimiento

| Acción                 | Comando                       |
| ---------------------- | ----------------------------- |
| Iniciar backend        | `startmailton`                |
| Detener backend        | `stopmailton`                 |
| Ver estado de procesos | `pm2 status`                  |
| Ver logs IA            | `logmailton`                  |
| Ver logs WhatsApp      | `logwhatsapp`                 |
| Iniciar WhatsApp       | `startwhatsapp`               |
| Detener WhatsApp       | `stopwhatsapp`                |
| Reiniciar backend      | `pm2 restart mailton-backend` |
| Eliminar backend       | `pm2 delete mailton-backend`  |

---

## 📅 Lecciones aprendidas

* ✅ PM2 permite control robusto, reinicio tras reboot y logs continuos del backend IA.
* ⚠️ Es necesario incluir `cd` al directorio correcto dentro de cada script.
* 🔐 Se recomienda no eliminar el proceso salvo que se necesite reinstanciar (`pm2 delete`).
* 📝 `logmailton` y `logwhatsapp` evitan dejar sesiones abiertas para seguimiento continuo.
* 📁 Los logs deben escribirse en rutas estándar (`/var/log`) para trazabilidad.
* 🔁 Toda acción estandarizada debe tener su commit, alias y bitácora.
* 💡 Separar backend y gateway permite reinicios independientes, mejora la trazabilidad y facilita la escalabilidad modular.
* 🔍 El archivo correcto para levantar el gateway WhatsApp es `index.js`, no `test.js`.
* 🧠 Las respuestas del agente IA y los mensajes entrantes desde WhatsApp deben ser visibles en tiempo real por consola o logs (`console.log()` o `logger.info()` en index.js).

---

## 🔄 Commits registrados

* `2025-07-10 16:22` → `chore ⚙️ agrega scripts PM2 para control completo del gateway WhatsApp (start, stop, log)`

---

## 📂 Archivos involucrados

* `/opt/mailton/scripts/start_backend_pm2.sh`
* `/opt/mailton/scripts/stop_backend_pm2.sh`
* `/opt/mailton/scripts/log_backend_pm2.sh`
* `/opt/mailton/scripts/start_whatsapp_gateway.sh`
* `/opt/mailton/scripts/stop_whatsapp_gateway.sh`
* `/opt/mailton/scripts/log_whatsapp_gateway.sh`
* `/var/log/mailton_backend.log`
* Alias creados: `startmailton`, `stopmailton`, `logmailton`, `startwhatsapp`, `stopwhatsapp`, `logwhatsapp`

---

## 🗺️ Próximo paso en el roadmap del proyecto

### 🔹 Nueva fase: Post-MVP (`v1.0.0` ya publicado)

| Objetivo                                      | Acción sugerida                                                       |
| --------------------------------------------- | --------------------------------------------------------------------- |
| Crear rama de desarrollo                      | `git checkout -b dev && git push -u origin dev`                       |
| Refinar el prompt del agente IA               | Separar mensaje inicial, flujo de preguntas y respuestas contextuales |
| Agregar `console.log()` detallado en index.js | Para registrar `message.body` y `reply` en tiempo real                |
| Preparar próxima rama: `feat/n8n-automation`  | Para integración con flujos de leads y cupones                        |
| Crear `feat/analytics-airtable`               | Métricas y dashboard desde Airtable o externos                        |

---
