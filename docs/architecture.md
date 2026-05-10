# Internship Pipeline System — Documento de Arquitectura e Ingeniería

**Versión:** 1.0  
**Fecha:** Abril 2026  
**Equipo:** 6 estudiantes — 8vo semestre Ciencias de la Computación e IA  
**Objetivo:** Sistema automatizado para conseguir prácticas internacionales (S1-2027) en empresas tier 1 globales.

---

## 1. Visión y objetivos

### 1.1 Problema
Estudiantes con buen perfil técnico aplican a las mismas empresas locales con cartas genéricas y bajan tasa de éxito. No tienen visibilidad de oportunidades globales, no aprovechan referrals, y compiten entre sí sin coordinación.

### 1.2 Solución
Plataforma interna self-hosted que:
- Mantiene un **watchlist activo de ~160 empresas globales** clasificadas en tiers (A/B/C).
- Encuentra **contactos internos priorizados por afinidad** (alumni → compatriotas → latinos).
- Hace **match técnico automático** entre cada empresa y el miembro del equipo más adecuado.
- Coordina al equipo para **evitar fuego amigo** y maximizar cobertura.
- Genera **outreach personalizado** con aprobación humana, no spam masivo.
- Trackea pipeline individual y agrega métricas para iterar.

### 1.3 Métricas de éxito (definition of done)
- **6 ofertas firmadas** en empresas Tier A o B antes de noviembre 2026.
- **Response rate ≥ 15%** en outreach (industria: 1-3% en cold outreach).
- **≥ 30 entrevistas técnicas conseguidas** entre los 6.
- Sistema operativo, mantenido por el equipo, sin caídas > 24h.

### 1.4 Restricciones
- Hosting: PC personal de un miembro (sin costos de cloud).
- Presupuesto operativo: ≤ $200/mes total ($35/persona).
- Equipo: 6 desarrolladores con tiempo limitado (carga académica paralela).
- Plazo: MVP funcional en 4 semanas; sistema completo en 10 semanas.

---

## 2. Roles y responsabilidades del equipo

Modelo ágil ligero, sprints de 1 semana. Cada miembro asume un rol de "owner" pero todos contribuyen a todo.

| Rol | Responsabilidad principal |
|---|---|
| **Tech Lead / Backend Owner** | Arquitectura, decisiones técnicas, code reviews, FastAPI core |
| **Frontend Owner** | Next.js dashboard, UX, integración con backend |
| **Data/Scraping Owner** | Módulos de discovery, people finder, integración Apify/Apollo |
| **AI/LLM Owner** | Prompts, generación de outreach, tech matching, agentes |
| **DevOps/Infra Owner** | Docker, Cloudflare Tunnel, CI/CD, backups, monitoring |
| **Product/Data Owner** | Curaduría lista de empresas, métricas, post-mortems, KB |

**Ceremonias:**
- Daily async en Discord (15 min, formato standup escrito).
- Weekly sync sincrónico (1h, lunes): demo + planning del sprint.
- Retro quincenal (30 min): qué funciona, qué no.

---

## 3. Arquitectura del sistema

### 3.1 Diagrama de alto nivel

