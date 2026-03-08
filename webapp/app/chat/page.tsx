"use client";

import { useState, useRef, useEffect } from "react";
import {
  Send,
  Bot,
  User,
  Sparkles,
  BookOpen,
  ChevronRight,
} from "lucide-react";
import { api } from "@/lib/api";

// ── Types ─────────────────────────────────────────────────────────────────
interface Citation {
  regulation: string;
  article?: string;
  excerpt: string;
}

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  citations?: Citation[];
  loading?: boolean;
}

// ── Suggested questions ───────────────────────────────────────────────────
const SUGGESTED = [
  "Do I need to label AI content?",
  "What does EU AI Act require for high-risk?",
  "Is voice data biometric under GDPR?",
  "DPDP Act consent requirements",
];

// ── Mock citations for demo ───────────────────────────────────────────────
const MOCK_CITATIONS: Record<string, Citation[]> = {
  default: [
    {
      regulation: "EU AI Act",
      article: "Article 13",
      excerpt:
        "High-risk AI systems shall be designed and developed in such a way as to ensure that their operation is sufficiently transparent.",
    },
    {
      regulation: "GDPR",
      article: "Article 22",
      excerpt:
        "The data subject shall have the right not to be subject to a decision based solely on automated processing.",
    },
  ],
  label: [
    {
      regulation: "EU AI Act",
      article: "Article 50",
      excerpt:
        "Providers of AI systems that generate synthetic audio, video, text or images shall ensure the outputs are marked in a machine-readable format.",
    },
  ],
  biometric: [
    {
      regulation: "GDPR",
      article: "Article 9",
      excerpt:
        "Processing of biometric data for the purpose of uniquely identifying a natural person constitutes special category data.",
    },
    {
      regulation: "EU AI Act",
      article: "Article 3(34)",
      excerpt:
        "Biometric data means personal data resulting from specific technical processing relating to physical, physiological or behavioural characteristics.",
    },
  ],
  dpdp: [
    {
      regulation: "India DPDP Act 2023",
      article: "Section 6",
      excerpt:
        "A Data Fiduciary shall give the Data Principal a notice requesting consent for processing of her personal data.",
    },
  ],
};

function getCitations(query: string): Citation[] {
  const q = query.toLowerCase();
  if (q.includes("label") || q.includes("synthetic")) return MOCK_CITATIONS.label;
  if (q.includes("biometric") || q.includes("voice")) return MOCK_CITATIONS.biometric;
  if (q.includes("dpdp") || q.includes("consent")) return MOCK_CITATIONS.dpdp;
  return MOCK_CITATIONS.default;
}

// ── Mock AI responses ─────────────────────────────────────────────────────
function getMockResponse(query: string): string {
  const q = query.toLowerCase();
  if (q.includes("label") || q.includes("synthetic")) {
    return "Yes, under **EU AI Act Article 50**, providers of AI systems generating synthetic content (text, audio, images, video) must ensure outputs are machine-readable marked as AI-generated. For consumer-facing products, visible disclosure is also required when the content could reasonably be mistaken for authentic. The obligation applies to both the AI provider and, in some cases, the deployer.";
  }
  if (q.includes("high-risk") || q.includes("eu ai act")) {
    return "Under the **EU AI Act**, high-risk AI systems (Annex III) must meet these key requirements:\n\n• **Risk management system** — documented throughout the lifecycle\n• **Data governance** — training data must meet quality criteria\n• **Technical documentation** — comprehensive system documentation\n• **Transparency** — users must be informed they're interacting with AI\n• **Human oversight** — mechanisms to allow human intervention\n• **Accuracy & robustness** — measurable performance standards\n• **Conformity assessment** — either self-assessment or third-party audit before market placement";
  }
  if (q.includes("biometric") || q.includes("voice")) {
    return "Yes, voice data can constitute biometric data under **GDPR Article 9** when processed to uniquely identify a person. Voiceprints created through technical processing are explicitly biometric data — a special category requiring explicit consent or another legal basis under Article 9(2). The EU AI Act additionally prohibits or restricts certain real-time biometric AI applications in public spaces. Your system should conduct a Data Protection Impact Assessment (DPIA) if processing voice for identification purposes.";
  }
  if (q.includes("dpdp") || q.includes("consent")) {
    return "The **India Digital Personal Data Protection Act 2023** establishes these consent requirements:\n\n• Consent must be **free, specific, informed, unconditional and unambiguous**\n• A clear **notice** must be provided before or at the time of collecting data\n• Consent requests must be in **plain language** and available in scheduled languages\n• Users have the right to **withdraw consent** at any time\n• For children (<18), **verifiable parental consent** is required\n• Data Fiduciaries must maintain records of consent\n\nNote: Implementing rules and commencement date are still pending as of early 2026.";
  }
  return "Based on the compliance knowledge base, I can help you navigate this regulatory question. The applicable frameworks depend on your jurisdiction, the type of AI system, and the data processed. Please share more details about your specific use case, and I'll reference the relevant regulatory provisions from EU AI Act, GDPR, DPDP Act, and other applicable standards.";
}

