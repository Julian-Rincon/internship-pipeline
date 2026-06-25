# Tutorial de Usuario — Internship Pipeline

Esta guía explica cómo usar el sistema paso a paso, desde que te registras hasta que tienes una aplicación activa con seguimiento automático de recordatorios.

---

## ¿Qué es este sistema?

Un dashboard interno para equipos de estudiantes que aplican a prácticas internacionales. Centraliza:

- Empresas target con estado de investigación por persona
- Contactos manuales por empresa
- Aplicaciones con seguimiento de estado y próximas acciones
- Descubrimiento automático de vacantes desde Greenhouse, Lever, Ashby y GetOnBoard
- Recordatorios internos (sin correos, sin outreach automático)
- Notificaciones opcionales vía Telegram (n8n)

**No hace:** scraping de LinkedIn, envío de correos, outreach automático, People Finder, uso de datos personales reales en demo.

---

## URLs locales

| Servicio | URL |
|---|---|
| Dashboard | http://localhost:3001 |
| API Swagger | http://localhost:8000/docs |
| n8n | http://localhost:5678 |

---

## Paso 1 — Registrarte como usuario

Ve a **http://localhost:3001/users** y crea tu perfil.

**Campos mínimos requeridos:**

| Campo | Ejemplo |
|---|---|
| `name` | Julian Rincon |
| `email` | julianer2002@gmail.com |
| `role` | `member` o `admin` |

**Campos de perfil (completa después):**

| Campo | Descripción |
|---|---|
| `github_handle` | Tu usuario de GitHub (sin @) |
| `linkedin_url` | URL completa de tu LinkedIn |
| `cv_url` | URL de tu CV o portafolio |
| `portfolio_url` | URL de tu portafolio web |
| `target_roles` | Lista: "ML Engineering Intern", "Data Engineering Intern"... |
| `target_countries` | Lista: "Germany", "Netherlands", "USA"... |
| `target_regions` | Lista: "Remote", "EU"... |
| `strong_skills` | Lista: "Python", "FastAPI", "PyTorch"... |
| `technical_interests` | Lista: "LLMs", "MLOps", "Data Pipelines"... |
| `internship_goals` | Texto libre: tus objetivos de prácticas |
| `profile_status` | `incomplete` → `in_progress` → `ready` |

> Tip: solo cuando `profile_status = ready` el equipo sabe que tu perfil está listo para matching manual.

**Via API (también funciona):**

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Tu Nombre",
    "email": "tu@email.com",
    "role": "member"
  }'
```

---

## Paso 2 — Explorar empresas y reclamar una

Ve a **http://localhost:3001/companies**.

Cada empresa tiene:
- **Tier**: A (top target) → B → C → D
- **Ownership status**: `unclaimed` → `claimed` → `paused` → `done`
- **ATS type**: greenhouse / lever / ashby / getonboard / direct

**Cómo reclamar una empresa:**

1. Abre el detalle de la empresa (click en su nombre)
2. En el panel de ownership, selecciona tu usuario
3. Agrega notas: "Investigando ML roles para verano 2026"
4. Click **Claim**

Esto le dice al equipo que tú eres quien investiga esa empresa. Nadie más debería duplicar el trabajo.

**Estados de ownership:**

| Estado | Significado |
|---|---|
| `unclaimed` | Disponible — nadie la está trabajando |
| `claimed` | La estás investigando activamente |
| `paused` | La pusiste en pausa temporalmente |
| `done` | Ya no hay acción por tomar (aplicaste o descartaste) |

> Una empresa reclamada por más de 14 días sin actualización aparece en **Reminders** como `stale_claim`.

---

## Paso 3 — Agregar contactos

Ve a **http://localhost:3001/contacts** o desde el detalle de la empresa.

Agrega solo contactos que obtuviste manualmente (LinkedIn, email directo, evento, referral).

| Campo | Descripción |
|---|---|
| `full_name` | Nombre del contacto |
| `email` | Email si tienes uno |
| `title` | Cargo (Recruiter, Engineering Manager...) |
| `company_id` | La empresa a la que pertenece |
| `source` | `manual` (por ahora, siempre manual) |
| `affinity_type` | `unknown`, `warm`, `cold`, `referred` |

**No uses datos personales reales en ambiente de prueba.** Para demo usa nombres ficticios o datos de `@example.com`.

---

## Paso 4 — Crear una aplicación

Ve a **http://localhost:3001/applications** → **New application**.

Una aplicación conecta:
- Un **usuario** (tú)
- Una **empresa**
- Un **contacto** opcional

**Campos requeridos:**

| Campo | Opciones / ejemplo |
|---|---|
| `company_id` | UUID de la empresa |
| `user_id` | Tu UUID |
| `type` | `formal`, `speculative`, `referral`, `networking`, `other` |
| `status` | empieza en `researching` |

**Campos opcionales importantes:**

| Campo | Descripción |
|---|---|
| `role_title` | "ML Engineering Intern" |
| `next_action` | "Aplicar via Greenhouse el viernes" |
| `next_action_due` | Fecha límite ISO: "2026-07-01" |
| `notes` | Contexto, links, notas de la entrevista |

### Flujo de estados

```
researching → contacted → responded → interviewing → offer
                                                   ↘ rejected
                                                   ↘ paused
