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

## Autenticación (actualizado 2026-07-06 — JWT por persona)

El equipo pasó de 2 a ~5-6 personas, así que se reemplazó la key compartida
única por un modelo de dos niveles:

- **JWT por persona** — cada quien tiene su propia cuenta (nombre, email,
  password) y entra por `/login` en el frontend. El navegador manda el token
  de ESA persona (`Authorization: Bearer ...`), no un secreto compartido.
  Los tokens duran `JWT_EXPIRES_SECONDS` (7 días por defecto) y se guardan en
  `localStorage` del navegador — si expira o es inválido, la app rebota sola
  a `/login`.
- **`API_KEY` de sistema** (header `X-API-Key`) — para llamadas que NO son de
  una persona: los workflows de n8n y el renderizado del lado del servidor
  del frontend. Se sigue usando exactamente igual que antes.
- **Roles**: solo cuentas con `role=admin` pueden crear (`POST /users`) o
  borrar (`DELETE /users/{id}`) cuentas de otras personas. Cualquier persona
  logueada (member o admin) puede usar el resto de la app normalmente — es
  una herramienta de equipo compartida, no un sistema con datos privados por
  usuario.

### Crear la primera cuenta admin (bootstrap)

No hay una pantalla de "primer arranque" — la primera cuenta admin se crea
con `API_KEY` directamente (funciona igual en Windows o Linux, solo necesita
`curl` o Postman/Insomnia si prefieren algo visual):

```bash
curl -X POST http://localhost:8000/users \
  -H "X-API-Key: TU_API_KEY_REAL" \
  -H "Content-Type: application/json" \
  -d '{"name":"Tu Nombre","email":"tu@email.com","role":"admin","password":"una-contraseña-de-verdad"}'
```

Con esa cuenta, entren a `/login` en el frontend — desde ahí ya pueden crear
al resto del equipo (`POST /users` autenticado como admin, o directamente
desde la página `/users` del frontend una vez logueados).

## Checklist de seguridad ANTES de desplegar en un servidor real (2026-07-06)

Esto ya no es "esta fase local" — es para quien vaya a correr `docker compose up`
en una máquina con IP pública (Windows o Linux, docker compose funciona igual
en ambos). Auditoría de seguridad hecha 2026-07-05 encontró 63 endpoints sin
ninguna autenticación, Postgres/Redis/n8n expuestos a toda la red, y passwords
en el valor literal `change-me-local-only`. Ya se arregló en código (ver
commits correspondientes); esto es lo que falta hacer AL MOMENTO DEL DEPLOY:

1. **Generar secretos reales** — uno distinto por cada valor, con:
   ```
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Reemplazar en `.env` (nunca en `.env.example`, ni commitear `.env`):
   - `API_KEY` (llamadas de sistema: n8n, server-side rendering)
   - `JWT_SECRET` (firma los tokens de login de cada persona — si alguien
     lo adivinara podría forjar tokens; debe ser aleatorio y real)
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
   plano, incluido el JWT y la API key.

5. Si necesitan ver la interfaz de n8n desde otra máquina (no la del server),
   usar un túnel SSH en vez de abrir el puerto:
   ```
   ssh -L 5678:localhost:5678 usuario@servidor
   ```
   y entrar a `http://localhost:5678` desde su propia máquina.

6. Correr la migración nueva al desplegar (agrega la columna de contraseña):
   ```
   docker compose exec backend alembic upgrade head
   ```
