import { useState } from "react";
import "./App.css";

const SpeechRecognition =
  window.SpeechRecognition || window.webkitSpeechRecognition;

function speak(text) {
  if (!("speechSynthesis" in window)) return;
  window.speechSynthesis.cancel();
  const u = new SpeechSynthesisUtterance(text);
  u.lang = "hi-IN";
  u.rate = 0.9;
  window.speechSynthesis.speak(u);
}
const API_URL = "https://scamshield-x9s4.onrender.com/check";
const REPORT_URL = "https://scamshield-x9s4.onrender.com/report";
function getDeviceId() {
  let id = localStorage.getItem("scamshield_device_id");
  if (!id) {
    id = "dev_" + Date.now() + "_" + Math.random().toString(36).slice(2, 12);
    localStorage.setItem("scamshield_device_id", id);
  }
  return id;
}
const TABS = [
  { id: "message", label: "मैसेज", hint: "जो मैसेज आया है उसे यहाँ paste करें" },
  { id: "url", label: "लिंक", hint: "जो link आया है उसे यहाँ paste करें" },
  { id: "number", label: "नंबर", hint: "जिस नंबर से call आई उसे लिखें" },
];

const VERDICTS = {
  safe: { title: "सुरक्षित लगता है", emoji: "✅", cls: "safe" },
  suspicious: { title: "सावधान रहें, संदिग्ध है", emoji: "⚠️", cls: "suspicious" },
  dangerous: { title: "खतरा! यह scam है", emoji: "🚫", cls: "dangerous" },
};

export default function App() {
  const [tab, setTab] = useState("message");
  const [content, setContent] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [listening, setListening] = useState(false);
  const [reportStatus, setReportStatus] = useState(null);

  function startListening() {
    if (!SpeechRecognition) {
      setError("इस browser में बोलकर लिखना काम नहीं करता। Chrome इस्तेमाल करें।");
      return;
    }
    const rec = new SpeechRecognition();
    rec.lang = "hi-IN";
    rec.interimResults = false;
    rec.onstart = () => setListening(true);
    rec.onend = () => setListening(false);
    rec.onerror = () => setListening(false);
    rec.onresult = (e) => {
      const text = e.results[0][0].transcript;
      setContent((prev) => (prev ? prev + " " : "") + text);
    };
    rec.start();
  }

  function speakResult() {
    if (!result) return;
    const parts = [VERDICTS[result.verdict].title, result.explanation, result.advice];
    speak(parts.filter(Boolean).join(". "));
  }

  async function handleReport() {
    if (!result || !content.trim()) return;
    setReportStatus("sending");
    try {
      const res = await fetch(REPORT_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          report_type: tab,
          content,
          device_id: getDeviceId(),
        }),
      });
      if (!res.ok) throw new Error();
      await res.json();
      setReportStatus("done");
    } catch {
      setReportStatus("error");
    }
  }
  const current = TABS.find((t) => t.id === tab);

  async function handleCheck() {
    if (!content.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    setReportStatus(null);
    try {
      const res = await fetch(API_URL, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ input_type: tab, content }),
      });
      if (!res.ok) throw new Error("Server error " + res.status);
      setResult(await res.json());
    } catch (e) {
      setError("जाँच नहीं हो पाई। कृपया दोबारा कोशिश करें।");
    } finally {
      setLoading(false);
    }
  }

  function switchTab(id) {
    setTab(id);
    setContent("");
    setResult(null);
    setError("");
    setReportStatus(null);
  }

  const v = result ? VERDICTS[result.verdict] : null;

  return (
    <div className="app">
      <h1>🛡️ ScamShield</h1>
      <p className="subtitle">कोई भी call, link या message जाँचें, scam से बचें</p>

      <div className="tabs">
        {TABS.map((t) => (
          <button
            key={t.id}
            className={"tab" + (tab === t.id ? " active" : "")}
            onClick={() => switchTab(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "message" ? (
        <textarea
          rows={5}
          value={content}
          placeholder={current.hint}
          onChange={(e) => setContent(e.target.value)}
        />
      ) : (
        <input
          type="text"
          value={content}
          placeholder={current.hint}
          onChange={(e) => setContent(e.target.value)}
        />
      )}

      <button
        className={"mic-btn" + (listening ? " on" : "")}
        onClick={startListening}
        type="button"
      >
        {listening ? "🎙️ सुन रहा हूँ..." : "🎤 बोलकर लिखें"}
      </button>

      <button className="check-btn" onClick={handleCheck} disabled={loading || !content.trim()}>
        {loading ? "जाँच हो रही है..." : "जाँचें"}
      </button>

      {error && <p className="error">{error}</p>}

      {v && (
        <div className={"result " + v.cls}>
          <h2>
            {v.emoji} {v.title}
          </h2>
          {result.explanation && <p className="explain">{result.explanation}</p>}
          {result.advice && (
            <p className="advice">
              <strong>क्या करें:</strong> {result.advice}
            </p>
          )}
          {result.reasons.length > 0 && (
            <ul>
              {result.reasons.map((r, i) => (
                <li key={i}>{r}</li>
              ))}
            </ul>
          )}

          <button className="listen-btn" onClick={speakResult} type="button">
            🔊 सुनें
          </button>

          {(result.verdict === "suspicious" || result.verdict === "dangerous") && (
            <div className="report-box">
              {reportStatus === "done" ? (
                <p className="report-done">✅ धन्यवाद, आपकी report मिल गई है।</p>
              ) : (
                <button
                  className="report-btn"
                  onClick={handleReport}
                  disabled={reportStatus === "sending"}
                  type="button"
                >
                  {reportStatus === "sending" ? "भेजा जा रहा है..." : "🚩 यह scam है, report करें"}
                </button>
              )}
              {reportStatus === "error" && (
                <p className="error">Report नहीं भेज पाए, दोबारा कोशिश करें।</p>
              )}
            </div>
          )}

          <p className="score">जोखिम स्तर: {result.score}/100</p>
        </div>
      )}
    </div>
  );
}