import { useCallback, useEffect, useState } from "react";
import { api, fmtMoney } from "./api.js";
import VoiceAgent from "./VoiceAgent.jsx";

const STAGE_ORDER = ["Prospecting", "Qualification", "Proposal", "Negotiation"];

export default function App() {
  const [deals, setDeals] = useState([]);
  const [contacts, setContacts] = useState([]);
  const [pipeline, setPipeline] = useState(null);
  const [err, setErr] = useState(null);

  const load = useCallback(() => {
    Promise.all([api.deals(), api.contacts(), api.pipeline()])
      .then(([d, c, p]) => {
        setDeals(d);
        setContacts(c);
        setPipeline(p);
        setErr(null);
      })
      .catch((e) => setErr(e.message));
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="app">
      <header className="topbar">
        <div>
          <div className="eyebrow">Sales desk</div>
          <h1>Atlas CRM</h1>
        </div>
        <VoiceAgent onCallEnd={load} />
      </header>

      {err && (
        <div className="error">
          Couldn’t reach the backend ({err}). Is the API running on port 8000?
        </div>
      )}

      {pipeline && (
        <section>
          <h2>Pipeline</h2>
          <div className="stage-grid">
            {STAGE_ORDER.map((s) => {
              const cell = pipeline.by_stage[s] || { count: 0, amount: 0 };
              return (
                <div className="stage-card" key={s}>
                  <div className="stage-name">{s}</div>
                  <div className="stage-amount">{fmtMoney(cell.amount)}</div>
                  <div className="stage-count">
                    {cell.count} deal{cell.count === 1 ? "" : "s"}
                  </div>
                </div>
              );
            })}
          </div>
          <div className="forecast">
            <span>Open total <strong>{fmtMoney(pipeline.open_total)}</strong></span>
            <span>Weighted forecast <strong>{fmtMoney(pipeline.weighted_forecast)}</strong></span>
          </div>
        </section>
      )}

      <section>
        <h2>Deals</h2>
        <table className="grid">
          <thead>
            <tr><th>Deal</th><th>Account</th><th>Stage</th><th className="num">Amount</th><th>Owner</th></tr>
          </thead>
          <tbody>
            {deals.map((d) => (
              <tr key={d.id}>
                <td>{d.name}</td>
                <td className="muted">{d.account}</td>
                <td><span className={`stage-tag s-${d.stage.replace(/\s/g, "")}`}>{d.stage}</span></td>
                <td className="num mono">{fmtMoney(d.amount)}</td>
                <td className="muted">{d.owner}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <section>
        <h2>Contacts</h2>
        <table className="grid">
          <thead>
            <tr><th>Name</th><th>Title</th><th>Account</th><th>Phone</th></tr>
          </thead>
          <tbody>
            {contacts.map((c) => (
              <tr key={c.id}>
                <td>{c.name}</td>
                <td className="muted">{c.title}</td>
                <td className="muted">{c.account}</td>
                <td className="mono muted">{c.phone}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>

      <footer className="foot">
        Try saying: “What’s the status of the Northwind fleet deal?” · “Give me the pipeline summary.”
        · “Who is Maria Alvarez?”
      </footer>
    </div>
  );
}
