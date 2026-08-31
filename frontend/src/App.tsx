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
  Bot,
  User,
  PanelLeftClose,
  PanelLeftOpen,
  ArrowUpRight,
  FileText,
  Globe,
  AlertTriangle
  ,ArrowLeft
} from 'lucide-react';
import { api } from './services/api';
import { Citation, StructuredAnswer, Jurisdiction } from './types';
import { ProductJourneyWizard } from './components/wizards/ProductJourneyWizard';
import { IPMatrixView } from './components/cards/IPMatrixView';
import { ABSWizard } from './components/wizards/ABSWizard';
import { CorpusExplorer } from './components/corpus/CorpusExplorer';
import { CitationModal } from './components/modals/CitationModal';
import { ComplianceDossierModal } from './components/common/ComplianceDossierModal';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  answerData?: StructuredAnswer;
}

type ActiveView = 'chat' | 'classification' | 'ip_matrix' | 'abs_wizard' | 'corpus';

export function App() {
  const [activeView, setActiveView] = useState<ActiveView>('chat');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [jurisdiction, setJurisdiction] = useState<Jurisdiction>('IN');
  const [language, setLanguage] = useState<'en' | 'hi'>('en');
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [inspectorCitation, setInspectorCitation] = useState<Citation | null>(null);
  const [isDossierOpen, setIsDossierOpen] = useState(false);

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

    try {
      const response = await api.askAyuRaksha(textToSend, jurisdiction, language);
      const assistantMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: response.direct_answer,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        answerData: response
      };
      setMessages((prev) => [...prev, assistantMsg]);

      const citations = response.verified_claims?.flatMap((c) => c.supporting_citations) || [];
      if (citations.length > 0) {
        setInspectorCitation(citations[0]);
      }
    } catch (err) {
      console.error('Chat error', err);
      const errorMsg: ChatMessage = {
        id: (Date.now() + 1).toString(),
        sender: 'assistant',
        text: 'AyuRaksha decision engine is processing requests. Please verify your backend server connection.',
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
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
    <div className="fixed inset-0 flex items-center justify-center p-2 sm:p-4 md:p-6 lg:p-8 font-sans overflow-hidden">
      {/* Outer Shell: Double-Bezel Design */}
      <div className="w-full h-full max-w-[1800px] flex overflow-hidden rounded-[2.5rem] bg-white/40 border border-white/40 shadow-[0_8px_32px_rgba(0,0,0,0.04)] backdrop-blur-3xl relative">
        
        {/* ========================================================= */}
        {/* 1. LEFT SIDEBAR (Floating Island)                         */}
        {/* ========================================================= */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.aside
              initial={{ width: 0, opacity: 0, x: -50 }}
              animate={{ width: 300, opacity: 1, x: 0 }}
              exit={{ width: 0, opacity: 0, x: -50 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="flex flex-col justify-between shrink-0 select-none overflow-hidden bg-transparent z-30"
            >
              <div className="w-[300px] h-full flex flex-col justify-between p-4 pb-4">
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
                      { id: 'corpus', label: 'Statutory Corpus & TKDL', icon: BookOpen }
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

            <div className="flex items-center space-x-3 text-xs">
              <motion.button
                whileHover={{ scale: 0.97 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsDossierOpen(true)}
                className="px-4 py-2 bg-white hover:bg-slate-50 text-slate-700 rounded-xl text-xs font-bold transition-all border border-slate-200 flex items-center space-x-2 shadow-subtle group"
              >
                <FileText className="w-4 h-4 text-ayush-saffron group-hover:text-ayush-saffronLight transition-colors" />
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

                  {/* Message Bubbles */}
                  {messages.map((msg) => (
                    <motion.div
                      initial={{ opacity: 0, y: 16, filter: 'blur(4px)' }}
                      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
                      transition={{ duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
                      key={msg.id}
                      className={`max-w-4xl mx-auto flex space-x-4 sm:space-x-6 ${
                        msg.sender === 'user' ? 'justify-end' : 'justify-start'
                      }`}
                    >
                      {msg.sender === 'assistant' && (
                        <div className="w-10 h-10 rounded-[14px] bg-white text-ayush-forest flex items-center justify-center shrink-0 shadow-subtle border border-slate-100 mt-1">
                          <Bot className="w-5 h-5" />
                        </div>
                      )}

                      <div
                        className={`space-y-4 ${
                          msg.sender === 'user'
                            ? 'bg-ayush-forest text-white px-6 py-4 rounded-[2rem] rounded-tr-[4px] max-w-[85%] sm:max-w-2xl text-sm font-medium shadow-[0_8px_30px_rgba(20,83,45,0.15)] leading-relaxed'
                            : 'bg-white border border-slate-100 p-6 sm:p-8 rounded-[2rem] rounded-tl-[4px] w-full shadow-[0_4px_24px_-4px_rgba(0,0,0,0.02)] text-sm text-slate-800 space-y-5 leading-relaxed'
                        }`}
                      >
                        {/* Message Body */}
                        <div className="whitespace-pre-line">
                          {msg.text}
                        </div>

                        {/* Structured Findings & Citations */}
                        {msg.sender === 'assistant' && msg.answerData && (
                          <div className="space-y-6 pt-5 border-t border-slate-100 text-xs">
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
                            {msg.answerData.verified_claims.length > 0 && (
                              <div className="space-y-3">
                                <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">
                                  Verified Statutory Evidence
                                </p>
                                <div className="flex flex-wrap gap-2.5">
                                  {msg.answerData.verified_claims
                                    .flatMap((vc) => vc.supporting_citations)
                                    .map((cit, idx) => (
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
                                    ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}
                      </div>

                      {msg.sender === 'user' && (
                        <div className="w-10 h-10 rounded-[14px] bg-white border border-slate-100 text-slate-400 flex items-center justify-center shrink-0 shadow-subtle mt-1">
                          <User className="w-5 h-5" />
                        </div>
                      )}
                    </motion.div>
                  ))}

                  {/* Loading Skeleton */}
                  {loading && (
                    <motion.div 
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="max-w-4xl mx-auto flex space-x-6"
                    >
                      <div className="w-10 h-10 rounded-[14px] bg-slate-100 text-slate-400 flex items-center justify-center shrink-0 border border-slate-100 mt-1">
                        <Bot className="w-5 h-5" />
                      </div>
                      <div className="bg-white border border-slate-100 p-8 rounded-[2rem] w-full max-w-md shadow-sm space-y-4">
                        <div className="h-3 bg-slate-100 rounded-full w-3/4 animate-pulse" />
                        <div className="h-3 bg-slate-100 rounded-full w-1/2 animate-pulse" />
                        <div className="h-3 bg-slate-100 rounded-full w-5/6 animate-pulse" />
                      </div>
                    </motion.div>
                  )}

                  <div ref={messagesEndRef} className="h-10" />
                </div>

                {/* Bottom Input Area */}
                <div className="p-4 sm:p-8 bg-gradient-to-t from-[#FAFAFA] via-[#FAFAFA] to-transparent shrink-0">
                  <div className="max-w-4xl mx-auto relative">
                    <div className="relative flex flex-col bg-white border border-slate-200 focus-within:border-slate-300 focus-within:ring-4 focus-within:ring-slate-100 rounded-[1.75rem] shadow-card transition-all p-3 pl-5">
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
                        placeholder="Ask about Ayurvedic IP, Section 3(p), ABS, or FSSAI laws..."
                        className="w-full bg-transparent resize-none focus:outline-none text-sm sm:text-base font-medium text-slate-800 placeholder-slate-400 py-3 pr-16 max-h-40"
                      />
                      
                      <div className="absolute right-3 bottom-3 flex items-center space-x-2">
                        <span className="text-[10px] font-bold px-3 py-1.5 rounded-xl bg-slate-50 text-slate-500 border border-slate-100 hidden sm:inline">
                          {jurisdiction === 'IN' ? '🇮🇳 India Law' : '🌎 International'}
                        </span>
                        <motion.button
                          whileHover={{ scale: 1.05 }}
                          whileTap={{ scale: 0.92 }}
                          onClick={() => handleSendMessage()}
                          disabled={loading || !inputQuery.trim()}
                          className="w-10 h-10 rounded-[14px] bg-ayush-navy text-white flex items-center justify-center disabled:opacity-30 transition-colors shadow-subtle"
                        >
                          <Send className="w-4 h-4 ml-0.5" />
                        </motion.button>
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
                    <div className="text-[10px] text-slate-400 font-mono font-medium">
                      Source ID: {inspectorCitation.source_id}
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
