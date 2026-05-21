import React, { useState, useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import {
  Stethoscope,
  AlertTriangle,
  Compass,
  MessageSquare,
  Sparkles,
  Send,
  Loader2,
  CircleAlert,
  Printer,
  RotateCcw,
  Activity,
} from "lucide-react";

const AGENT_ICONS = {
  ddx: Stethoscope,
  redflag: AlertTriangle,
  specialist: Compass,
  questions: MessageSquare,
  synth: Sparkles,
};

const AGENT_COLORS = {
  ddx: "text-sky-300 border-sky-500/40 bg-sky-500/5",
  redflag: "text-rose-300 border-rose-500/40 bg-rose-500/5",
  specialist: "text-amber-300 border-amber-500/40 bg-amber-500/5",
  questions: "text-violet-300 border-violet-500/40 bg-violet-500/5",
  synth: "text-emerald-300 border-emerald-500/40 bg-emerald-500/5",
};

const SEVERITY_BADGE = {
  EMERGENCY: "bg-rose-500/20 text-rose-200 border-rose-500/50",
  URGENT: "bg-amber-500/20 text-amber-200 border-amber-500/50",
  ROUTINE: "bg-sky-500/20 text-sky-200 border-sky-500/50",
  "SELF-CARE": "bg-emerald-500/20 text-emerald-200 border-emerald-500/50",
};

function Disclaimer() {
  return (
    <div className="bg-amber-500/10 border-y border-amber-500/30 text-amber-200 px-4 py-2 text-sm flex items-center gap-2">
      <CircleAlert className="w-4 h-4 shrink-0" />
      <span>
        SymptomReason is informational only — <strong>not a substitute for medical advice.</strong> If
        this is an emergency, call your local emergency services.
      </span>
    </div>
  );
}

function Header({ provider, model }) {
  return (
    <header className="border-b border-border bg-panel/60 backdrop-blur">
      <div className="max-w-6xl mx-auto px-6 py-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-emerald-400 to-sky-400 flex items-center justify-center text-bg font-bold">
            S
          </div>
          <div>
            <h1 className="font-semibold text-lg leading-tight">SymptomReason</h1>
            <p className="text-xs text-zinc-400">Multi-agent medical reasoning</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="px-2 py-1 rounded bg-panel2 border border-border text-zinc-400 font-mono">
            {provider || "—"}
          </span>
          <span className="px-2 py-1 rounded bg-panel2 border border-border text-zinc-400 font-mono">
            {model || "—"}
          </span>
        </div>
      </div>
    </header>
  );
}

function InputForm({ onSubmit, busy, examples }) {
  const [form, setForm] = useState({
    symptoms: "",
    age: "",
    sex: "",
    duration: "",
    context: "",
  });

  const update = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const fillExample = (ex) => setForm({ ...form, ...ex });

  const submit = (e) => {
    e.preventDefault();
    if (!form.symptoms.trim() || busy) return;
    onSubmit({
      ...form,
      age: form.age ? parseInt(form.age, 10) : null,
    });
  };

  return (
    <form onSubmit={submit} className="bg-panel border border-border rounded-xl p-5 space-y-4">
      <div>
        <label className="block text-xs uppercase tracking-wider text-zinc-400 mb-1.5">
          Describe what's happening
        </label>
        <textarea
          value={form.symptoms}
          onChange={(e) => update("symptoms", e.target.value)}
          rows={4}
          placeholder="e.g. Persistent dry cough for 3 weeks, mild shortness of breath when climbing stairs, no fever..."
          className="w-full bg-panel2 border border-border rounded-lg px-3 py-2.5 text-sm focus:outline-none focus:border-accent2/60 resize-none"
        />
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
        <input
          type="number"
          placeholder="Age"
          value={form.age}
          onChange={(e) => update("age", e.target.value)}
          className="bg-panel2 border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-accent2/60"
        />
        <input
          type="text"
          placeholder="Sex"
          value={form.sex}
          onChange={(e) => update("sex", e.target.value)}
          className="bg-panel2 border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-accent2/60"
        />
        <input
          type="text"
          placeholder="Duration"
          value={form.duration}
          onChange={(e) => update("duration", e.target.value)}
          className="bg-panel2 border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-accent2/60"
        />
        <input
          type="text"
          placeholder="Conditions / meds"
          value={form.context}
          onChange={(e) => update("context", e.target.value)}
          className="bg-panel2 border border-border rounded-lg px-3 py-2 text-sm focus:outline-none focus:border-accent2/60"
        />
      </div>

      {examples && examples.length > 0 && (
        <div className="flex flex-wrap gap-2 items-center">
          <span className="text-xs text-zinc-500">Try:</span>
          {examples.map((ex, i) => (
            <button
              key={i}
              type="button"
              onClick={() => fillExample(ex)}
              className="text-xs px-2.5 py-1 rounded-full bg-panel2 border border-border hover:border-accent/60 hover:text-accent transition"
            >
              {ex.title}
            </button>
          ))}
        </div>
      )}

      <button
        type="submit"
        disabled={busy || !form.symptoms.trim()}
        className="w-full bg-gradient-to-r from-emerald-500 to-sky-500 disabled:opacity-50 disabled:cursor-not-allowed text-bg font-semibold rounded-lg px-4 py-2.5 flex items-center justify-center gap-2 hover:brightness-110 transition"
      >
        {busy ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin" />
            Reasoning…
          </>
        ) : (
          <>
            <Send className="w-4 h-4" />
            Run consultation
          </>
        )}
      </button>
    </form>
  );
}