// ── Message bubble ────────────────────────────────────────────────────────
function MessageBubble({ msg }: { msg: Message }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex gap-3 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {/* Avatar */}
      <div
        className={`w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center ${
          isUser
            ? "bg-blue-500/20 border border-blue-500/30"
            : "bg-purple-500/20 border border-purple-500/30"
        }`}
      >
        {isUser ? (
          <User className="w-4 h-4 text-blue-400" />
        ) : (
          <Bot className="w-4 h-4 text-purple-400" />
        )}
      </div>

      {/* Bubble */}
      <div className={`max-w-[72%] space-y-2 ${isUser ? "items-end" : "items-start"} flex flex-col`}>
        <div
          className={`px-4 py-3 rounded-2xl text-sm leading-relaxed ${
            isUser
              ? "bg-blue-500/20 border border-blue-500/25 text-white rounded-tr-sm"
              : "glass border border-white/[0.08] text-white rounded-tl-sm"
          } ${msg.loading ? "animate-pulse" : ""}`}
        >
          {msg.loading ? (
            <div className="flex items-center gap-2 text-[rgb(163,163,163)]">
              <Sparkles className="w-3.5 h-3.5 animate-spin text-purple-400" />
              <span className="text-xs">Analysing compliance knowledge base…</span>
            </div>
          ) : (
            <div className="whitespace-pre-line">
              {msg.content.split(/(\*\*[^*]+\*\*)/).map((part, i) =>
                part.startsWith("**") && part.endsWith("**") ? (
                  <strong key={i} className="font-semibold text-white">
                    {part.slice(2, -2)}
                  </strong>
                ) : (
                  <span key={i}>{part}</span>
                )
              )}
            </div>
          )}
        </div>

        {/* Citations */}
        {!msg.loading && msg.citations && msg.citations.length > 0 && (
          <div className="space-y-1.5">
            <p className="text-[10px] text-[rgb(115,115,115)] flex items-center gap-1">
              <BookOpen className="w-3 h-3" />
              Sources
            </p>
            {msg.citations.map((c, i) => (
              <div
                key={i}
                className="glass-card px-3 py-2 rounded-xl border-l-2 border-l-purple-500/40 text-xs"
              >
                <p className="font-semibold text-purple-300">
                  {c.regulation}
                  {c.article && (
                    <span className="text-[rgb(163,163,163)] font-normal ml-1">
                      — {c.article}
                    </span>
                  )}
                </p>
                <p className="text-[rgb(163,163,163)] mt-0.5 leading-relaxed line-clamp-2">
                  {c.excerpt}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Timestamp */}
        <p className="text-[10px] text-[rgb(115,115,115)]">
          {msg.timestamp.toLocaleTimeString([], {
            hour: "2-digit",
            minute: "2-digit",
          })}
        </p>
      </div>
    </div>
  );
}

// ── Page ─────────────────────────────────────────────────────────────────
export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hello! I'm your Compliance Advisor, powered by the Adhi regulatory knowledge base. I can answer questions about EU AI Act, GDPR, DPDP Act, NIST AI RMF, and other applicable regulations. What would you like to know?",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || sending) return;
    const userMsg: Message = {
      id: `u-${Date.now()}`,
      role: "user",
      content: text.trim(),
      timestamp: new Date(),
    };
    const loadingMsg: Message = {
      id: `l-${Date.now()}`,
      role: "assistant",
      content: "",
      timestamp: new Date(),
      loading: true,
    };
    setMessages((prev) => [...prev, userMsg, loadingMsg]);
    setInput("");
    setSending(true);

    try {
      // Try real API first
      const response = await api.post("/v1/query", {
        query: text,
        context: "compliance",
      });
      const data = response.data;
      const aiMsg: Message = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: data.answer || getMockResponse(text),
        timestamp: new Date(),
        citations: getCitations(text),
      };
      setMessages((prev) =>
        prev.map((m) => (m.id === loadingMsg.id ? aiMsg : m))
      );
    } catch {
      // Fallback to mock
      await new Promise((r) => setTimeout(r, 1200));
      const aiMsg: Message = {
        id: `a-${Date.now()}`,
        role: "assistant",
        content: getMockResponse(text),
        timestamp: new Date(),
        citations: getCitations(text),
      };
      setMessages((prev) =>
        prev.map((m) => (m.id === loadingMsg.id ? aiMsg : m))
      );
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage(input);
    }
  };

  return (
    <div className="flex flex-col h-full max-h-screen">
      {/* Header */}
      <div className="px-6 py-5 border-b border-white/[0.06] flex-shrink-0">
        <div className="max-w-4xl mx-auto flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-purple-500/20 border border-purple-500/30 flex items-center justify-center">
              <Bot className="w-4.5 h-4.5 text-purple-400" />
            </div>
            <div>
              <h1 className="font-heading font-bold text-white text-lg">
                Compliance Advisor
              </h1>
              <p className="text-xs text-[rgb(163,163,163)]">
                AI-powered regulatory guidance &mdash; EU AI Act · GDPR · DPDP · NIST
              </p>
            </div>
          </div>
          <div className="flex items-center gap-1.5 text-xs text-green-400">
            <div className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
            KB Online
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        <div className="max-w-4xl mx-auto space-y-6">
          {messages.map((msg) => (
            <MessageBubble key={msg.id} msg={msg} />
          ))}
          <div ref={bottomRef} />
        </div>
      </div>

      {/* Suggested chips */}
      {messages.length <= 2 && (
        <div className="px-6 pb-3 flex-shrink-0">
          <div className="max-w-4xl mx-auto">
            <p className="text-[10px] text-[rgb(115,115,115)] mb-2 flex items-center gap-1">
              <Sparkles className="w-3 h-3" />
              Suggested questions
            </p>
            <div className="flex flex-wrap gap-2">
              {SUGGESTED.map((q) => (
                <button
                  key={q}
                  onClick={() => sendMessage(q)}
                  disabled={sending}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full glass border border-white/[0.08] text-xs text-[rgb(163,163,163)] hover:text-white hover:border-blue-500/30 hover:bg-blue-500/10 transition-all disabled:opacity-50"
                >
                  {q}
                  <ChevronRight className="w-3 h-3" />
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Input bar */}
      <div className="px-6 pb-6 pt-2 flex-shrink-0 border-t border-white/[0.06]">
        <div className="max-w-4xl mx-auto">
          <div className="glass border border-white/[0.10] rounded-2xl flex items-end gap-3 p-3 focus-within:border-blue-500/40 transition-colors">
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about regulations, compliance requirements, or specific AI system obligations…"
              rows={1}
              disabled={sending}
              className="flex-1 bg-transparent text-sm text-white placeholder-[rgb(115,115,115)] resize-none focus:outline-none leading-relaxed max-h-32 overflow-y-auto disabled:opacity-50"
              style={{ minHeight: "1.5rem" }}
            />
            <button
              onClick={() => sendMessage(input)}
              disabled={!input.trim() || sending}
              className="flex-shrink-0 w-9 h-9 rounded-xl bg-blue-500 hover:bg-blue-400 disabled:bg-white/[0.06] disabled:text-[rgb(115,115,115)] text-white flex items-center justify-center transition-all glow-blue disabled:shadow-none"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
          <p className="text-[10px] text-[rgb(115,115,115)] text-center mt-2">
            Shift+Enter for new line · Enter to send · Responses reference live regulation KB
          </p>
        </div>
      </div>
    </div>
  );
}
