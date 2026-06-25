export const dynamic = "force-dynamic";
export default async function OutreachPage() {
  return (
    <section>
      <h1>Outreach</h1>
      <p className="muted">Log de outreach enviado. Límite: 20 mensajes/día por usuario.</p>
      <div className="panel" style={{ marginTop: 16 }}>
        <h2>Outreach log</h2>
        <p className="muted">Los mensajes enviados aparecerán aquí con su estado.</p>
      </div>
    </section>
  );
}
