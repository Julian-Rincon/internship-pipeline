export const dynamic = "force-dynamic";
export default async function TemplatesPage() {
  return (
    <section>
      <h1>Outreach Templates</h1>
      <p className="muted">Plantillas de mensajes para outreach personalizado. Variables: {"{company_name}"}, {"{contact_name}"}, {"{user_name}"}, {"{user_skills}"}.</p>
      <div className="panel" style={{ marginTop: 16 }}>
        <h2>Templates disponibles</h2>
        <p className="muted">Crea templates para intro, followup e informational outreach.</p>
      </div>
    </section>
  );
}