```

Actualiza el estado y `next_action` cada vez que haya movimiento. El sistema no hace seguimiento automático — tú eres quien mantiene esto actualizado.

### Crear aplicación desde una vacante revisada

1. Ve a `/discovery` y aprueba un candidato
2. Ve a `/job-postings`
3. Busca el posting de esa empresa
4. Click **Link to company** si no está vinculado
5. Click **Create application** — elige tu usuario

Esto pone el título del rol y la URL de la vacante en las notas automáticamente.

---

## Paso 5 — Usar el Discovery

El discovery alimenta el pipeline con vacantes reales de ATS públicos.

### 5a. Ver candidatos pendientes

Ve a **http://localhost:3001/discovery**.

Verás candidatos con `pending_review`. Para cada uno puedes ver:
- Empresa detectada
- Título del rol
- URL de la vacante
- Fuente (greenhouse, lever, ashby, getonboard)
- Confidence score (0–1)

**Aprobar** → crea o vincula la empresa en el sistema + abre el job posting.  
**Rechazar** → descarta el candidato sin crear empresa.

> Nunca se convierte una empresa en "oficial" sin revisión humana.

### 5b. Correr las fuentes manualmente

Ve a **http://localhost:3001/discovery/sources**.

Puedes correr una fuente individual (botón Run) o todas las habilitadas a la vez (Run all enabled).

Cada corrida hace un GET público al ATS, filtra títulos que parezcan "internship/early-career", y crea candidatos pendientes de revisión.

**Fuentes habilitadas por defecto:** Anthropic, Scale AI, Vercel, Cloudflare, Databricks, Figma, Twilio, Stripe (Greenhouse), Airtable, Notion, Linear, Cohere, Replit, Perplexity AI (Ashby), GetOnBoard Latam.

### 5c. Registrar una fuente nueva

En `/discovery/sources` → New source:

| Campo | Ejemplo Greenhouse | Ejemplo Lever | Ejemplo Ashby |
|---|---|---|---|
| `source_type` | `greenhouse` | `lever` | `ashby` |
| `source_key` | `openai` | `figma` | `linear` |
| `name` | "OpenAI Internships" | ... | ... |

La `source_key` es el identificador que usa el ATS en su URL pública.

Para Greenhouse: `https://boards-api.greenhouse.io/v1/boards/{source_key}/jobs`  
Para Lever: `https://api.lever.co/v0/postings/{source_key}`  
Para Ashby: `https://api.ashbyhq.com/posting-api/job-board/{source_key}`

---

## Paso 6 — Revisar recordatorios

Ve a **http://localhost:3001/reminders**.

Los recordatorios se calculan en tiempo real. Tipos:

| Tipo | Descripción |
|---|---|
| **Overdue** | `next_action_due` pasó, estado activo |
| **Due today** | Acción vence hoy |
| **Due soon** | Vence en los próximos 7 días |
| **Pending review** | Candidatos de discovery sin revisar |
| **Stale claim** | Empresa reclamada > 14 días sin cambio |

Desde el reminder puedes navegar directo a la aplicación o empresa correspondiente.

**Los recordatorios son solo visibilidad interna.** No se envían emails ni mensajes externos desde esta pantalla.

---

## Paso 7 — Notificaciones automáticas vía n8n (opcional)

Si el servidor tiene n8n configurado con Telegram, recibirás resúmenes automáticos.

### Daily Discovery Digest (equipo)

- Lunes a viernes a las 9am
- Corre todas las fuentes habilitadas
- Envía resumen de candidatos pendientes al chat configurado
- Requiere: credencial Telegram en n8n + `TELEGRAM_CHAT_ID` en `.env`

### JARVIS Personal Alerts (solo Julian)