```
                          INTERNET
                              │
                    ┌─────────▼─────────┐
                    │ Cloudflare Tunnel │  (HTTPS, sin abrir puertos)
                    └─────────┬─────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │       PC HOST (Ubuntu/Debian)        │
           │                                       │
           │  ┌─────────────┐    ┌─────────────┐  │
           │  │  Next.js    │◄──►│  FastAPI    │  │
           │  │  Frontend   │    │  Backend    │  │
           │  │  :3000      │    │  :8000      │  │
           │  └─────────────┘    └──────┬──────┘  │
           │                            │          │
           │                    ┌───────┴───────┐  │
           │                    │               │  │
           │              ┌─────▼────┐   ┌─────▼─────┐
           │              │ Postgres │   │   Redis    │
           │              │  :5432   │   │   :6379    │
           │              └──────────┘   └─────┬──────┘
           │                                   │
           │                    ┌──────────────┴──────┐
           │                    │  Celery Workers     │
           │                    │  (scrapers, LLM,    │
           │                    │   email senders)    │
           │                    └──────┬──────────────┘
           │                           │
           │                    ┌──────▼──────┐
           │                    │     n8n     │
           │                    │   :5678     │  (orquestación visual,
           │                    └─────────────┘   notifs Discord, schedules)
           │                                       │
           └───────────────────────────────────────┘
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
    ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
    │   Apify /    │  │  Apollo.io / │  │  Anthropic / │
    │ PhantomBuster│  │  Hunter.io   │  │  OpenAI API  │
    └──────────────┘  └──────────────┘  └──────────────┘
       (scraping)        (emails)          (LLM)
```

### 3.2 Decisiones arquitectónicas (ADRs resumidos)

**ADR-001: Monolito modular en lugar de microservicios.**  
Razón: 6 devs juniors, scope acotado, deploy simple. Microservicios serían overkill.

**ADR-002: Postgres como única DB.**  
Razón: relacional + JSONB cubre todos los casos (incluido tech_profile, notes flexibles). Evitar Mongo/Elasticsearch hasta tener métricas que justifiquen.

**ADR-003: Celery + Redis para tareas async.**  
Razón: scraping y LLM calls son lentos y deben correr fuera del request cycle. Alternativa más simple (apscheduler) considerada y descartada por falta de retry/visibility.

**ADR-004: n8n como orquestador complementario, no reemplazo de código.**  
Razón: workflows visuales para schedulers, webhooks y notificaciones (Discord/email) son más rápidos en n8n. Lógica compleja vive en Python.

**ADR-005: Next.js 14 (App Router) + Tailwind + shadcn/ui.**  
Razón: stack estándar moderno, vibe coding fluido con Claude/Cursor, componentes pre-hechos.

**ADR-006: Auth con magic links (Resend) en lugar de OAuth.**  
Razón: 6 usuarios fijos, no necesita Google login. Magic link = 1 día de implementación vs 3.

**ADR-007: Cloudflare Tunnel en lugar de exponer puertos.**  
Razón: HTTPS gratis, sin configurar router, sin riesgo de exposición directa del PC.

---

## 4. Stack tecnológico definitivo

| Capa | Tecnología | Versión | Justificación |
|---|---|---|---|
| OS host | Ubuntu Server | 22.04 LTS | Estable, soporte Docker nativo |
| Containerización | Docker + Compose | 24+ | Estándar, reproducible |
| Túnel | Cloudflare Tunnel (cloudflared) | latest | HTTPS sin puertos, gratis |
| Backend | Python + FastAPI | 3.11 / 0.110+ | Async, Pydantic, OpenAPI auto |
| ORM | SQLAlchemy 2.0 + Alembic | 2.0+ | Estándar Python, migrations |
| DB | PostgreSQL | 16 | Relacional + JSONB |
| Cache/Queue | Redis | 7 | Celery broker + cache |
| Workers | Celery | 5.3+ | Scraping y LLM async |
| Frontend | Next.js (App Router) | 14+ | SSR, RSC, vibe coding fluido |
| UI | Tailwind + shadcn/ui | latest | Componentes listos |
| Auth | NextAuth + magic links | 5 (beta) | Simple, seguro |
| Orquestación | n8n | latest | Workflows visuales |
| LLM | Anthropic Claude (Sonnet 4.6) | API | Mejor para outreach personalizado |
| Scraping | Playwright + Apify SDK | latest | Anti-bot decente |
| Email finder | Apollo.io + Hunter.io | API | Multi-fuente para coverage |
| Email sender | Resend | API | DX bueno, deliverability alta |
| Monitoring | Uptime Kuma + Loki | latest | Self-hosted, simple |

---

## 5. Módulos del sistema (especificación detallada)

