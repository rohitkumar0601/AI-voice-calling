import { useEffect, useRef, useState } from "react";
import Vapi from "@vapi-ai/web";

const PUBLIC_KEY = import.meta.env.VITE_VAPI_PUBLIC_KEY;
const ASSISTANT_ID = import.meta.env.VITE_VAPI_ASSISTANT_ID;

export default function VoiceAgent({ onCallEnd }) {
  const vapiRef = useRef(null);
  const [status, setStatus] = useState("idle"); // idle | connecting | live | error
  const [assistantSpeaking, setAssistantSpeaking] = useState(false);
  const [turns, setTurns] = useState([]);
  const [partial, setPartial] = useState(null);

  useEffect(() => {
    if (!PUBLIC_KEY) return; // no key yet -> button stays disabled
    const vapi = new Vapi(PUBLIC_KEY);
    vapiRef.current = vapi;

    vapi.on("call-start", () => setStatus("live"));
    vapi.on("call-end", () => {
      setStatus("idle");
      setAssistantSpeaking(false);
      setPartial(null);
      onCallEnd?.(); // refresh dashboard after a call
    });
    vapi.on("speech-start", () => setAssistantSpeaking(true));
    vapi.on("speech-end", () => setAssistantSpeaking(false));
    vapi.on("error", (e) => {
      console.error("Vapi error:", e);
      setStatus("error");
    });
    vapi.on("message", (m) => {
      if (m.type !== "transcript") return;
      if (m.transcriptType === "final") {
        setTurns((t) => [...t, { role: m.role, text: m.transcript }]);
        setPartial(null);
      } else {
        setPartial({ role: m.role, text: m.transcript });
      }
    });

    return () => vapi.stop();
  }, [onCallEnd]);

  const toggle = () => {
    const vapi = vapiRef.current;
    if (!vapi) return;
    if (status === "live" || status === "connecting") {
      vapi.stop();
    } else {
      setTurns([]);
      setStatus("connecting");
      vapi.start(ASSISTANT_ID);
    }
  };

  const live = status === "live";
  const visible = [...turns, ...(partial ? [partial] : [])];
  const configured = Boolean(PUBLIC_KEY && ASSISTANT_ID);

  return (
    <div className="voice">
      <div className="voice-head">
        <button
          className={`mic ${live ? "mic-live" : ""}`}
          onClick={toggle}
          disabled={!configured}
          aria-label={live ? "End call" : "Start voice call"}
        >
          <span className="mic-dot" />
          {live ? "End call" : status === "connecting" ? "Connecting…" : "Talk to CRM"}
        </button>
        <span className={`pill pill-${status}`}>
          {status === "live" ? (assistantSpeaking ? "assistant speaking" : "listening") : status}
        </span>
      </div>

      {!configured && (
        <p className="hint">
          Set <code>VITE_VAPI_PUBLIC_KEY</code> and <code>VITE_VAPI_ASSISTANT_ID</code> in{" "}
          <code>.env</code> to enable the mic.
        </p>
      )}

      {visible.length > 0 && (
        <div className="transcript">
          {visible.map((t, i) => (
            <div key={i} className={`bubble ${t.role === "assistant" ? "bot" : "you"}`}>
              <span className="who">{t.role === "assistant" ? "CRM" : "You"}</span>
              {t.text}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