function AgentCard({ agent, state }) {
  const Icon = AGENT_ICONS[agent.id] || Activity;
  const color = AGENT_COLORS[agent.id] || "text-zinc-300 border-border bg-panel2";
  const status = state?.status || "idle";
  const text = state?.text || "";

  const statusLabel =
    status === "idle"
      ? "WAITING"
      : status === "running"
      ? "REASONING…"
      : status === "done"
      ? "DONE"
      : status === "error"
      ? "ERROR"
      : status.toUpperCase();

  return (
    <div className={`border ${color} rounded-xl p-4 transition`}>
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Icon className="w-4 h-4" />
          <h3 className="font-semibold text-sm">{agent.label}</h3>
        </div>
        <div className="flex items-center gap-2 text-[10px] font-mono uppercase tracking-wider">
          {status === "running" && <Loader2 className="w-3 h-3 animate-spin" />}
          <span className="text-zinc-400">{statusLabel}</span>
          {state?.elapsed_s && (
            <span className="text-zinc-500">{state.elapsed_s}s</span>
          )}
        </div>
      </div>
      <div className="markdown text-sm text-zinc-200 max-h-72 overflow-y-auto pr-2">
        {text ? (
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
        ) : (
          <p className="text-zinc-500 italic text-xs">Waiting for trigger…</p>
        )}
      </div>
    </div>
  );
}