### Módulo 1 — Company Watchlist

**Propósito:** mantener viva la lista de ~160 empresas target y detectar aperturas.

**Componentes:**
- `services/company_watcher.py`: orquestador.
- `scrapers/`: un scraper por fuente (Greenhouse, Lever, Ashby, Workday, careers pages custom).
- Job Celery diario (06:00 UTC): recorre todas las empresas activas, busca nuevas vacantes que matcheen filtros.
- Trigger: si encuentra vacante nueva → notifica Discord + crea entry en `job_postings` + asigna a empresa.

**Inputs:** lista de empresas (curada por Product Owner).  
**Outputs:** `job_postings` table actualizada, notificaciones.

**Edge cases:**
- Careers page cambia HTML → scraper falla. Mitigación: fallback a búsqueda en LinkedIn jobs API + alerta al equipo.
- Rate limiting → exponential backoff, rotate user agents.

---

### Módulo 2 — People Finder multi-fuente con priorización por afinidad

**Propósito:** encontrar contactos internos en cada empresa, priorizando afinidad.

**Pipeline (por empresa):**

```
1. Alumni de tu universidad        (peso: 10) ← LinkedIn search filtrado
2. Colombianos en la empresa       (peso: 8)  ← LinkedIn filtro nacionalidad
3. Latinoamericanos en la empresa  (peso: 6)
4. Recruiters de university progs  (peso: 7)
5. Engineering managers / leads    (peso: 5)
6. Ingenieros en GitHub commits    (peso: 4) ← email de commits públicos
7. Autores de papers de la empresa (peso: 5) ← arXiv affiliation
8. Activos en Twitter/X            (peso: 3)
9. Email pattern + verify          (peso: 2) ← último recurso
```

**Componentes:**
- `services/people_finder.py`: orquestador.
- `enrichers/linkedin.py`: vía Apify actor.
- `enrichers/github.py`: API GitHub + scraping commits.
- `enrichers/apollo.py`, `enrichers/hunter.py`: emails.
- `enrichers/arxiv.py`: papers por afiliación.
- Cada enricher devuelve `Contact` con score y `affinity_type`.

**Output:** tabla `contacts` con top 5-15 por empresa, rankeados.

**Reglas de negocio:**
- Deduplicación por nombre + empresa.
- Score final = `affinity_weight * 0.5 + role_relevance * 0.3 + recency * 0.2`.
- Refresh: cada empresa se re-procesa cada 30 días.

---

### Módulo 3 — Portfolio-Tech Matcher

**Propósito:** decidir cuál de los 6 miembros tiene mejor match para cada empresa.

**Entrada:**
- Tech stack de la empresa (auto-detectado: GitHub repos públicos, job descriptions, blog).
- Tech profile de cada user (auto-generado de su GitHub: lenguajes, frameworks, dominios).

**Algoritmo:**
1. Embedding del stack de la empresa (Claude o sentence-transformers local).
2. Embedding de cada user profile.
3. Cosine similarity → score por user.
4. Ranking: el top-1 puede claimar; el top-2 queda como backup.

**Output:** sugerencia automática en el dashboard: "Esta empresa matchea mejor con: Juan (0.87) > Ana (0.72) > ...".

**Override humano:** un user puede claimar aunque no sea top-1, pero queda registrado.

---

### Módulo 4 — Pipeline Tracker (dashboard personal y de equipo)

**Vistas principales:**

**4.1 — Mi Pipeline (vista personal)**
- Kanban: `Researching → Contacted → Responded → Interview → Offer / Rejected`.
- Cada card: empresa, contacto, próxima acción, deadline.
- Recordatorios automáticos: "Follow-up con X mañana".

**4.2 — Vista de equipo**
- Mapa global de empresas claimed (color por owner).
- Pool de empresas libres (filtrable por tier, país, stack).
- Leaderboard amigable: outreach enviados, responses, interviews.