- Lunes a viernes: 8am, 12pm, 6pm
- Filtra candidatos con keywords ML/AI/Data Engineering
- Reporta solo tus aplicaciones con acción pendiente
- Envía via JARVIS bot al chat personal
- Requiere: `JARVIS_TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` en `.env` + credencial "JARVIS Bot" en n8n

**Para configurar la credencial Telegram en n8n:**

1. Abre http://localhost:5678
2. Settings → Credentials → New
3. Busca "Telegram API"
4. Nombre: "Internship Pipeline Bot" (o "JARVIS Bot" para el workflow personal)
5. Pega el bot token de @BotFather
6. Guarda
7. Importa el workflow JSON desde `n8n/workflows/`
8. Asigna la credencial al nodo "Send Telegram"
9. Activa el workflow

---

## Vista rápida del dashboard

El dashboard (http://localhost:3001) muestra en tiempo real:

```
Companies   Users   Contacts   Applications
    1          1        1           1

Reminders:  [overdue: 0] [due today: 0] [due soon: 0] [pending review: 17]

Company ownership:  [unclaimed: 0] [claimed: 1] [paused: 0] [done: 0]

Pipeline status:
  interviewing: 1
```

---

## API directa (avanzado)

Todos los endpoints están documentados en http://localhost:8000/docs.

Ejemplo básico con curl — crear usuario mínimo:

```bash
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "Ana García", "email": "ana@example.com", "role": "member"}'
```

Ejemplo — listar candidatos pendientes:

```bash
curl "http://localhost:8000/discovery-candidates?status=pending_review"
```

Ejemplo — resumen para n8n:

```bash
curl "http://localhost:8000/reminders/n8n-summary?days_ahead=7"
```

---

## Reglas del sistema (para todos)

1. **No uses datos personales reales** en ambiente de prueba — solo cuando esté en producción con privacidad revisada
2. **No conectes fuentes ATS privadas** — solo boards públicos sin autenticación
3. **Aprueba manualmente** cada discovery candidate — nunca dejes que pasen solos
4. **No configures outreach automático** sin aprobación del equipo
5. **No commits de `.env`**, tokens, API keys ni credenciales

---

## Perfil de ejemplo: Julian Rincon

Para ver cómo luce un perfil completo listo para uso:

```bash
curl http://localhost:8000/users/4fafd6de-9301-49b1-a7df-7ed6b01e3231 | python3 -m json.tool
```

Campos notables:
- `profile_status: "ready"`
- `strong_skills`: Python, FastAPI, SQLAlchemy, AWS, Docker, PyTorch, XGBoost, PySpark
- `target_countries`: Germany, Netherlands, USA, Canada
- `target_roles`: ML Engineering Intern, Data Engineering Intern, AI Research Intern
- `internship_goals`: EU internship in ML/Data Engineering, Germany preferred for MSc

---

## Comandos útiles de administración

```bash
# Levantar todo
docker compose up -d

# Ver logs en tiempo real
docker compose logs -f backend
docker compose logs -f n8n

# Correr tests
docker compose exec backend pytest -v

# Aplicar migraciones
docker compose exec backend alembic upgrade head

# Correr todas las fuentes ATS habilitadas
curl -X POST http://localhost:8000/discovery-sources/run-enabled

# Ver resumen de recordatorios
curl http://localhost:8000/reminders/n8n-summary | python3 -m json.tool

# Reiniciar solo n8n
docker compose restart n8n

# Parar todo sin borrar datos
docker compose down

# Parar y borrar datos (cuidado)
docker compose down -v
```

---

## Troubleshooting

**Frontend no carga:**
```bash
docker compose logs frontend --tail=20
# Si hay error de puerto: cambia FRONTEND_PORT en .env
```

**Backend no responde:**
```bash
curl http://localhost:8000/health
docker compose logs backend --tail=30
```

**Discovery sources retornan 404:**
- El ATS board de la empresa puede haber cambiado su key o estar deshabilitado
- Desactiva la fuente y agrega la nueva key desde la UI de discovery sources

**n8n no envía Telegram:**
- Verifica que la credencial Telegram esté configurada en n8n Credentials
- Verifica que `TELEGRAM_CHAT_ID` esté en `.env`
- Reinicia n8n: `docker compose restart n8n`

**Tests fallan por datos previos:**
```bash
# Limpiar datos de tests anteriores que no se revirtieron
docker compose exec postgres psql -U internship -d internship_pipeline \
  -c "DELETE FROM users WHERE email LIKE '%@example.com';"
```