function Severity({ text }) {
  // Try to extract severity from synth output
  const m = text.match(/(?:Severity at a glance|Severity)[:\s\n]*\n?\s*(?:\*\*)?(EMERGENCY|URGENT|ROUTINE|SELF-CARE)/i);
  const sev = m ? m[1].toUpperCase() : null;
  if (!sev) return null;
  const cls = SEVERITY_BADGE[sev] || "bg-zinc-500/20 text-zinc-200 border-zinc-500/50";
  return (
    <div className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${cls} text-xs font-mono uppercase tracking-wider`}>
      <Activity className="w-3.5 h-3.5" />
      {sev}
    </div>
  );
}

function FinalReport({ text, complete }) {
  if (!text) return null;
  return (
    <div className="bg-gradient-to-br from-emerald-500/5 to-sky-500/5 border border-emerald-500/30 rounded-xl p-5">
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-emerald-300" />
          <h2 className="font-semibold text-emerald-300">Synthesized Report</h2>
          {complete && <Severity text={text} />}
        </div>
        <button
          onClick={() => window.print()}
          className="text-xs px-2.5 py-1 rounded-md bg-panel2 border border-border hover:border-emerald-400/60 hover:text-emerald-300 transition flex items-center gap-1"
        >
          <Printer className="w-3 h-3" />
          Print prep sheet
        </button>
      </div>
      <div className="markdown text-zinc-100">
        <ReactMarkdown remarkPlugins={[remarkGfm]}>{text}</ReactMarkdown>
      </div>
    </div>
  );
}

function Stats({ stats }) {
  if (!stats) return null;
  return (
    <div className="flex flex-wrap items-center gap-2 text-xs">
      <span className="px-2 py-1 rounded bg-panel2 border border-border text-zinc-400 font-mono">
        agents: {stats.agents_completed}
      </span>
      <span className="px-2 py-1 rounded bg-panel2 border border-border text-zinc-400 font-mono">
        ~{stats.total_tokens_estimate.toLocaleString()} tokens
      </span>
    </div>
  );
}

export default function App() {
  const [config, setConfig] = useState({ provider: null, model: null });
  const [examples, setExamples] = useState([]);
  const [busy, setBusy] = useState(false);
  const [agents, setAgents] = useState({}); // id -> {status, text, elapsed_s}
  const [agentList, setAgentList] = useState([]);
  const [synth, setSynth] = useState({ status: "idle", text: "" });
  const [stats, setStats] = useState(null);
  const [error, setError] = useState(null);
  const abortRef = useRef(null);

  useEffect(() => {
    fetch("/api/config")
      .then((r) => r.json())
      .then(setConfig)
      .catch(() => {});
    fetch("/api/examples")
      .then((r) => r.json())
      .then(setExamples)
      .catch(() => {});
  }, []);

  const reset = () => {
    setAgents({});
    setSynth({ status: "idle", text: "" });
    setStats(null);
    setError(null);
  };

  const runConsult = async (input) => {
    reset();
    setBusy(true);
    abortRef.current = new AbortController();

    try {
      const resp = await fetch("/api/consult", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(input),
        signal: abortRef.current.signal,
      });

      if (!resp.ok || !resp.body) {
        throw new Error(`HTTP ${resp.status}`);
      }

      const reader = resp.body.getReader();
      const decoder = new TextDecoder();
      let buf = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });

        // Parse SSE blocks
        const blocks = buf.split("\n\n");
        buf = blocks.pop() || "";

        for (const block of blocks) {
          const lines = block.split("\n");
          let event = "message";
          let data = "";
          for (const ln of lines) {
            if (ln.startsWith("event: ")) event = ln.slice(7).trim();
            else if (ln.startsWith("data: ")) data += ln.slice(6);
          }
          if (!data) continue;
          let payload;
          try {
            payload = JSON.parse(data);
          } catch {
            continue;
          }
          handleEvent(event, payload);
        }
      }
    } catch (e) {
      if (e.name !== "AbortError") {
        setError(e.message || "Unknown error");
      }
    } finally {
      setBusy(false);
    }
  };

  const handleEvent = (event, payload) => {
    if (event === "pipeline_start") {
      setAgentList(payload.agents || []);
      setAgents(
        Object.fromEntries(
          (payload.agents || []).map((a) => [a.id, { status: "idle", text: "" }])
        )
      );
      return;
    }
    if (event === "phase") return;
    if (event === "start") {
      const id = payload.agent;
      if (id === "synth") {
        setSynth({ status: "running", text: "" });
      } else {
        setAgents((s) => ({ ...s, [id]: { ...(s[id] || {}), status: "running", text: "" } }));
      }
      return;
    }
    if (event === "token") {
      const id = payload.agent;
      if (id === "synth") {
        setSynth((s) => ({ ...s, text: (s.text || "") + payload.text }));
      } else {
        setAgents((s) => ({
          ...s,
          [id]: { ...(s[id] || {}), text: ((s[id] && s[id].text) || "") + payload.text },
        }));
      }
      return;
    }
    if (event === "done") {
      const id = payload.agent;
      if (id === "synth") {
        setSynth((s) => ({ ...s, status: "done", elapsed_s: payload.elapsed_s }));
      } else {
        setAgents((s) => ({
          ...s,
          [id]: { ...(s[id] || {}), status: "done", elapsed_s: payload.elapsed_s },
        }));
      }
      return;
    }
    if (event === "error") {
      if (payload.agent === "synth") {
        setSynth((s) => ({ ...s, status: "error", text: (s.text || "") + `\n\n_Error: ${payload.message}_` }));
      } else if (payload.agent) {
        setAgents((s) => ({
          ...s,
          [payload.agent]: { ...(s[payload.agent] || {}), status: "error" },
        }));
      } else {
        setError(payload.message || "pipeline error");
      }
      return;
    }
    if (event === "pipeline_complete") {
      setStats(payload);
      return;
    }
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header provider={config.provider} model={config.model} />
      <Disclaimer />

      <main className="flex-1 max-w-6xl mx-auto w-full px-6 py-6 space-y-6">
        <section className="grid lg:grid-cols-2 gap-6">
          <InputForm onSubmit={runConsult} busy={busy} examples={examples} />

          <div className="bg-panel border border-border rounded-xl p-5">
            <div className="flex items-center justify-between mb-3">
              <h2 className="font-semibold text-zinc-200">Pipeline</h2>
              <div className="flex items-center gap-2">
                <Stats stats={stats} />
                {!busy && (agentList.length > 0 || synth.text) && (
                  <button
                    onClick={reset}
                    className="text-xs px-2 py-1 rounded bg-panel2 border border-border hover:border-zinc-400 transition flex items-center gap-1"
                  >
                    <RotateCcw className="w-3 h-3" />
                    Clear
                  </button>
                )}
              </div>
            </div>
            <p className="text-xs text-zinc-500 leading-relaxed">
              4 specialist agents run in parallel via <code className="text-accent">asyncio.gather()</code>.
              A long-chain synthesizer combines their reasoning into a final report.
              All output streams via Server-Sent Events.
            </p>
            <div className="mt-3 grid grid-cols-2 gap-2 text-[11px] font-mono text-zinc-400">
              <div className="px-2 py-1 rounded bg-panel2 border border-border">
                Phase 1: parallel reasoning
              </div>
              <div className="px-2 py-1 rounded bg-panel2 border border-border">
                Phase 2: long-chain synth
              </div>
            </div>
          </div>
        </section>

        {error && (
          <div className="bg-rose-500/10 border border-rose-500/30 text-rose-200 rounded-lg px-4 py-3 text-sm">
            <strong>Error:</strong> {error}
          </div>
        )}

        {agentList.length > 0 && (
          <section>
            <h2 className="text-sm uppercase tracking-wider text-zinc-400 mb-3">
              Phase 1 — Parallel agents
            </h2>
            <div className="grid md:grid-cols-2 gap-4">
              {agentList.map((a) => (
                <AgentCard key={a.id} agent={a} state={agents[a.id]} />
              ))}
            </div>
          </section>
        )}

        {(synth.status !== "idle" || synth.text) && (
          <section>
            <h2 className="text-sm uppercase tracking-wider text-zinc-400 mb-3">
              Phase 2 — Synthesis
            </h2>
            <FinalReport text={synth.text} complete={synth.status === "done"} />
          </section>
        )}

        <footer className="text-center text-xs text-zinc-500 pt-8 pb-4">
          Built for medical preparedness. Not a substitute for a clinician.
          {" · "}
          <a
            href="https://github.com/zerone516/symptom-reason"
            target="_blank"
            rel="noreferrer"
            className="hover:text-accent"
          >
            GitHub
          </a>
        </footer>
      </main>
    </div>
  );
}