**4.3 — Empresa detail page**
- Briefing IA-generado (misión, stack, news recientes).
- Lista de contactos rankeados.
- Historial de interacciones del equipo con esa empresa.
- Botón "claim" (con lock atómico).

---

### Módulo 5 — Speculative Outreach Engine

**Propósito:** generar y enviar outreach personalizado por tier.

**Tier A (10 empresas):**
- Sistema genera draft + briefing completo.
- Review humano obligatorio + edición manual.
- Envío manual desde el dashboard.

**Tier B (50 empresas):**
- Sistema genera draft + variantes.
- Review humano (puede ser rápido).
- Envío automatizado con cooldown.

**Tier C (100 empresas):**
- Generación + envío automatizado con plantillas robustas.
- Spot-check humano (10% sample).

**Anti-spam rules (hard-coded):**
- Max 1 mensaje por persona.
- Follow-up max 1 vez, 7 días después.
- Max 20 envíos/día por user (warm-up).
- Cooldown 24h entre envíos a misma empresa por equipo.
- Lock atómico Postgres antes de enviar.

**Componentes:**
- `services/outreach_generator.py`: prompt builder + LLM call.
- `services/email_sender.py`: integración Resend con tracking.
- Tabla `outreach_log` con cada envío y status (sent/opened/replied).

---

### Módulo 6 — Interview Knowledge Base

**Propósito:** cada entrevista alimenta al equipo.

**Componentes:**
- Tabla `interviews`: empresa, user, fecha, formato, preguntas, outcome, notas.
- Después de cada entrevista, recordatorio automático para llenar post-mortem (24h).
- Vista "Prep mode" por empresa: muestra todas las entrevistas pasadas del equipo en esa empresa.
- Integración con herramientas externas (Pramp, interviewing.io) — links, no reimplementación.

---

### Módulo 7 — Visa & Sponsorship Filter

**Propósito:** flag de viabilidad legal por empresa.

**Datos:**
- Tabla `visa_data`: empresa + país → `intern_friendly` (bool), `visa_type`, `evidence_url`, `last_verified`.
- Fuentes: MyVisaJobs (J-1), Praktikantenbewilligung Suiza, programas formales (ByteDance Global, Google STEP, etc.).
- Curaduría manual asistida por IA (no 100% automatizable, demasiada nuance legal).

**UI:** badge en cada empresa: 🟢 friendly / 🟡 case-by-case / 🔴 muy difícil.

---

## 6. Modelo de datos (schema completo)

