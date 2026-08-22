# La VM de Oracle Cloud (500MB RAM) no alcanza a correr `npm run build` --
# el build de produccion se hace en local y se copia el resultado. Ver
# docs/runbook.md "Deploy en Oracle Cloud" para el proceso completo.
#
# Este Dockerfile solo empaqueta el output ya construido de
# `.next/standalone` (con `.next/static` copiado adentro) en
# frontend/prebuilt/ -- no compila nada.
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production
COPY prebuilt/ ./
EXPOSE 3000
CMD ["node", "server.js"]
