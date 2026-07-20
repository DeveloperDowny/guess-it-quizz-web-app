import { useEffect, useMemo, useState } from "react";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";
const SESSION_KEY = "quizz.sessionId";
const PLAYER_KEY = "quizz.playerId";

async function api(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers ?? {}) },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail ?? "The request could not be completed.");
  return payload;
}

function Shell({ children }) {
  return <main className="min-h-screen bg-slate-100 px-4 py-8 text-slate-900 sm:px-8">
    <div className="mx-auto max-w-3xl">{children}</div>
  </main>;
}

function ErrorMessage({ error }) {
  return error ? <p role="alert" className="rounded-lg bg-red-50 p-3 text-sm text-red-700">{error}</p> : null;
}

function StartView({ onReady }) {
  const [sets, setSets] = useState([]);
  const [mode, setMode] = useState("create");
  const [playerId, setPlayerId] = useState("");
  const [sessionId, setSessionId] = useState("");
  const [questionSetId, setQuestionSetId] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { api("/api/question-sets").then((data) => {
    setSets(data.question_sets ?? []);
    setQuestionSetId(data.question_sets?.[0] ?? "");
  }).catch((err) => setError(err.message)); }, []);

  async function submit(event) {
    event.preventDefault(); setError(""); setBusy(true);
    try {
      if (!playerId.trim()) throw new Error("Enter a display name to continue.");
      let id = sessionId.trim();
      if (mode === "create") {
        if (!questionSetId) throw new Error("No question sets are available yet.");
        const created = await api("/api/sessions", { method: "POST", body: JSON.stringify({ question_set_id: questionSetId, created_by: playerId.trim() }) });
        id = created.session_id;
      } else {
        if (!id) throw new Error("Enter the session ID shared by player 1.");
        await api(`/api/sessions/${encodeURIComponent(id)}/join`, { method: "POST", body: JSON.stringify({ joined_by: playerId.trim() }) });
      }
      sessionStorage.setItem(SESSION_KEY, id); sessionStorage.setItem(PLAYER_KEY, playerId.trim());
      onReady(id, playerId.trim());
    } catch (err) { setError(err.message); } finally { setBusy(false); }
  }

  return <Shell>
    <header className="mb-8"><p className="mb-2 text-sm font-semibold uppercase tracking-[0.3em] text-sky-700">Browser quiz</p><h1 className="text-4xl font-bold tracking-tight">Play as yourself. Think like someone else.</h1><p className="mt-3 text-slate-600">Create a room or join one with a shared session ID. No account required.</p></header>
    <section className="rounded-2xl bg-white p-6 shadow-sm sm:p-8">
      <div className="mb-6 flex gap-2 rounded-lg bg-slate-100 p-1"><button type="button" onClick={() => setMode("create")} className={`flex-1 rounded-md px-4 py-2 text-sm font-semibold ${mode === "create" ? "bg-white shadow-sm" : "text-slate-500"}`}>Create session</button><button type="button" onClick={() => setMode("join")} className={`flex-1 rounded-md px-4 py-2 text-sm font-semibold ${mode === "join" ? "bg-white shadow-sm" : "text-slate-500"}`}>Join session</button></div>
      <form onSubmit={submit} className="space-y-5">
        <label className="block text-sm font-semibold">Your display name<input value={playerId} onChange={(e) => setPlayerId(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 font-normal outline-none focus:border-sky-600" placeholder="e.g. Alex" /></label>
        {mode === "create" ? <label className="block text-sm font-semibold">Question set<select value={questionSetId} onChange={(e) => setQuestionSetId(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 bg-white px-3 py-2 font-normal"><option value="">Select a question set</option>{sets.map((id) => <option key={id} value={id}>{id}</option>)}</select></label> : <label className="block text-sm font-semibold">Session ID<input value={sessionId} onChange={(e) => setSessionId(e.target.value)} className="mt-2 w-full rounded-lg border border-slate-300 px-3 py-2 font-normal" placeholder="Paste the session ID" /></label>}
        <ErrorMessage error={error} /><button disabled={busy} className="w-full rounded-lg bg-sky-700 px-4 py-3 font-semibold text-white transition hover:bg-sky-800 disabled:cursor-wait disabled:opacity-60">{busy ? "Connecting…" : mode === "create" ? "Create room" : "Join room"}</button>
      </form>
    </section>
  </Shell>;
}

function PlayerView({ sessionId, playerId, onExit }) {
  const [questions, setQuestions] = useState([]); const [session, setSession] = useState(null); const [perspective, setPerspective] = useState("self"); const [answers, setAnswers] = useState({ self: {}, impersonation: {} }); const [error, setError] = useState(""); const [busy, setBusy] = useState(false); const [saved, setSaved] = useState(0); const [showJudge, setShowJudge] = useState(false);
  useEffect(() => { Promise.all([api(`/api/sessions/${encodeURIComponent(sessionId)}`), api(`/api/sessions/${encodeURIComponent(sessionId)}/questions`)]).then(([state, data]) => { setSession(state); setQuestions(data.questions ?? []); const stored = state.data?.answers?.[playerId] ?? {}; setAnswers({ self: stored.self ?? {}, impersonation: stored.impersonation ?? {} }); }).catch((err) => setError(err.message)); }, [sessionId, playerId]);
  const completed = useMemo(() => questions.length > 0 && ["self", "impersonation"].every((kind) => questions.every((q) => answers[kind][q.id] || answers[kind][String(q.id)])), [answers, questions]);
  async function choose(question, answer) { setError(""); setBusy(true); try { await api(`/api/sessions/${encodeURIComponent(sessionId)}/answers`, { method: "POST", body: JSON.stringify({ question_id: question.id, answer, player_id: playerId, perspective }) }); setAnswers((current) => ({ ...current, [perspective]: { ...current[perspective], [question.id]: answer } })); setSaved((count) => count + 1); } catch (err) { setError(err.message); } finally { setBusy(false); } }
  async function complete() { setError(""); setBusy(true); try { await api(`/api/sessions/${encodeURIComponent(sessionId)}/complete`, { method: "POST" }); setShowJudge(true); } catch (err) { setError(err.message); } finally { setBusy(false); } }
  if (showJudge) return <JudgeView sessionId={sessionId} onExit={onExit} />;
  return <Shell><header className="mb-6 flex flex-wrap items-start justify-between gap-4"><div><p className="text-sm font-semibold uppercase tracking-[0.25em] text-sky-700">Session room</p><h1 className="mt-1 text-3xl font-bold">{sessionId}</h1><p className="mt-1 text-sm text-slate-600">{session?.joined_by ? "Both players are connected." : "Share this ID with player 2."}</p></div><button onClick={onExit} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold">Leave</button></header>
    <section className="mb-5 rounded-2xl bg-white p-4 shadow-sm"><div className="flex gap-2"><button onClick={() => setPerspective("self")} className={`flex-1 rounded-lg px-3 py-3 text-sm font-semibold ${perspective === "self" ? "bg-sky-700 text-white" : "bg-slate-100"}`}>My answers</button><button onClick={() => setPerspective("impersonation")} className={`flex-1 rounded-lg px-3 py-3 text-sm font-semibold ${perspective === "impersonation" ? "bg-sky-700 text-white" : "bg-slate-100"}`}>Impersonation answers</button></div><p className="mt-3 text-sm text-slate-600">Choose one option for every question as {perspective === "self" ? "yourself" : "the person you are impersonating"}.</p></section>
    <ErrorMessage error={error} /><div className="mt-5 space-y-4">{questions.map((question, index) => <article key={question.id} className="rounded-2xl bg-white p-5 shadow-sm"><p className="text-sm font-semibold text-slate-500">Question {index + 1}</p><h2 className="mt-1 text-lg font-semibold">{question.question}</h2><div className="mt-4 grid gap-2 sm:grid-cols-2">{question.options.map((option) => { const selected = answers[perspective][question.id] === option || answers[perspective][String(question.id)] === option; return <button key={option} disabled={busy} onClick={() => choose(question, option)} className={`rounded-lg border px-4 py-3 text-left text-sm transition ${selected ? "border-sky-700 bg-sky-50 text-sky-900" : "border-slate-200 hover:border-sky-400"}`}>{option}</button>; })}</div></article>)}</div>
    <footer className="mt-6 flex flex-wrap items-center justify-between gap-3 rounded-xl bg-slate-800 p-4 text-sm text-white"><span>{saved} answer{saved === 1 ? "" : "s"} saved this visit.{completed && <span className="ml-2 text-emerald-300">Both perspectives are complete.</span>}</span>{completed && <button disabled={busy} onClick={complete} className="rounded-lg bg-emerald-400 px-3 py-2 font-semibold text-slate-900 disabled:opacity-60">Finish and review</button>}</footer>
  </Shell>;
}

function JudgeView({ sessionId, onExit }) {
  const [results, setResults] = useState([]); const [error, setError] = useState("");
  useEffect(() => { api(`/api/sessions/${encodeURIComponent(sessionId)}/judge`).then((data) => setResults(data.results ?? [])).catch((err) => setError(err.message)); }, [sessionId]);
  return <Shell><header className="mb-6 flex flex-wrap items-start justify-between gap-4"><div><p className="text-sm font-semibold uppercase tracking-[0.25em] text-sky-700">Judge review</p><h1 className="mt-1 text-3xl font-bold">Session results</h1><p className="mt-1 text-sm text-slate-600">{sessionId}</p></div><button onClick={onExit} className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm font-semibold">Leave</button></header><ErrorMessage error={error} /><div className="space-y-5">{results.map((result) => <section key={result.player_name} className="rounded-2xl bg-white p-5 shadow-sm"><div className="flex flex-wrap items-baseline justify-between gap-3"><div><h2 className="text-xl font-bold">{result.player_name} impersonating {result.target_name}</h2><p className="text-sm text-slate-600">Exact matches by question</p></div><p className="text-2xl font-bold text-sky-700">{result.matched_answers} / {result.total_questions}</p></div><div className="mt-4 space-y-2">{result.reviews.map((review) => <div key={review.question_id} className={`rounded-lg border p-3 ${review.is_match ? "border-emerald-200 bg-emerald-50" : "border-red-200 bg-red-50"}`}><div className="flex gap-3"><span aria-label={review.is_match ? "Match" : "Miss"} className="text-lg">{review.is_match ? "✓" : "×"}</span><div><p className="font-semibold">{review.question}</p><p className="mt-1 text-sm text-slate-600">Guessed: {review.guessed_answer || "No answer"} · Correct: {review.correct_answer || "No answer"}</p></div></div></div>)}</div></section>)}</div></Shell>;
}

export default function App() {
  const [identity, setIdentity] = useState(() => ({ sessionId: sessionStorage.getItem(SESSION_KEY), playerId: sessionStorage.getItem(PLAYER_KEY) }));
  function exit() { sessionStorage.removeItem(SESSION_KEY); sessionStorage.removeItem(PLAYER_KEY); setIdentity({ sessionId: null, playerId: null }); }
  return identity.sessionId && identity.playerId ? <PlayerView sessionId={identity.sessionId} playerId={identity.playerId} onExit={exit} /> : <StartView onReady={(sessionId, playerId) => setIdentity({ sessionId, playerId })} />;
}