```sql
-- Usuarios del equipo (6 miembros)
CREATE TABLE users (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  email TEXT UNIQUE NOT NULL,
  github_handle TEXT,
  linkedin_url TEXT,
  tech_profile JSONB,           -- auto-generado: {languages: [...], frameworks: [...]}
  tech_embedding VECTOR(1536),  -- pgvector para matching
  role TEXT DEFAULT 'member',   -- member | admin
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Empresas target
CREATE TABLE companies (
  id UUID PRIMARY KEY,
  name TEXT NOT NULL,
  domain TEXT UNIQUE,
  tier CHAR(1) CHECK (tier IN ('A','B','C')),
  country TEXT,
  region TEXT,                  -- USA, EU, China, LATAM, etc.
  careers_url TEXT,
  ats_type TEXT,                -- greenhouse | lever | ashby | workday | custom
  tech_stack JSONB,             -- ["python","rust","kubernetes"]
  tech_embedding VECTOR(1536),
  visa_friendly_intern TEXT,    -- green | yellow | red | unknown
  visa_notes TEXT,
  briefing TEXT,                -- IA-generated
  briefing_updated_at TIMESTAMPTZ,
  claimed_by UUID REFERENCES users(id),
  claimed_at TIMESTAMPTZ,
  locked_until TIMESTAMPTZ,     -- lock atómico para outreach
  status TEXT DEFAULT 'active', -- active | paused | rejected | won
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_companies_tier ON companies(tier);
CREATE INDEX idx_companies_claimed ON companies(claimed_by);

-- Contactos dentro de empresas
CREATE TABLE contacts (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id) ON DELETE CASCADE,
  full_name TEXT NOT NULL,
  role TEXT,
  email TEXT,
  linkedin_url TEXT,
  github_handle TEXT,
  twitter_handle TEXT,
  source TEXT,                  -- linkedin | github | apollo | arxiv | manual
  affinity_type TEXT,           -- alumni | colombian | latino | none
  affinity_score INT,           -- 0-100
  role_relevance INT,           -- 0-100
  total_score INT,              -- composite
  metadata JSONB,               -- posts recientes, papers, etc.
  contacted BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  refreshed_at TIMESTAMPTZ
);
CREATE INDEX idx_contacts_company ON contacts(company_id);
CREATE INDEX idx_contacts_score ON contacts(total_score DESC);

-- Job postings detectados
CREATE TABLE job_postings (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  title TEXT,
  url TEXT UNIQUE,
  location TEXT,
  remote BOOLEAN,
  description TEXT,
  detected_at TIMESTAMPTZ DEFAULT now(),
  closed_at TIMESTAMPTZ,
  status TEXT DEFAULT 'open'
);

-- Aplicaciones del equipo
CREATE TABLE applications (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  user_id UUID REFERENCES users(id),
  job_posting_id UUID REFERENCES job_postings(id),
  type TEXT,                    -- formal | speculative
  status TEXT,                  -- researching|contacted|responded|interviewing|offer|rejected
  applied_at TIMESTAMPTZ,
  next_action TEXT,
  next_action_due DATE,
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Log de outreach
CREATE TABLE outreach_log (
  id UUID PRIMARY KEY,
  contact_id UUID REFERENCES contacts(id),
  user_id UUID REFERENCES users(id),
  application_id UUID REFERENCES applications(id),
  channel TEXT,                 -- email | linkedin | twitter
  subject TEXT,
  body TEXT,
  template_id UUID,
  sent_at TIMESTAMPTZ,
  opened_at TIMESTAMPTZ,
  replied_at TIMESTAMPTZ,
  reply_sentiment TEXT,         -- positive | neutral | negative
  status TEXT                   -- queued | sent | bounced | replied
);

-- Plantillas
CREATE TABLE templates (
  id UUID PRIMARY KEY,
  name TEXT,
  type TEXT,                    -- intro | followup | informational
  tier CHAR(1),
  content TEXT,
  variables JSONB,              -- {company_name, contact_name, ...}
  success_rate FLOAT,
  created_by UUID REFERENCES users(id),
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Entrevistas (knowledge base)
CREATE TABLE interviews (
  id UUID PRIMARY KEY,
  company_id UUID REFERENCES companies(id),
  user_id UUID REFERENCES users(id),
  scheduled_at TIMESTAMPTZ,
  type TEXT,                    -- phone | technical | system_design | behavioral | onsite
  interviewer_role TEXT,
  questions JSONB,
  outcome TEXT,                 -- passed | failed | pending
  notes TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);

-- Audit log para acciones críticas
CREATE TABLE audit_log (
  id UUID PRIMARY KEY,
  user_id UUID,
  action TEXT,
  entity_type TEXT,
  entity_id UUID,
  metadata JSONB,
  created_at TIMESTAMPTZ DEFAULT now()
);
```

**Extensiones requeridas:** `pgvector` para embeddings, `uuid-ossp` para UUIDs.

---

## 7. Flujos críticos (sequence diagrams en texto)

### 7.1 Flujo: agregar empresa nueva al sistema

