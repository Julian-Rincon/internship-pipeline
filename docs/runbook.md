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
