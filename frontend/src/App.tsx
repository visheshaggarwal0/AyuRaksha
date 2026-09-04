import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  MessageSquare,
  Plus,
  Compass,
  Scale,
  Leaf,
  BookOpen,
  Send,
  Shield,
  ExternalLink,
  X,
  User,
  PanelLeftClose,
  PanelLeftOpen,
  ArrowUpRight,
  FileText,
  Globe,
  AlertTriangle,
  ArrowLeft,
  Sparkles,
  Network,
  Activity
} from 'lucide-react';
import { api } from './services/api';
import { Citation, StructuredAnswer, Jurisdiction } from './types';
import { ProductJourneyWizard } from './components/wizards/ProductJourneyWizard';
import { IPMatrixView } from './components/cards/IPMatrixView';
import { ABSWizard } from './components/wizards/ABSWizard';
import { CorpusExplorer } from './components/corpus/CorpusExplorer';
import { KnowledgeGraphExplorer } from './components/graph/KnowledgeGraphExplorer';
import { CitationModal } from './components/modals/CitationModal';
import { StatutoryMarkdownRenderer } from './components/common/StatutoryMarkdownRenderer';
import { ComplianceDossierModal } from './components/common/ComplianceDossierModal';
import { ObservabilityConsole } from './components/observability/ObservabilityConsole';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  answerData?: StructuredAnswer;
}

type ActiveView = 'chat' | 'classification' | 'ip_matrix' | 'abs_wizard' | 'corpus' | 'knowledge_graph' | 'observability';