```
Product Owner → Dashboard → POST /companies {name, tier, country}
  Backend → INSERT companies
  Backend → Celery.enqueue(enrich_company, company_id)
    Worker → scrape careers_url → detectar ats_type
    Worker → scrape blog/repos → detectar tech_stack
    Worker → LLM → generar briefing
    Worker → Celery.enqueue(find_people, company_id)
      Worker → ejecutar enrichers en paralelo (LinkedIn, GitHub, Apollo, ...)
      Worker → calcular scores → INSERT contacts
    Worker → Celery.enqueue(match_team, company_id)
      Worker → cosine sim → sugerir owner
  → Notify Discord: "Nueva empresa lista: [X]. Match sugerido: Juan"
```

### 7.2 Flujo: enviar outreach (Tier B)

```
User → Dashboard → click "Generate outreach" en Contact card
  Frontend → POST /outreach/draft {contact_id}
  Backend → check lock: SELECT FOR UPDATE en companies.locked_until
  Backend → LLM → generar 2 variantes con briefing + perfil contacto + perfil user
  → return drafts
User → revisa → edita → click "Send"
  Frontend → POST /outreach/send {draft_id, final_body}
  Backend → set companies.locked_until = now() + 7 days
  Backend → Resend.send(...)
  Backend → INSERT outreach_log
  Backend → schedule followup task (+7 days)
  → Notify Discord: "Juan envió outreach a Maria @ Stripe"
```

### 7.3 Flujo: detección de respuesta

```
n8n workflow (cada 15 min):
  → Resend webhook → /webhooks/email-reply
  Backend → identificar outreach_log por message-id
  Backend → UPDATE replied_at, reply_sentiment (LLM clasifica)
  Backend → UPDATE application.status = 'responded'
  → Notify user en Discord DM: "¡Maria @ Stripe respondió! [link]"
```

---

## 8. Seguridad y compliance

### 8.1 Riesgos identificados
1. **Ban de cuentas LinkedIn** por scraping agresivo → usar Apify (cuentas dedicadas), no las personales.
2. **Quema de dominio email** → dominio secundario, warm-up gradual, SPF/DKIM/DMARC.
3. **Leak de datos** (lista de contactos es sensible) → DB no expuesta, backups encriptados.
4. **GDPR / privacidad** de contactos europeos → solo guardar info pública, permitir delete on request.
5. **PC personal cae** → backups diarios a Cloudflare R2 o Backblaze B2.

### 8.2 Controles
- Secrets en `.env` nunca commiteados; usar `.env.example`.
- Backups automáticos: `pg_dump` diario a R2 (cifrado), retención 30 días.
- Logs sin info sensible (no loguear emails completos).
- Rate limits en API pública.
- Auth obligatoria en todos los endpoints excepto webhooks (que validan signature).

---

## 9. DevOps y deployment

### 9.1 Setup inicial del PC host
1. Ubuntu Server 22.04 limpio.
2. Instalar Docker + Compose.
3. Crear cuenta Cloudflare → agregar dominio → crear Tunnel.
4. Configurar `cloudflared` como servicio systemd.
5. Clonar repo → `docker compose up -d`.
6. Correr migrations: `docker compose exec backend alembic upgrade head`.
7. Seed data: `python scripts/seed_companies.py`.

### 9.2 CI/CD (ligero)
- **GitHub Actions:** lint (ruff, eslint), tests, build images.
- **Deploy:** push a `main` → webhook al PC → `git pull && docker compose up -d --build`.
- No staging environment (overkill); usar feature branches + preview en localhost.

### 9.3 Backups
- Daily cron: `pg_dump` → cifrado GPG → upload a R2 (free tier).
- Retención: 7 daily + 4 weekly + 3 monthly.
- Test de restore mensual.

### 9.4 Monitoring
- **Uptime Kuma** chequea: backend health, frontend, postgres, n8n.
- Alertas → Discord webhook.
- Logs centralizados en Loki (opcional, fase 2).

---

## 10. Roadmap por sprints (10 semanas)

### Sprint 0 — Setup (semana 1)
- [ ] Repos GitHub creados (mono-repo).
- [ ] Docker Compose con todos los servicios up.
- [ ] Cloudflare Tunnel configurado, dominio funcionando.
- [ ] FastAPI hello world + Postgres conectado + migrations base.
- [ ] Next.js hello world + auth magic link funcional.
- [ ] CI básico (lint + tests vacíos pasando).
- **Demo:** login funciona, dashboard vacío visible en dominio.

