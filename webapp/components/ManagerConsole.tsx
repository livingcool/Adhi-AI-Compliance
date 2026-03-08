"use client";

import { useState, useEffect, useRef } from "react";
import { Mic, MicOff, Send, Bot, X, Check, ArrowRight, Sparkles, Settings as SettingsIcon } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import Link from "next/link";

// Mock Intelligence Data
const DAILY_BRIEFING = [
    { id: 1, type: "critical", msg: "Client Alpha: Contract renewal risk detects. Sentiment in last email was negative.", action: "Draft Renewal Strategy" },
    { id: 2, type: "info", msg: "Legislation Update: New privacy laws affect 3 of your contracts.", action: "Review Impact" },
    { id: 3, type: "success", msg: "Invoice #992 (Client Bravo) was paid early.", action: "Send Thank You" }
];

interface Message {
    id: string;
    role: "ai" | "user";
    text: string;
    action?: {
        label: string;
        type: "approve" | "review";
        onAction: () => void;
    };
    timestamp: Date;
}

interface ManagerConsoleProps {
    orgId: string;
    clientName: string;
}

export default function ManagerConsole({ orgId, clientName }: ManagerConsoleProps) {
    const [isOpen, setIsOpen] = useState(false);
    const [isListening, setIsListening] = useState(false);
    const [input, setInput] = useState("");
    const [messages, setMessages] = useState<Message[]>([
        {
            id: "init",
            role: "ai",
            text: `Good afternoon. I've analyzed intelligence for ${clientName}. Ready for your command.`,
            timestamp: new Date()
        }
    ]);
    const [filters, setFilters] = useState({
        doc_type: "",
    });

    const messagesEndRef = useRef<HTMLDivElement>(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isOpen]);

    const handleSend = async () => {
        if (!input.trim()) return;

        // User Message
        const userMsg: Message = { id: Date.now().toString(), role: "user", text: input, timestamp: new Date() };
        setMessages(prev => [...prev, userMsg]);
        setInput("");

        // Real AI Response
        try {
            const response = await fetch('/api/chat/manager', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: input,
                    orgId: orgId,
                    filters: filters.doc_type ? { doc_type: filters.doc_type } : {}
                })
            });
            const data = await response.json();

            if (data.success) {
                const aiMsg: Message = {
                    id: (Date.now() + 1).toString(),
                    role: "ai",
                    text: data.text,
                    timestamp: new Date(data.timestamp)
                };
                setMessages(prev => [...prev, aiMsg]);
            }
        } catch (error) {
            console.error("Chat Error", error);
        }
    };

    const toggleVoice = () => {
        setIsListening(!isListening);
        if (!isListening) {
            // Mock voice input simulation
            setTimeout(() => {
                setInput("Schedule a meeting with Client Alpha for Tuesday");
                setIsListening(false);
            }, 2000);
        }
    };

    return (
        <>
            {/* Floating Trigger Button */}
            <motion.button
                onClick={() => setIsOpen(!isOpen)}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                className="fixed bottom-6 right-6 z-50 h-14 w-14 rounded-full bg-secondary border border-white/10 shadow-[0_0_20px_rgba(0,0,0,0.5)] flex items-center justify-center text-foreground hover:bg-secondary/80 transition-colors"
            >
                {isOpen ? <X size={24} /> : <Bot size={28} className="text-[#F5F5DC]" />}
                {!isOpen && (
                    <span className="absolute -top-1 -right-1 h-3 w-3 bg-white rounded-full animate-pulse shadow-[0_0_5px_white]" />
                )}
            </motion.button>

            {/* Console Window */}
            <AnimatePresence>
                {isOpen && (
                    <motion.div
                        initial={{ opacity: 0, y: 20, scale: 0.95 }}
                        animate={{ opacity: 1, y: 0, scale: 1 }}
                        exit={{ opacity: 0, y: 20, scale: 0.95 }}
                        className="fixed bottom-24 right-6 w-96 h-[600px] z-50 glass-card rounded-3xl border border-white/10 flex flex-col overflow-hidden shadow-2xl"
                    >
                        {/* Header */}
                        <div className="p-4 border-b border-white/5 bg-secondary/30 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="h-2 w-2 rounded-full bg-white animate-pulse" />
                                <h3 className="font-bold text-white tracking-widest text-sm uppercase">{clientName} Intelligence</h3>
                            </div>
                            <div className="flex items-center gap-2">
                                <Link href="/settings" className="text-muted-foreground hover:text-white transition-colors">
                                    <SettingsIcon size={16} />
                                </Link>
                                <Sparkles size={16} className="text-[#F5F5DC]" />
                            </div>
                        </div>

                        {/* Chat / Feed Area */}
                        <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">

                            {/* ROI Ledger (AI Spend Tracker) */}
                            <div className="glass-card rounded-xl p-4 border border-white/5 flex items-center justify-between">
                                <div>
                                    <h4 className="text-[10px] uppercase font-bold text-muted-foreground mb-1">AI ROI Ledger</h4>
                                    <div className="flex items-center gap-2">
                                        <span className="text-xl font-bold text-white">$437.50</span>
                                        <span className="text-xs text-green-400 font-bold bg-green-400/10 px-1.5 py-0.5 rounded flex items-center gap-1">
                                            <Sparkles size={10} /> Saved
                                        </span>
                                    </div>
                                </div>
                                <div className="text-right">
                                    <p className="text-[10px] text-muted-foreground mb-1">Cost (Est.)</p>
                                    <p className="text-sm font-mono text-red-300">-$12.45</p>
                                </div>
                            </div>

                            {/* Briefing Card (if at top) */}
                            <div className="bg-white/5 rounded-xl p-4 border border-white/5 mb-6">
                                <h4 className="text-[10px] uppercase font-bold text-muted-foreground mb-3">Daily Briefing</h4>
                                <div className="space-y-3">
                                    {DAILY_BRIEFING.map((item) => (
                                        <div key={item.id} className="flex gap-3 items-start group cursor-pointer">
                                            <div className={`mt-1 h-1.5 w-1.5 rounded-full shrink-0 ${item.type === 'critical' ? 'bg-white shadow-[0_0_5px_white]' : 'bg-[#D5CEA3]'}`} />
                                            <div>
                                                <p className="text-xs text-foreground/90 font-medium leading-relaxed group-hover:text-white transition-colors">{item.msg}</p>
                                                <button className="text-[10px] text-[#D5CEA3] hover:text-white hover:underline mt-1 flex items-center gap-1">
                                                    {item.action} <ArrowRight size={10} />
                                                </button>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            {/* Conversation */}
                            {messages.map((msg) => (
                                <div key={msg.id} className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                                    <div className={`max-w-[85%] rounded-2xl p-3 ${msg.role === 'user'
                                        ? 'bg-[#F5F5DC] text-[#1A120B]'
                                        : 'bg-secondary/50 border border-white/5 text-[#F5F5DC]'
                                        }`}>
                                        <p className="text-xs leading-relaxed">{msg.text}</p>

                                        {/* Embedded Action */}
                                        {msg.action && (
                                            <div className="mt-3 pt-3 border-t border-white/10 flex justify-end">
                                                <button
                                                    onClick={msg.action.onAction}
                                                    className="bg-white/10 hover:bg-white/20 text-white text-[10px] font-bold py-1.5 px-3 rounded-lg border border-white/10 flex items-center gap-2 transition-colors"
                                                >
                                                    <Check size={12} /> {msg.action.label}
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            ))}
                            <div ref={messagesEndRef} />
                        </div>

                        {/* Input Area */}
                        <div className="p-3 bg-secondary/30 border-t border-white/5">
                            {isListening && (
                                <div className="mb-2 text-center text-[10px] font-mono text-white animate-pulse">Listening to your command...</div>
                            )}
                            <div className="flex gap-2">
                                <button
                                    onClick={toggleVoice}
                                    className={`p-3 rounded-xl border transition-all ${isListening ? 'bg-white text-black border-white' : 'bg-white/5 text-muted-foreground border-white/5 hover:bg-white/10'}`}
                                >
                                    {isListening ? <Mic size={18} /> : <MicOff size={18} />}
                                </button>

                                <select
                                    value={filters.doc_type}
                                    onChange={(e) => setFilters(prev => ({ ...prev, doc_type: e.target.value }))}
                                    className="bg-white/5 border border-white/5 text-white text-[10px] rounded-xl px-2 focus:outline-none focus:border-white/20 [&>option]:text-black"
                                >
                                    <option value="" className="text-black">All Memory</option>
                                    <option value="video" className="text-black">Video</option>
                                    <option value="audio" className="text-black">Audio</option>
                                    <option value="pdf" className="text-black">PDF</option>
                                    <option value="image" className="text-black">Image</option>
                                </select>
                                <div className="flex-1 relative">
                                    <input
                                        type="text"
                                        value={input}
                                        onChange={(e) => setInput(e.target.value)}
                                        onKeyDown={(e) => e.key === 'Enter' && handleSend()}
                                        placeholder="Give a task or ask for an update..."
                                        className="w-full h-full bg-white/5 border border-white/5 rounded-xl px-4 text-xs text-white placeholder:text-muted-foreground focus:outline-none focus:border-white/20"
                                    />
                                    <button
                                        onClick={handleSend}
                                        className="absolute right-2 top-1/2 -translate-y-1/2 p-1.5 text-[#F5F5DC] hover:text-white transition-colors"
                                    >
                                        <Send size={14} />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </>
    );
}
