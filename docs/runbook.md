# Runbook local

## Arranque inicial

1. Copia variables de entorno:

   ```bash
   cp .env.example .env
   ```

2. Levanta servicios:

   ```bash
   docker compose up --build
   ```

3. Aplica migraciones:

   ```bash
   docker compose exec backend alembic upgrade head
   ```

4. Verifica backend:

   ```bash
   curl http://localhost:8000/health
   ```

5. Abre el dashboard:

   http://localhost:3000

## Operacion diaria

Levantar servicios en background:

```bash
docker compose up -d
```

Ver logs:

```bash
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f postgres
docker compose logs -f n8n
```

Detener servicios:

```bash
docker compose down
```

Detener y borrar volumenes locales:

```bash
docker compose down -v
```

Usa `down -v` solo si quieres perder la base de datos local.

## Migraciones

Aplicar migraciones:

```bash
docker compose exec backend alembic upgrade head
```

Crear una migracion futura:

```bash
docker compose exec backend alembic revision --autogenerate -m "describe change"
```

## Pruebas manuales rapidas

Health:

```bash
curl http://localhost:8000/health
```

Crear company ficticia:

```bash
curl -X POST http://localhost:8000/companies \
  -H "Content-Type: application/json" \
  -d '{"name":"Example AI Lab","domain":"example-ai-lab.test","tier":"A","status":"active"}'
```

Listar companies:

```bash
curl http://localhost:8000/companies
```

PowerShell equivalente:

```powershell
curl.exe http://localhost:8000/health
curl.exe http://localhost:8000/companies
```

## Perfiles progresivos

Los integrantes pueden crearse con datos minimos:

- `name`
- `email`
- `role`
- `profile_status`

GitHub, LinkedIn, CV, portafolio, intereses tecnicos y objetivos son opcionales. Cada integrante puede completar su perfil despues desde `/users` o via API.

Estados permitidos:

- `incomplete`: perfil creado con datos basicos.
- `in_progress`: perfil en edicion.
- `ready`: perfil completado y revisado manualmente.

No se debe activar matching, embeddings, scraping, People Finder ni outreach hasta que los perfiles relevantes esten revisados manualmente y el equipo apruebe continuar.

## Contacts manuales

Los contacts existen por ahora solo para carga manual y con datos ficticios o de prueba. No hay scraping, People Finder, enrichment automatico ni llamadas a LinkedIn, Apollo, Hunter, Resend, OpenAI o Anthropic.

Reglas de esta fase:

- No cargar datos reales sin revision explicita del equipo.
- No enviar correos ni mensajes desde el sistema.
- No marcar contactos reales como fuente de outreach.
- `source` debe usarse como `manual` en esta etapa.
- People Finder queda para una fase posterior con aprobacion separada.

## Applications manuales

`applications` conecta manualmente una company, un user y opcionalmente un contact. Este modulo solo registra estado del pipeline, siguiente accion, fecha limite y notas.

No hay automatizacion de outreach, envio de correos, scraping, matching, embeddings ni llamadas a APIs externas. Los estados se cambian manualmente por ahora: `researching`, `contacted`, `responded`, `interviewing`, `offer`, `rejected`, `paused`.

Antes de usar datos reales, el equipo debe revisar manualmente perfiles, companies y contacts. n8n sigue sin workflows activos para este flujo.

## Tests

Ejecutar suite backend:

```bash
docker compose exec backend pytest
```

Los tests usan rollback por test mediante dependency override de FastAPI. Aunque apuntan al mismo Postgres local del stack, no deben persistir datos en las tablas visibles por el dashboard.

Para limpiar datos de prueba que quedaron antes de este aislamiento:

```bash
docker compose exec postgres psql -U internship -d internship_pipeline -c "DELETE FROM users WHERE email LIKE '%@example.com' OR name IN ('Duplicate User','Status User','Patch User','Get User','List User','Example Member');"
docker compose exec postgres psql -U internship -d internship_pipeline -c "DELETE FROM companies WHERE domain LIKE '%example-%.test' OR name IN ('Example Systems','List Example','Get Example','Patch Example','Delete Example','Invalid Tier Example');"
```

## Nota n8n

El aviso de logs sobre Python task runner missing no bloquea esta fase. n8n esta levantado solo como orquestador complementario y todavia no usamos Python Code nodes ni workflows externos reales.

## Reglas de seguridad de esta fase

- No guardar datos personales reales.
- No guardar tokens, API keys o credenciales reales.
- No enviar correos ni mensajes desde el sistema.
- No activar workflows n8n con acciones externas sin aprobacion.
- No implementar scraping ni People Finder todavia.

## Checklist de seguridad ANTES de desplegar en un servidor real (2026-07-06)

Esto ya no es "esta fase local" — es para quien vaya a correr `docker compose up`
en una máquina con IP pública (Windows o Linux, docker compose funciona igual
en ambos). Auditoría de seguridad hecha 2026-07-05 encontró 63 endpoints sin
ninguna autenticación, Postgres/Redis/n8n expuestos a toda la red, y passwords
en el valor literal `change-me-local-only`. Ya se arregló en código (ver
commit correspondiente); esto es lo que falta hacer AL MOMENTO DEL DEPLOY:

1. **Generar secretos reales** — uno distinto por cada valor, con:
   ```
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Reemplazar en `.env` (nunca en `.env.example`, ni commitear `.env`):
   - `API_KEY` (protege los 63 endpoints del backend — antes no existía nada)
   - `POSTGRES_PASSWORD` (y actualizar `DATABASE_URL` con el mismo valor)
   - `N8N_BASIC_AUTH_PASSWORD`
   - `N8N_ENCRYPTION_KEY`

2. **`CORS_ORIGINS`** — poner la URL real donde va a vivir el frontend
   (ej. `https://internships.tu-dominio.com`), no `localhost`. Si el frontend
   corre en un puerto/dominio distinto al que quede aquí, las llamadas desde
   el navegador van a fallar por CORS.

3. **Ya viene resuelto en `docker-compose.yml`** (no requiere acción, solo
   verificar que no se haya revertido): Postgres (5432), Redis (6379) y n8n
   (5678) están publicados solo en `127.0.0.1` — ya no son alcanzables desde
   fuera de esa máquina. Solo `backend` (8000) y `frontend` (3000/3001)
   quedan expuestos a la red, que es lo que sí necesita ser público.

4. **Recomendado, no bloqueante**: poner un reverse proxy (Caddy o nginx) con
   HTTPS delante de `frontend` y `backend` — ahora mismo todo viaja en HTTP
   plano, incluida la API key en el header `X-API-Key`.

5. Si necesitan ver la interfaz de n8n desde otra máquina (no la del server),
   usar un túnel SSH en vez de abrir el puerto:
   ```
   ssh -L 5678:localhost:5678 usuario@servidor
   ```
   y entrar a `http://localhost:5678` desde su propia máquina.

**Nota sobre el alcance real de `API_KEY`:** el frontend manda esta key en
cada llamada al backend, incluidas las que hace el navegador directamente
(vía `NEXT_PUBLIC_API_KEY`) — esa variable SÍ queda visible para quien
inspeccione el código del sitio en su navegador. La key no esconde el
backend de alguien que ya usa la app; su trabajo es bloquear que cualquiera
en internet encuentre el puerto abierto y empiece a leer/crear/borrar datos
sin ni siquiera abrir el sitio. Para dos personas usando su propia
herramienta, es una mejora real y proporcionada — no es el nivel de un
producto multi-usuario público.