### Sprint 1 — Core data layer (semana 2)
- [ ] Schema completo migrado.
- [ ] CRUD endpoints: users, companies, contacts.
- [ ] Frontend: páginas listado de companies + detail page (sin features avanzados).
- [ ] Seed script con 20 empresas de prueba.
- **Demo:** equipo puede agregar/ver empresas manualmente.

### Sprint 2 — Tracker y coordinación (semana 3)
- [ ] Módulo 4 completo: kanban personal, claim/lock, vista equipo.
- [ ] Notificaciones Discord vía n8n.
- [ ] 6 users del equipo onboarded.
- **Demo:** cada miembro usa el tracker manualmente para sus aplicaciones actuales.

### Sprint 3 — Discovery (semana 4) — **MVP COMPLETO**
- [ ] Módulo 1: scrapers de Greenhouse, Lever, Ashby (los 3 ATS más comunes).
- [ ] Job diario corriendo.
- [ ] Lista oficial de 160 empresas curada (Tier A: 10, B: 50, C: 100).
- **Demo:** sistema detecta vacantes nuevas automáticamente, las muestra en dashboard.

### Sprint 4 — People Finder I (semana 5)
- [ ] Integración Apify para LinkedIn.
- [ ] Integración Apollo + Hunter.
- [ ] Lógica de affinity scoring (alumni, colombiano, latino).
- **Demo:** generar lista de top 10 contactos para 5 empresas Tier A.

### Sprint 5 — People Finder II + Tech Matcher (semana 6)
- [ ] Enricher GitHub (commits, repos).
- [ ] Enricher arXiv.
- [ ] Módulo 3: tech embeddings + matching.
- **Demo:** sistema sugiere owner óptimo por empresa.

### Sprint 6 — Outreach Engine (semana 7)
- [ ] Generador de drafts con LLM.
- [ ] Templates Tier A/B/C.
- [ ] Integración Resend + dominio secundario warmed up.
- [ ] Anti-spam rules.
- **Demo:** flujo completo: claim → generar → revisar → enviar → trackear.

### Sprint 7 — Tracking de respuestas (semana 8)
- [ ] Webhook de Resend.
- [ ] Clasificación de sentiment por LLM.
- [ ] Notificaciones a Discord en respuestas.
- [ ] Followup automático scheduling.
- **Demo:** ciclo completo end-to-end con respuesta real.

### Sprint 8 — Interview KB + Visa Filter (semana 9)
- [ ] Módulo 6: tabla de entrevistas, post-mortems, prep mode.
- [ ] Módulo 7: visa filter UI + carga inicial de datos.
- **Demo:** equipo registra primera entrevista real, otros la ven.

### Sprint 9 — Polish, métricas, docs (semana 10)
- [ ] Dashboard de métricas globales.
- [ ] Documentación de uso para el equipo.
- [ ] Backup/restore probado.
- [ ] Retro general + plan de operación post-MVP.
- **Demo:** sistema en producción, equipo operándolo.

---

## 11. Estructura de repositorio