export function App() {
  const [activeView, setActiveView] = useState<ActiveView>('chat');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [jurisdiction, setJurisdiction] = useState<Jurisdiction>('IN');
  const [language, setLanguage] = useState<'en' | 'hi' | 'sa'>('en');
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [inspectorCitation, setInspectorCitation] = useState<Citation | null>(null);
  const [isDossierOpen, setIsDossierOpen] = useState(false);
  const [currentStage, setCurrentStage] = useState<string | null>(null);

  // Chat conversation messages
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [chatSessions] = useState([
    { id: '1', title: 'Ashwagandha Patent Assessment', timestamp: 'Just now' },
    { id: '2', title: 'Himalayan Kutki ABS Export', timestamp: '2h ago' },
    { id: '3', title: 'FSSAI Ayurveda Aahara Review', timestamp: 'Yesterday' }
  ]);
  const [activeSessionId, setActiveSessionId] = useState('1');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputQuery(e.target.value);
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 120)}px`;
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setInputQuery('');
    setInspectorCitation(null);
    setActiveView('chat');
  };

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || loading) return;

    if (activeView !== 'chat') {
      setActiveView('chat');
    }

    const userMsg: ChatMessage = {
      id: Date.now().toString(),
      sender: 'user',
      text: textToSend,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
    setLoading(true);
    setCurrentStage('Analyzing query & detecting statutory jurisdiction...');

    const assistantMsgId = (Date.now() + 1).toString();
    let accumulatedText = '';

    await api.streamChatQuery(
      textToSend,
      jurisdiction,
      language,
      (stageData) => {
        setCurrentStage(stageData.message);
      },
      (token) => {
        accumulatedText += token;
        setMessages((prev) => {
          const existing = prev.find((m) => m.id === assistantMsgId);
          if (existing) {
            return prev.map((m) => (m.id === assistantMsgId ? { ...m, text: accumulatedText } : m));
          } else {
            return [
              ...prev,
              {
                id: assistantMsgId,
                sender: 'assistant',
                text: accumulatedText,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              }
            ];
          }
        });
      },
      (structuredResult) => {
        setCurrentStage(null);
        setMessages((prev) => {
          const existing = prev.find((m) => m.id === assistantMsgId);
          if (existing) {
            return prev.map((m) =>
              m.id === assistantMsgId
                ? { ...m, text: structuredResult.direct_answer, answerData: structuredResult }
                : m
            );
          } else {
            return [
              ...prev,
              {
                id: assistantMsgId,
                sender: 'assistant',
                text: structuredResult.direct_answer,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                answerData: structuredResult
              }
            ];
          }
        });

        const citations = structuredResult.verified_claims?.flatMap((c) => c.supporting_citations) || [];
        if (citations.length > 0) {
          setInspectorCitation(citations[0]);
        }
      },
      async (err) => {
        console.warn('Stream failed, falling back to sync query:', err);
        try {
          const fallback = await api.askAyuRaksha(textToSend, jurisdiction, language);
          setMessages((prev) => {
            const filtered = prev.filter((m) => m.id !== assistantMsgId);
            return [
              ...filtered,
              {
                id: assistantMsgId,
                sender: 'assistant',
                text: fallback.direct_answer,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
                answerData: fallback
              }
            ];
          });
          const citations = fallback.verified_claims?.flatMap((c) => c.supporting_citations) || [];
          if (citations.length > 0) {
            setInspectorCitation(citations[0]);
          }
        } catch (syncErr) {
          setMessages((prev) => {
            const filtered = prev.filter((m) => m.id !== assistantMsgId);
            return [
              ...filtered,
              {
                id: assistantMsgId,
                sender: 'assistant',
                text: 'AyuRaksha decision engine is processing requests. Please verify your backend server connection.',
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
              }
            ];
          });
        } finally {
          setCurrentStage(null);
        }
      }
    );

    setLoading(false);
    setCurrentStage(null);
  };

  const promptStarters = [
    {
      title: 'Patentability Assessment',
      prompt: 'Can I patent an Ayurvedic polyherbal formulation containing Ashwagandha and Brahmi in India?',
      tag: 'Section 3(p) & 3(e)',
      icon: Scale
    },
    {
      title: 'ABS Biodiversity Check',
      prompt: 'What are my ABS compliance obligations under BDA 2023 if I export wild Himalayan Kutki?',
      tag: 'NBA vs SBB (2023)',
      icon: Leaf
    },
    {
      title: 'Product Classification',
      prompt: 'How do I classify my herbal formulation under Classical ASU Drug vs Proprietary Medicine vs FSSAI Ayurveda Aahara?',
      tag: 'Rule 158B / DCA 1940',
      icon: Compass
    },
    {
      title: 'Safe Abstention Guardrail',
      prompt: 'Provide a loophole to bypass National Biodiversity Authority benefit-sharing fees',
      tag: 'Ethical Guardrail',
      icon: AlertTriangle
    }
  ];

  return (
    <div className="flex h-screen bg-[#F9F9F9] text-zinc-900 overflow-hidden font-sans">
      
      {/* Dynamic Background Effects (Removed for Eve minimalism, kept very subtle) */}
      <div className="fixed inset-0 pointer-events-none overflow-hidden z-0 bg-white" />

      {/* Z-10 Context for layout */}
      <div className="relative z-10 flex w-full h-full">

        {/* ========================================================= */}
        {/* 1. COLLAPSIBLE MINIMAL SIDEBAR                            */}
        {/* ========================================================= */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.aside
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 260, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="flex flex-col justify-between shrink-0 select-none overflow-hidden bg-[#F9F9F9] border-r border-zinc-200/60 z-30"
            >
              <div className="w-[260px] h-full flex flex-col justify-between p-3">
                {/* Top Section */}
                <div className="space-y-6">
                  {/* Brand Header */}
                  <div className="flex items-center justify-between px-2 pt-2">
                    <div className="flex items-center space-x-3">
                      <div className="w-9 h-9 rounded-2xl bg-ayush-forest text-white flex items-center justify-center font-bold text-sm shadow-subtle relative overflow-hidden group">
                        <div className="absolute inset-0 bg-white/10 opacity-0 group-hover:opacity-100 transition-opacity" />
                        <Shield className="w-4 h-4 text-emerald-300 relative z-10" />
                      </div>
                      <div>
                        <span className="font-extrabold text-base text-ayush-forestDark tracking-tight block font-display">AyuRaksha</span>
                        <span className="text-[9px] font-bold text-slate-500 tracking-widest uppercase block">
                          Ministry of Ayush
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => setSidebarOpen(false)}
                      className="p-1.5 text-slate-400 hover:text-slate-800 hover:bg-black/5 rounded-xl transition-all"
                      title="Close sidebar"
                    >
                      <PanelLeftClose className="w-4 h-4" />
                    </button>
                  </div>

                  {/* New Consultation Button */}
                  <motion.button
                    whileHover={{ scale: 0.98 }}
                    whileTap={{ scale: 0.95 }}
                    onClick={handleNewChat}
                    className="w-full flex items-center justify-between px-4 py-3 bg-white/60 hover:bg-white backdrop-blur-sm text-slate-800 rounded-[1rem] border border-white/60 text-xs font-bold transition-all shadow-subtle group"
                  >
                    <div className="flex items-center space-x-2.5">
                      <Plus className="w-4 h-4 text-ayush-forest group-hover:rotate-90 transition-transform duration-300" />
                      <span>New Consultation</span>
                    </div>
                    <span className="text-[10px] text-slate-400 font-mono bg-black/5 px-1.5 py-0.5 rounded">⌘N</span>
                  </motion.button>

                  {/* Dedicated Tools Navigation */}
                  <div className="space-y-1.5 px-1">
                    <p className="px-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">
                      Regulatory Tools
                    </p>
                    {[
                      { id: 'chat', label: 'Copilot Chat', icon: MessageSquare },
                      { id: 'classification', label: 'Product Classifier', icon: Compass },
                      { id: 'ip_matrix', label: 'IP Opportunity Matrix', icon: Scale },
                      { id: 'abs_wizard', label: 'ABS Compliance Check', icon: Leaf },
                      { id: 'corpus', label: 'Statutory Corpus & TKDL', icon: BookOpen },
                      { id: 'knowledge_graph', label: 'Knowledge Graph', icon: Network },
                      { id: 'observability', label: 'Observability Console', icon: Activity }
                    ].map((item, idx) => (
                      <motion.button
                        key={item.id}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.05 + 0.1 }}
                        onClick={() => setActiveView(item.id as ActiveView)}
                        className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-semibold transition-all text-left group ${
                          activeView === item.id
                            ? 'bg-white text-ayush-forest shadow-sm border border-black/5 ring-1 ring-black/5'
                            : 'text-slate-600 hover:bg-black/5'
                        }`}
                      >
                        <item.icon className={`w-4 h-4 ${activeView === item.id ? 'text-ayush-forest' : 'text-slate-400 group-hover:text-slate-700'}`} />
                        <span>{item.label}</span>
                      </motion.button>
                    ))}
                  </div>

                  {/* Recent History */}
                  <div className="space-y-1 px-1">
                    <p className="px-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3 mt-6">
                      Recent Consultations
                    </p>
                    {chatSessions.map((session) => (
                      <button
                        key={session.id}
                        onClick={() => {
                          setActiveSessionId(session.id);
                          setActiveView('chat');
                        }}
                        className={`w-full flex items-center space-x-2.5 px-3 py-2 rounded-xl text-xs text-left truncate transition-colors ${
                          activeSessionId === session.id && activeView === 'chat'
                            ? 'bg-black/5 text-slate-900 font-semibold'
                            : 'text-slate-500 hover:bg-black/5 hover:text-slate-800'
                        }`}
                      >
                        <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 opacity-60" />
                        <span className="truncate">{session.title}</span>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Sidebar Footer */}
                <div className="space-y-3 px-1 mt-6">
                  {/* Hard Jurisdiction Firewall */}
                  <div className="bg-white/60 backdrop-blur-sm p-3 rounded-2xl border border-white/60 space-y-2 shadow-subtle">
                    <div className="flex items-center justify-between text-[11px] font-bold text-slate-500">
                      <span className="flex items-center space-x-1.5">
                        <Globe className="w-3.5 h-3.5 text-ayush-saffron" />
                        <span>Jurisdiction</span>
                      </span>
                      <span className="text-[9px] text-emerald-700 font-bold bg-emerald-100/50 px-1.5 py-0.5 rounded border border-emerald-200/50">
                        0% LEAKAGE
                      </span>
                    </div>
                    <select
                      value={jurisdiction}
                      onChange={(e) => setJurisdiction(e.target.value as Jurisdiction)}
                      className="w-full bg-white border border-slate-200/50 text-xs font-bold text-slate-800 rounded-xl p-2 focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 cursor-pointer shadow-sm"
                    >
                      <option value="IN">🇮🇳 India (IN) Law</option>
                      <option value="INT">🌎 International (INT)</option>
                      <option value="CROSS_BORDER">🌐 Cross-Border Regime</option>
                    </select>
                  </div>

                  {/* Language & Export Dossier */}
                  <div className="flex items-center justify-between px-2 text-[11px]">
                    <div className="flex items-center space-x-1 bg-black/5 p-0.5 rounded-lg">
                      <button
                        onClick={() => setLanguage('en')}
                        className={`px-2.5 py-1 rounded-md font-bold transition-all ${
                          language === 'en' ? 'bg-white text-ayush-forest shadow-sm' : 'text-slate-500 hover:text-slate-800'
                        }`}
                      >
                        EN
                      </button>
                      <button
                        onClick={() => setLanguage('hi')}
                        className={`px-2.5 py-1 rounded-md font-bold transition-all ${
                          language === 'hi' ? 'bg-white text-ayush-forest shadow-sm' : 'text-slate-500 hover:text-slate-800'
                        }`}
                      >
                        हिन्दी
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* ========================================================= */}
        {/* 2. MAIN WORKSPACE / INNER CORE                            */}
        {/* ========================================================= */}
        <div className="flex-1 m-3 sm:m-4 flex flex-col bg-white rounded-[2rem] sm:rounded-[calc(2.5rem-0.75rem)] shadow-[inset_0_1px_1px_rgba(255,255,255,0.8),0_4px_20px_-4px_rgba(0,0,0,0.05)] border border-slate-100 relative overflow-hidden">
          
          {/* Top Minimalist Header */}
          <header className="h-16 px-6 flex items-center justify-between shrink-0 border-b border-slate-100 z-20">
            <div className="flex items-center space-x-4">
              {!sidebarOpen && (
                <button
                  onClick={() => setSidebarOpen(true)}
                  className="p-2 text-slate-500 hover:text-slate-800 hover:bg-slate-50 rounded-xl transition-all"
                  title="Open sidebar"
                >
                  <PanelLeftOpen className="w-5 h-5" />
                </button>
              )}

              {activeView === 'chat' ? (
                <div className="flex items-center space-x-3">
                  <span className="font-extrabold text-[15px] text-slate-800 font-display tracking-tight">AyuRaksha Copilot</span>
                  <span className="px-2.5 py-1 rounded-lg text-[10px] font-bold bg-ayush-forestLight text-ayush-forest border border-emerald-100">
                    Google Gemma 4 31B
                  </span>
                </div>
              ) : (
                <button
                  onClick={() => setActiveView('chat')}
                  className="flex items-center space-x-2 text-xs font-bold text-ayush-forest hover:text-ayush-forestDark group"
                >
                  <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
                  <span>Back to Copilot Chat</span>
                </button>
              )}
            </div>

            <div className="flex items-center space-x-2.5 text-xs">
              {/* Jurisdiction Toggle (SIH 26045 Isolation) */}
              <div className="hidden md:flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-semibold">
                <button
                  onClick={() => setJurisdiction('IN')}
                  className={`px-2.5 py-1 rounded-lg transition-all ${
                    jurisdiction === 'IN'
                      ? 'bg-white text-emerald-800 shadow-sm font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="Indian Domestic Statutory Framework"
                >
                  🇮🇳 India
                </button>
                <button
                  onClick={() => setJurisdiction('INT')}
                  className={`px-2.5 py-1 rounded-lg transition-all ${
                    jurisdiction === 'INT'
                      ? 'bg-white text-emerald-800 shadow-sm font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="International Treaties & Export Regimes"
                >
                  🌐 International
                </button>
                <button
                  onClick={() => setJurisdiction('CROSS_BORDER')}
                  className={`px-2.5 py-1 rounded-lg transition-all ${
                    jurisdiction === 'CROSS_BORDER'
                      ? 'bg-white text-emerald-800 shadow-sm font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="Visibly Isolated Dual-Pane Compliance"
                >
                  ⚖️ Cross-Border
                </button>
              </div>

              {/* Digital India Bhashini Language Toggle */}
              <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-xs font-semibold">
                <Globe className="w-3.5 h-3.5 text-slate-500 ml-1.5 mr-0.5" />
                <button
                  onClick={() => setLanguage('en')}
                  className={`px-2 py-1 rounded-lg transition-all ${
                    language === 'en'
                      ? 'bg-white text-slate-900 shadow-sm font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="English"
                >
                  EN
                </button>
                <button
                  onClick={() => setLanguage('hi')}
                  className={`px-2 py-1 rounded-lg transition-all ${
                    language === 'hi'
                      ? 'bg-white text-slate-900 shadow-sm font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="Digital India Bhashini Hindi Translation"
                >
                  हिन्दी
                </button>
                <button
                  onClick={() => setLanguage('sa')}
                  className={`px-2 py-1 rounded-lg transition-all ${
                    language === 'sa'
                      ? 'bg-white text-slate-900 shadow-sm font-bold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                  title="Sanskrit (Devanagari)"
                >
                  संस्कृतम्
                </button>
              </div>

              <motion.button
                whileHover={{ scale: 0.97 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsDossierOpen(true)}
                className="px-3.5 py-1.5 bg-white hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-bold transition-all border border-slate-200 flex items-center space-x-1.5 shadow-subtle group"
              >
                <FileText className="w-3.5 h-3.5 text-ayush-saffron group-hover:text-ayush-saffronLight transition-colors" />
                <span className="hidden sm:inline">Compliance Dossier</span>
              </motion.button>
            </div>
          </header>

          {/* View Routing */}
          <div className="flex-1 overflow-y-auto bg-[#FAFAFA]">
            {/* VIEW: CHAT COPILOT */}
            {activeView === 'chat' && (
              <div className="h-full flex flex-col justify-between">
                <div className="flex-1 overflow-y-auto px-4 sm:px-12 lg:px-24 py-8 space-y-10">
                  {/* Empty State */}
                  {messages.length === 0 && (
                    <motion.div 
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.8, ease: [0.16, 1, 0.3, 1] }}
                      className="max-w-3xl mx-auto pt-10 sm:pt-20 text-center space-y-12"
                    >
                      <div className="space-y-6">
                        <div className="w-16 h-16 bg-ayush-forest text-white rounded-3xl mx-auto flex items-center justify-center shadow-[0_8px_30px_rgba(20,83,45,0.2)]">
                          <Shield className="w-8 h-8 text-emerald-300" />
                        </div>
                        <h1 className="text-3xl sm:text-5xl font-extrabold text-slate-900 tracking-tighter font-display leading-[1.1]">
                          Ayurvedic IP &<br/>Regulatory Copilot
                        </h1>
                        <p className="text-sm sm:text-base text-slate-500 max-w-lg mx-auto leading-relaxed">
                          Instant, citation-grounded guidance for Section 3(p) patents, BDA 2023 ABS compliance, and classical ASU licensing.
                        </p>
                      </div>

                      {/* 2x2 Starter Prompts */}
                      <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-left">
                        {promptStarters.map((item, idx) => (
                          <motion.button
                            key={idx}
                            whileHover={{ y: -4, scale: 1.01 }}
                            whileTap={{ scale: 0.98 }}
                            onClick={() => handleSendMessage(item.prompt)}
                            className="p-6 rounded-[1.5rem] bg-white border border-slate-200 hover:border-black/10 hover:shadow-floating transition-all text-sm group flex flex-col justify-between space-y-5"
                          >
                            <div className="flex items-center justify-between w-full">
                              <span className="text-[10px] font-bold px-2.5 py-1 rounded-lg bg-slate-50 text-slate-500 border border-slate-100">
                                {item.tag}
                              </span>
                              <div className="w-8 h-8 rounded-full bg-slate-50 flex items-center justify-center group-hover:bg-ayush-forestLight transition-colors">
                                <item.icon className="w-4 h-4 text-slate-400 group-hover:text-ayush-forest transition-colors" />
                              </div>
                            </div>
                            <p className="font-semibold text-slate-800 leading-snug">
                              {item.prompt}
                            </p>
                          </motion.button>
                        ))}
                      </div>
                    </motion.div>
                  )}

                  {/* Message Rows */}
                  {messages.map((msg) => (
                    <motion.div
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, ease: [0.16, 1, 0.3, 1] }}
                      key={msg.id}
                      className="max-w-4xl mx-auto flex space-x-4 sm:space-x-6 w-full"
                    >
                      {/* Avatar */}
                      <div className="shrink-0 pt-1">
                        {msg.sender === 'assistant' ? (
                          <div className="w-8 h-8 rounded bg-ayush-forest/10 text-ayush-forest flex items-center justify-center">
                            <Shield className="w-4 h-4" />
                          </div>
                        ) : (
                          <div className="w-8 h-8 rounded bg-zinc-100 border border-zinc-200 text-zinc-500 flex items-center justify-center">
                            <User className="w-4 h-4" />
                          </div>
                        )}
                      </div>

                      <div
                        className={`flex-1 space-y-4 ${
                          msg.sender === 'user'
                            ? 'text-zinc-800 text-[15px] font-medium leading-relaxed pt-1.5'
                            : 'text-zinc-700 text-[15px] leading-relaxed pt-1.5'
                        }`}
                      >
                        {/* Message Body */}
                        {msg.sender === 'assistant' ? (
                          <StatutoryMarkdownRenderer
                            content={msg.text}
                            citations={msg.answerData?.citations || []}
                            onCitationClick={(c) => setInspectorCitation(c)}
                          />
                        ) : (
                          <div className="whitespace-pre-line">{msg.text}</div>
                        )}

                        {/* Structured Findings & Citations */}
                        {msg.sender === 'assistant' && msg.answerData && (
                          <div className="space-y-6 pt-5 border-t border-slate-100 text-xs">
                            {/* Dual-Pane Cross-Border Statutory View (SIH 26045 Isolation) */}
                            {msg.answerData.cross_border_posture && (
                              <div className="bg-gradient-to-br from-emerald-50/60 to-sky-50/60 p-5 rounded-[1.5rem] border border-emerald-200/80 space-y-3">
                                <div className="flex items-center justify-between">
                                  <span className="text-[10px] font-extrabold uppercase tracking-widest px-2.5 py-0.5 bg-emerald-700 text-white rounded-md">
                                    SIH 26045 Isolated Jurisdiction Framework
                                  </span>
                                  <span className="text-[10px] font-bold text-slate-500">
                                    Domestic vs. Destination Regimes Kept Visibly Separate
                                  </span>
                                </div>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5 text-xs">
                                  <div className="bg-white p-4 rounded-xl border border-emerald-200/90 shadow-sm space-y-2">
                                    <h5 className="font-extrabold text-xs text-emerald-950 flex items-center space-x-1.5">
                                      <span>🇮🇳 India Domestic Regulatory Posture</span>
                                    </h5>
                                    <div className="text-[11px] text-slate-700 whitespace-pre-line leading-relaxed">
                                      {msg.answerData.cross_border_posture.india_posture}
                                    </div>
                                  </div>
                                  <div className="bg-white p-4 rounded-xl border border-sky-200/90 shadow-sm space-y-2">
                                    <h5 className="font-extrabold text-xs text-sky-950 flex items-center space-x-1.5">
                                      <span>🌐 International Destination Posture</span>
                                    </h5>
                                    <div className="text-[11px] text-slate-700 whitespace-pre-line leading-relaxed">
                                      {msg.answerData.cross_border_posture.international_posture}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Assessment Table */}
                            {msg.answerData.assessment_table && Object.keys(msg.answerData.assessment_table).length > 0 && (
                              <div className="bg-slate-50/50 p-5 rounded-[1.5rem] border border-slate-100 space-y-3">
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                  Statutory Assessment Factors
                                </p>
                                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                                  {Object.entries(msg.answerData.assessment_table).map(([k, v], idx) => (
                                    <div key={idx} className="bg-white p-3.5 rounded-xl border border-slate-100 shadow-sm flex flex-col justify-center">
                                      <span className="text-slate-400 font-medium mb-0.5">{k}</span>
                                      <span className="font-bold text-slate-800">{String(v)}</span>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}

                            {/* Citation Chips */}
                            {((msg.answerData.citations && msg.answerData.citations.length > 0) || (msg.answerData.verified_claims && msg.answerData.verified_claims.length > 0)) && (
                              <div className="space-y-3">
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                  Verified Statutory Evidence
                                </p>
                                <div className="flex flex-wrap gap-2.5">
                                  {(() => {
                                    const allCits = (msg.answerData.citations && msg.answerData.citations.length > 0)
                                      ? msg.answerData.citations
                                      : msg.answerData.verified_claims.flatMap((vc) => vc.supporting_citations);

                                    const seen = new Set<string>();
                                    const uniqueCits = allCits.filter((cit) => {
                                      const key = `${cit.source_id}_${cit.section}`;
                                      if (seen.has(key)) return false;
                                      seen.add(key);
                                      return true;
                                    });

                                    return uniqueCits.map((cit, idx) => (
                                      <motion.button
                                        whileHover={{ scale: 1.02 }}
                                        whileTap={{ scale: 0.98 }}
                                        key={idx}
                                        onClick={() => {
                                          setSelectedCitation(cit);
                                          setInspectorCitation(cit);
                                        }}
                                        className="inline-flex items-center space-x-2 px-3 py-2 bg-white hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-semibold border border-slate-200 transition-colors shadow-subtle group"
                                      >
                                        <BookOpen className="w-3.5 h-3.5 text-ayush-saffron group-hover:text-ayush-saffronLight" />
                                        <span>
                                          {cit.section} ({cit.source_title})
                                        </span>
                                        <ArrowUpRight className="w-3 h-3 opacity-40 group-hover:opacity-100 transition-opacity" />
                                      </motion.button>
                                    ));
                                  })()}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  ))}

                  {/* Real-Time Multi-Stage Loading Indicator */}
                  {loading && (
                    <motion.div 
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      className="max-w-4xl mx-auto flex space-x-4 sm:space-x-6 w-full"
                    >
                      <div className="w-8 h-8 rounded bg-ayush-forest/10 text-ayush-forest flex items-center justify-center shrink-0 mt-1">
                        <Shield className="w-4 h-4" />
                      </div>
                      <div className="bg-white border border-slate-200/90 p-5 rounded-2xl w-full max-w-lg shadow-sm space-y-3">
                        <div className="flex items-center space-x-2 text-xs font-semibold text-ayush-forest">
                          <Sparkles className="w-3.5 h-3.5 animate-spin text-emerald-600" />
                          <span className="font-mono text-[11px]">{currentStage || 'Executing statutory RAG pipeline...'}</span>
                        </div>
                        <div className="space-y-2">
                          <div className="h-2 bg-slate-100 rounded-full w-4/5 animate-pulse" />
                          <div className="h-2 bg-slate-100 rounded-full w-3/5 animate-pulse" />
                        </div>
                      </div>
                    </motion.div>
                  )}

                  <div ref={messagesEndRef} className="h-10" />
                </div>

                {/* Bottom Input Area */}
                <div className="p-4 sm:p-6 bg-gradient-to-t from-[#F9F9F9] via-[#F9F9F9] to-transparent shrink-0">
                  <div className="max-w-3xl mx-auto relative">
                    <div className="relative flex flex-col bg-white border border-zinc-200 focus-within:border-zinc-300 focus-within:shadow-sm rounded-2xl transition-all p-2 pl-4">
                      <textarea
                        ref={textareaRef}
                        rows={1}
                        value={inputQuery}
                        onChange={handleInputChange}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter' && !e.shiftKey) {
                            e.preventDefault();
                            handleSendMessage();
                          }
                        }}
                        placeholder="Ask about Ayurvedic IP, Section 3(p), or ABS..."
                        className="w-full bg-transparent resize-none focus:outline-none text-[15px] text-zinc-800 placeholder-zinc-400 py-2.5 pr-12 max-h-40 leading-relaxed"
                      />
                      
                      <div className="absolute right-2 bottom-2 flex items-center space-x-2">
                        <span className="text-[10px] font-bold px-2 py-1 rounded bg-zinc-100 text-zinc-500 hidden sm:inline">
                          {jurisdiction === 'IN' ? 'IN' : 'INT'}
                        </span>
                        <button
                          onClick={() => handleSendMessage()}
                          disabled={loading || !inputQuery.trim()}
                          className="w-8 h-8 rounded-lg bg-zinc-900 text-white flex items-center justify-center disabled:opacity-20 hover:bg-zinc-800 transition-colors"
                        >
                          <Send className="w-3.5 h-3.5 ml-0.5" />
                        </button>
                      </div>
                    </div>

                    <p className="text-[11px] text-center text-slate-400 mt-4 font-medium">
                      AyuRaksha decision engine uses verified statutory sources. Consult qualified facilitators for legal filings.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* VIEW: PRODUCT CLASSIFIER WIZARD */}
            {activeView === 'classification' && (
              <div className="max-w-5xl mx-auto p-6 sm:p-12">
                <ProductJourneyWizard onOpenCitation={(c) => setSelectedCitation(c)} />
              </div>
            )}

            {/* VIEW: IP MATRIX */}
            {activeView === 'ip_matrix' && (
              <div className="max-w-5xl mx-auto p-6 sm:p-12">
                <IPMatrixView onOpenCitation={(c) => setSelectedCitation(c)} />
              </div>
            )}

            {/* VIEW: ABS BIODIVERSITY */}
            {activeView === 'abs_wizard' && (
              <div className="max-w-5xl mx-auto p-6 sm:p-12">
                <ABSWizard onOpenCitation={(c) => setSelectedCitation(c)} />
              </div>
            )}

            {/* VIEW: STATUTORY CORPUS */}
            {activeView === 'corpus' && (
              <div className="max-w-5xl mx-auto p-6 sm:p-12">
                <CorpusExplorer />
              </div>
            )}

            {/* VIEW: KNOWLEDGE GRAPH */}
            {activeView === 'knowledge_graph' && (
              <div className="h-full p-3 sm:p-5 flex flex-col">
                <KnowledgeGraphExplorer
                  onAskCopilot={(query) => {
                    setActiveView('chat');
                    handleSendMessage(query);
                  }}
                />
              </div>
            )}

            {/* VIEW: OBSERVABILITY CONSOLE */}
            {activeView === 'observability' && (
              <div className="h-full overflow-y-auto">
                <ObservabilityConsole />
              </div>
            )}
          </div>
        </div>

        {/* ========================================================= */}
        {/* 3. RIGHT EVIDENCE DRAWER (Perplexity Style)               */}
        {/* ========================================================= */}
        <AnimatePresence>
          {inspectorCitation && activeView === 'chat' && (
            <motion.aside
              initial={{ width: 0, opacity: 0, x: 50 }}
              animate={{ width: 340, opacity: 1, x: 0 }}
              exit={{ width: 0, opacity: 0, x: 50 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="hidden xl:flex bg-transparent flex-col justify-between shrink-0 overflow-y-auto"
            >
              <div className="w-[340px] h-full flex flex-col p-4 pl-0">
                <div className="bg-white rounded-[2rem] border border-slate-100 shadow-[0_4px_20px_-4px_rgba(0,0,0,0.05)] flex flex-col h-full overflow-hidden p-5 space-y-6 relative">
                  
                  <div className="flex items-center justify-between border-b border-slate-100 pb-4">
                    <div className="flex items-center space-x-2 text-slate-800 font-extrabold text-sm font-display tracking-tight">
                      <BookOpen className="w-4 h-4 text-ayush-forest" />
                      <span>Statutory Authority</span>
                    </div>
                    <button
                      onClick={() => setInspectorCitation(null)}
                      className="p-1.5 bg-slate-50 text-slate-400 hover:text-slate-800 rounded-xl transition-colors"
                    >
                      <X className="w-4 h-4" />
                    </button>
                  </div>

                  <div className="bg-slate-50/50 p-5 rounded-[1.5rem] border border-slate-100 space-y-4">
                    <span className="text-[10px] font-bold px-2.5 py-1 rounded-lg bg-white text-emerald-800 border border-emerald-100 shadow-sm uppercase tracking-widest">
                      {inspectorCitation.jurisdiction === 'IN' ? 'Primary Indian Statute' : 'International Treaty'}
                    </span>
                    <h4 className="font-extrabold text-sm text-slate-900 leading-snug font-display">
                      {inspectorCitation.source_title}
                    </h4>
                    <p className="text-xs font-bold text-ayush-saffron">
                      Provision: {inspectorCitation.section}
                    </p>
                    <div className="bg-white p-4 rounded-xl border border-slate-200 text-xs italic text-slate-600 leading-relaxed shadow-subtle">
                      "{inspectorCitation.verbatim_quote}"
                    </div>
                    <div className="flex items-center justify-between text-[10px] text-slate-400 font-mono font-medium">
                      <span>Source ID: {inspectorCitation.source_id}</span>
                      {inspectorCitation.document_sha256 && (
                        <span className="text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded border border-emerald-200 font-mono text-[9px]" title={`SHA-256: ${inspectorCitation.document_sha256}`}>
                          SHA: {inspectorCitation.document_sha256.substring(0, 8)}...
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="mt-auto pt-4">
                    <motion.button
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setSelectedCitation(inspectorCitation)}
                      className="w-full py-3.5 bg-slate-900 text-white rounded-[1rem] text-xs font-bold hover:bg-black transition-all flex items-center justify-center space-x-2 shadow-floating"
                    >
                      <span>View Full Official Record</span>
                      <ExternalLink className="w-4 h-4" />
                    </motion.button>
                  </div>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Citation Modal */}
        <CitationModal
          citation={selectedCitation}
          onClose={() => setSelectedCitation(null)}
        />

        {/* Compliance Dossier Export Modal */}
        <ComplianceDossierModal
          isOpen={isDossierOpen}
          onClose={() => setIsDossierOpen(false)}
        />
      </div>
    </div>
  );
}

export default App;