```
internship-pipeline/
├── README.md
├── docker-compose.yml
├── docker-compose.prod.yml
├── .env.example
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── deploy.yml
├── backend/
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── alembic.ini
│   ├── alembic/versions/
│   ├── app/
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── db.py
│   │   ├── models/
│   │   ├── schemas/
│   │   ├── routers/
│   │   ├── services/
│   │   │   ├── company_watcher.py
│   │   │   ├── people_finder.py
│   │   │   ├── tech_matcher.py
│   │   │   ├── outreach_generator.py
│   │   │   └── llm.py
│   │   ├── scrapers/
│   │   │   ├── greenhouse.py
│   │   │   ├── lever.py
│   │   │   └── ashby.py
│   │   ├── enrichers/
│   │   │   ├── linkedin.py
│   │   │   ├── github.py
│   │   │   ├── apollo.py
│   │   │   ├── hunter.py
│   │   │   └── arxiv.py
│   │   ├── workers/
│   │   │   ├── celery_app.py
│   │   │   └── tasks.py
│   │   └── webhooks/
│   └── tests/
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── next.config.js
│   ├── tailwind.config.ts
│   ├── app/
│   │   ├── (auth)/
│   │   ├── (dashboard)/
│   │   │   ├── companies/
│   │   │   ├── contacts/
│   │   │   ├── pipeline/
│   │   │   ├── interviews/
│   │   │   └── metrics/
│   │   └── api/
│   ├── components/
│   │   ├── ui/        (shadcn)
│   │   └── features/
│   └── lib/
├── n8n/
│   └── workflows/      (JSON exports)
├── scripts/
│   ├── seed_companies.py
│   ├── backup_db.sh
│   └── restore_db.sh
└── docs/
    ├── architecture.md  (este doc)
    ├── runbook.md
    ├── onboarding.md
    └── api.md
```

---

## 12. Costos operativos detallados

| Concepto | Costo/mes | Notas |
|---|---|---|
| Hosting (PC propio) | $0 | Electricidad ~$5 |
| Dominio principal | $0 | Ya lo tienes |
| Dominio secundario outreach | $1 | $12/año |
| Cloudflare Tunnel | $0 | Free tier |
| Cloudflare R2 (backups) | $0 | <10GB free |
| Apify (LinkedIn scraping) | $50 | Plan Personal |
| Apollo.io | $0-50 | Free: 50 emails/mes/user × 6 = 300 |
| Hunter.io | $0 | Free tier 25 búsquedas/mes |
| Anthropic Claude API | $40 | ~10M tokens/mes estimado |
| Resend (email) | $20 | 50k emails/mes |
| **Total** | **~$110-160/mes** | **$18-27 por persona** |

---

## 13. Definition of Ready & Definition of Done

**DoR (para empezar un ticket):**
- Acceptance criteria claros.
- Diseño técnico discutido si toca arquitectura.
- Dependencies identificadas.
- Estimación en horas (Fibonacci: 1, 2, 3, 5, 8).

**DoD (para mergear):**
- Code reviewed por al menos 1 persona.
- Tests pasando (mínimo happy path).
- Documentado en código (docstrings) y en `/docs` si es feature nueva.
- Probado manualmente en local.
- Sin secrets hardcoded.

---

## 14. Riesgos del proyecto y mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigación |
|---|---|---|---|
| Equipo sin tiempo (carga académica) | Alta | Alto | Sprints cortos, scope estrictamente priorizado |
| Scraping bloqueado (LinkedIn ban) | Media | Alto | Usar Apify (cuentas dedicadas), no escalar sin warm-up |
| LLM costs explotan | Baja | Medio | Caching agresivo, budget alerts, usar Haiku donde sirva |
| PC host se cae | Media | Medio | Backups + runbook de restore + redundancia con segundo equipo si crítico |
| Tasas de respuesta bajas | Media | Alto | Iterar en outreach, A/B testing de templates, doblar apuesta en alumni |
| Conflictos en el equipo | Media | Medio | Roles claros, retros quincenales, decisiones por tech lead |

---

## 15. Próximos pasos inmediatos (esta semana)

1. **Hoy:** este doc → revisión del equipo → ajustes.
2. **Día 1-2:** asignación de roles, creación de repo, setup local de cada uno.
3. **Día 3-5:** Sprint 0 ejecutado → demo del viernes.
4. **En paralelo:** Product Owner empieza curaduría de las 160 empresas (entregar a Sprint 3).
5. **En paralelo:** todos los miembros trabajan en sus activos personales (CV inglés, GitHub, LinkedIn) — no negociable.

---

**Fin del documento.**
