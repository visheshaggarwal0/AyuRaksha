import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  MessageSquare,
  Leaf,
  BookOpen,
  Send,
  PanelLeftClose,
  PanelLeftOpen,
  ShieldCheck,
  Plus,
  FileCheck,
  FlaskConical,
  Wheat,
  Smile,
  Sparkles
} from 'lucide-react';
import { api } from './services/api';
import {
  Citation,
  StructuredAnswer,
  Jurisdiction,
  ActiveCaseState
} from './types';
import { LandingPage } from './components/landing/LandingPage';
import { CitationModal } from './components/modals/CitationModal';
import { ObservabilityConsole } from './components/observability/ObservabilityConsole';
import { useTranslation } from './i18n/LanguageContext';
import { BrandLogo } from './components/common/BrandLogo';
import { ConversationalAnswer } from './components/chat/ConversationalAnswer';
import { ActiveDossierView } from './components/dossier/ActiveDossierView';
import { EvaluatorCorpusSuite } from './components/corpus/EvaluatorCorpusSuite';
import { EvidenceInspector } from './components/evidence/EvidenceInspector';
import { HACKATHON_ID, MINISTRY_NAME } from './constants/branding';
import { ErrorBoundary } from './components/common/ErrorBoundary';

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  answerData?: StructuredAnswer;
}

type ActiveView = 'copilot' | 'dossier' | 'corpus_suite' | 'landing' | 'observability';

export function App() {
  const [activeView, setActiveView] = useState<ActiveView>('copilot');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [jurisdiction, setJurisdiction] = useState<Jurisdiction>('IN');
  const { language, setLanguage, t } = useTranslation();
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [inspectorCitation, setInspectorCitation] = useState<Citation | null>(null);
  const [activeContextAnswer, setActiveContextAnswer] = useState<StructuredAnswer | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [currentStage, setCurrentStage] = useState<string | null>(null);

  useEffect(() => {
    api.getCorpusStats().catch(() => {});
  }, []);

  // Persistent Active Case State
  const [activeCase, setActiveCase] = useState<ActiveCaseState | null>(() => {
    try {
      const saved = localStorage.getItem('ayuraksha_active_case');
      if (saved) return JSON.parse(saved);
    } catch (e) {
      console.error('Failed to load saved case:', e);
    }
    return null;
  });

  const updateActiveCase = (updater: (prev: ActiveCaseState | null) => ActiveCaseState | null) => {
    setActiveCase((prev) => {
      const next = updater(prev);
      if (next) {
        localStorage.setItem('ayuraksha_active_case', JSON.stringify(next));
      } else {
        localStorage.removeItem('ayuraksha_active_case');
      }
      return next;
    });
  };

  // Chat conversation messages
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && drawerOpen) {
        setDrawerOpen(false);
        setInspectorCitation(null);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [drawerOpen]);

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
    setDrawerOpen(false);
    setInspectorCitation(null);
    setActiveContextAnswer(null);
    setActiveView('copilot');
  };

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || loading) return;

    if (activeView !== 'copilot') {
      setActiveView('copilot');
    }

    const userMsg: ChatMessage = {
      id: crypto.randomUUID(),
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
    setCurrentStage(t ? t('app.analyzing') : 'Consulting statutory corpus & regulations...');

    const assistantMsgId = (Date.now() + 1).toString();
    let accumulatedText = '';

    await api.streamChatQuery(
      textToSend,
      jurisdiction,
      language,
      (stageData) => {
        const msg = stageData.message || '';
        setCurrentStage(msg);
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

        // Store context quietly for on-demand citation inspection
        setActiveContextAnswer(structuredResult);
        if (structuredResult.citations && structuredResult.citations.length > 0) {
          setInspectorCitation(structuredResult.citations[0]);
        }

        // If statutory category was identified, update or initialize Active Case
        if (structuredResult.statutory_category || structuredResult.assessment_table?.['Category']) {
          updateActiveCase((prev) => {
            const now = new Date().toISOString();
            const caseId = prev?.caseId || `AYR-2026-${Math.floor(1000 + Math.random() * 9000)}`;
            const catName = (structuredResult.statutory_category || structuredResult.assessment_table?.['Category']) as string;
            return {
              caseId,
              createdAt: prev?.createdAt || now,
              updatedAt: now,
              productRequest: prev?.productRequest || {
                name: textToSend.length < 50 ? textToSend : 'Evaluated Formulation',
                in_classical_text: catName.includes('Classical'),
                is_formulation_modified: !catName.includes('Classical'),
                has_novel_excipients: false,
                intended_use: 'therapeutic',
                disease_treatment_claims: true,
                has_biological_resources: true,
                target_market: jurisdiction
              },
              classificationResult: prev?.classificationResult || {
                product_name: 'Evaluated Formulation',
                category: catName,
                governing_act: 'Drugs and Cosmetics Act, 1940 (Rule 158B)',
                patentability: String(structuredResult.assessment_table?.['Patentability'] || 'Barred under Sec 3(p) unless synergistic extract'),
                patent_rationale: 'Section 3(p) traditional knowledge defense',
                abs_required: true,
                regulatory_authority: 'State Licensing Authority (AYUSH)',
                citations: structuredResult.citations || [],
                confidence: 0.95,
                next_actions: structuredResult.assessment_table?.['Next Actions'] as any || []
              },
              recentCitations: structuredResult.citations || [],
              status: 'EVALUATED'
            };
          });
        }

        setLoading(false);
      },
      (err) => {
        console.error('Chat query error:', err);
        setLoading(false);
        setCurrentStage(null);
      }
    );
  };

  // Nav items: 3 Workspaces
  const navItems = [
    { id: 'copilot', label: 'IP-SAKTI Sahayak', icon: MessageSquare, badge: 'Copilot' },
    { id: 'dossier', label: 'Compliance Dossier', icon: FileCheck, badge: activeCase ? 'Active' : undefined },
    { id: 'corpus_suite', label: 'Corpus & Graph Suite', icon: BookOpen, badge: 'Evaluator' }
  ];

  // 6 PS 26045 Official Statutory Categories
  const categoryStarters = [
    {
      title: 'Classical Shastriya',
      desc: 'First Schedule text formula (Charaka, Sushruta)',
      icon: BookOpen,
      payload: 'Evaluate a Classical Ayurvedic Medicine (Shastriya) formulation drawn from a First-Schedule text.'
    },
    {
      title: 'Proprietary ASU',
      desc: 'New polyherbal ratio or novel mixture under Rule 158B',
      icon: FlaskConical,
      payload: 'Evaluate a Patent or Proprietary Medicine (ASU) with a modified herbal composition under Rule 158B.'
    },
    {
      title: 'Phytopharmaceutical',
      desc: 'Standardized purified fraction with defined biomarkers',
      icon: Sparkles,
      payload: 'Evaluate a Phytopharmaceutical Drug (standardized fraction with chromatographic biomarkers).'
    },
    {
      title: 'Ayurveda-Aahar',
      desc: 'Nutritional / dietary food under FSSAI 2022 Regs',
      icon: Wheat,
      payload: 'Evaluate an Ayurveda-Aahar dietary food formulation under FSSAI 2022 Regulations.'
    },
    {
      title: 'Ayurvedic Cosmetic',
      desc: 'Topical skincare or haircare Ayurvedic formulation',
      icon: Smile,
      payload: 'Evaluate an Ayurvedic Cosmetic formulation for topical skin/hair application.'
    },
    {
      title: 'Biodiversity & ABS Check',
      desc: 'Biological Diversity Act 2023 approval & exemptions',
      icon: Leaf,
      payload: 'Check Biological Diversity Act 2023 (BDA 2023) Access and Benefit Sharing (ABS) requirements for sourcing Indian herbs.'
    }
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-slate-50 font-sans text-slate-800">
      
      {/* 1. MINIMALIST COLLAPSIBLE SIDEBAR */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-18'
        } bg-white border-r border-slate-200 flex flex-col justify-between transition-all duration-300 z-30 shrink-0 select-none`}
      >
        <div>
          {/* Logo & Toggle Header */}
          <div className="h-16 border-b border-slate-100 px-4 flex items-center justify-between">
            <BrandLogo
              size="sm"
              iconOnly={!sidebarOpen}
              onClick={() => setActiveView('landing')}
              className="cursor-pointer"
            />
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-600 hover:bg-slate-100 transition-all cursor-pointer"
              title={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
              aria-label="Toggle Sidebar"
            >
              {sidebarOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4" />}
            </button>
          </div>

          {/* New Case Button */}
          <div className="p-3">
            <button
              onClick={() => {
                setDrawerOpen(false);
                setInspectorCitation(null);
                setActiveContextAnswer(null);
                handleNewChat();
              }}
              className={`w-full py-2.5 px-3 bg-ayush-forest hover:bg-ayush-forestDark text-white font-bold rounded-xl text-xs flex items-center justify-center space-x-2 shadow-sm transition-all cursor-pointer ${
                !sidebarOpen && 'px-0'
              }`}
            >
              <Plus className="w-4 h-4" />
              {sidebarOpen && <span>New Inquiry</span>}
            </button>
          </div>

          {/* 3 Workspaces Navigation */}
          <nav className="px-3 py-2 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = activeView === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveView(item.id as ActiveView);
                    setDrawerOpen(false);
                    setInspectorCitation(null);
                  }}
                  className={`w-full flex items-center justify-between px-3 py-2.5 rounded-xl text-xs font-bold transition-all cursor-pointer ${
                    isActive
                      ? 'bg-emerald-50 text-ayush-forest border border-emerald-200/80 shadow-2xs'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-transparent'
                  }`}
                  title={!sidebarOpen ? item.label : undefined}
                >
                  <div className="flex items-center space-x-3 truncate">
                    <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-ayush-forest' : 'text-slate-500'}`} />
                    {sidebarOpen && <span className="truncate">{item.label}</span>}
                  </div>
                  {sidebarOpen && item.badge && (
                    <span className={`text-[9px] font-bold px-1.5 py-0.5 rounded ${
                      isActive ? 'bg-emerald-200/70 text-emerald-900' : 'bg-slate-100 text-slate-500'
                    }`}>
                      {item.badge}
                    </span>
                  )}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-slate-100 space-y-2 bg-slate-50/50">
          <button
            onClick={() => setActiveView('dossier')}
            className={`w-full py-2 px-3 rounded-xl border border-slate-200 hover:border-ayush-forest bg-white hover:bg-emerald-50 text-slate-800 text-xs font-bold flex items-center justify-between transition-all shadow-2xs cursor-pointer ${
              !sidebarOpen && 'px-0 justify-center'
            }`}
          >
            <div className="flex items-center space-x-2 truncate">
              <FileCheck className="w-4 h-4 text-ayush-forest shrink-0" />
              {sidebarOpen && <span className="truncate">Active Case Dossier</span>}
            </div>
            {sidebarOpen && activeCase && (
              <span className="font-mono text-[9px] font-bold px-1.5 py-0.5 bg-emerald-100 text-emerald-800 rounded shrink-0">
                {activeCase.caseId}
              </span>
            )}
          </button>

          {sidebarOpen && (
            <div className="text-[10px] text-slate-400 font-semibold text-center pt-1 leading-tight">
              <span>{HACKATHON_ID} · {MINISTRY_NAME}</span>
              <p className="text-[9px] text-slate-400 font-normal mt-0.5">Authoritative Guidance · Not Legal Advice</p>
            </div>
          )}
        </div>
      </aside>

      {/* 2. MAIN APP WORKSPACE */}
      <div className="flex-1 flex flex-col min-w-0 min-h-0 h-full overflow-hidden">
        
        {/* Top Header Bar */}
        <header className="h-16 border-b border-slate-200 bg-white/95 backdrop-blur-md px-5 flex items-center justify-between shrink-0 z-20">
          {/* Workspace Title / Breadcrumb */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 text-xs font-bold text-slate-800">
              <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-600 text-[11px]">
                {activeView === 'copilot' ? '💬 Copilot Canvas' : activeView === 'dossier' ? '📋 Compliance Dossier' : activeView === 'corpus_suite' ? '⚖️ Statutory Corpus & Graph' : 'Observability'}
              </span>
              {activeCase?.productRequest && activeView === 'copilot' && (
                <span className="hidden sm:inline-flex items-center space-x-1 text-[11px] text-emerald-800 bg-emerald-50 px-2 py-0.5 rounded-md border border-emerald-200">
                  <ShieldCheck className="w-3 h-3 text-emerald-600" />
                  <span>Product: {activeCase.productRequest.name}</span>
                </span>
              )}
            </div>
          </div>

          {/* Right Controls: Jurisdiction Toggle (PS 26045 Explicit Requirement) & Bhashini */}
          <div className="flex items-center space-x-3">
            
            {/* Explicit Jurisdiction Switcher */}
            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-[11px] font-bold">
              <button
                onClick={() => setJurisdiction('IN')}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  jurisdiction === 'IN'
                    ? 'bg-white text-slate-900 shadow-2xs border border-slate-200/80'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
                title="Indian domestic regulatory regime (DCA 1940, Patents Act, BDA 2023)"
              >
                🇮🇳 India Domestic
              </button>
              <button
                onClick={() => setJurisdiction('CROSS_BORDER')}
                className={`px-3 py-1 rounded-lg transition-all cursor-pointer ${
                  jurisdiction === 'CROSS_BORDER'
                    ? 'bg-white text-slate-900 shadow-2xs border border-slate-200/80'
                    : 'text-slate-600 hover:text-slate-900'
                }`}
                title="International export & treaty regimes (TRIPS, Nagoya, WIPO GRATK 2024, US FDA, EU THMPD)"
              >
                🌍 International / Export
              </button>
            </div>

            {/* Multilingual Switcher (Bhashini) */}
            <div className="hidden sm:flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-[11px] font-bold">
              <button
                onClick={() => setLanguage('en')}
                className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                  language === 'en' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLanguage('hi')}
                className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                  language === 'hi' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                हिंदी
              </button>
              <button
                onClick={() => setLanguage('sa')}
                className={`px-2.5 py-1 rounded-lg transition-all cursor-pointer ${
                  language === 'sa' ? 'bg-white text-slate-900 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                संस्कृतम्
              </button>
            </div>

          </div>
        </header>

        {/* 3. MAIN WORKSPACE CONTENT PANE */}
        <main className="flex-1 min-h-0 overflow-hidden relative p-4 md:p-6 bg-slate-50/60">
          
          {/* WORKSPACE 1: COPILOT HERO VIEW */}
          {activeView === 'copilot' && (
            <ErrorBoundary fallbackLabel="IP-SAKTI Sahayak Copilot">
              <div className="max-w-3xl mx-auto h-full min-h-0 flex flex-col justify-between space-y-4">
                
                {/* Conversation Stream Area */}
                <div className="flex-1 min-h-0 overflow-y-auto space-y-5 pr-2">
                  {messages.length === 0 ? (
                    <div className="py-6 sm:py-10 text-center space-y-6 max-w-2xl mx-auto animate-fadeIn">
                      
                      {/* Hero Icon & Title */}
                      <div className="space-y-2">
                        <div className="w-12 h-12 rounded-2xl bg-emerald-100/70 text-ayush-forest mx-auto flex items-center justify-center border border-emerald-200 shadow-2xs">
                          <MessageSquare className="w-6 h-6" />
                        </div>
                        <h1 className="text-2xl font-extrabold text-slate-900 font-display">
                          IP-SAKTI Sahayak
                        </h1>
                        <p className="text-xs sm:text-sm text-slate-600 max-w-lg mx-auto leading-relaxed">
                          Your multilingual AI co-counsel for Ayurvedic Intellectual Property (IPR), formulation classification, Section 3(p) patenting bars, and Biological Diversity Act (BDA 2023) ABS compliance.
                        </p>
                      </div>

                      {/* 6 Mandated Statutory Categories (PS 26045) */}
                      <div className="space-y-2 text-left">
                        <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500 block px-1">
                          Select a category to begin guided formulation intake:
                        </span>
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5">
                          {categoryStarters.map((cat, idx) => {
                            const Icon = cat.icon;
                            return (
                              <button
                                key={idx}
                                onClick={() => handleSendMessage(cat.payload)}
                                className="p-3.5 rounded-xl border border-slate-200 hover:border-ayush-forest bg-white hover:bg-emerald-50/50 text-left transition-all group shadow-2xs cursor-pointer"
                              >
                                <div className="flex items-start space-x-2.5">
                                  <div className="p-1.5 rounded-lg bg-emerald-50 text-ayush-forest group-hover:bg-ayush-forest group-hover:text-white transition-colors shrink-0">
                                    <Icon className="w-4 h-4" />
                                  </div>
                                  <div className="space-y-0.5 truncate">
                                    <span className="text-xs font-bold text-slate-800 block truncate group-hover:text-emerald-950">
                                      {cat.title}
                                    </span>
                                    <span className="text-[11px] text-slate-500 font-medium block truncate">
                                      {cat.desc}
                                    </span>
                                  </div>
                                </div>
                              </button>
                            );
                          })}
                        </div>
                      </div>

                    </div>
                  ) : (
                    messages.map((msg, idx) =>
                      msg.sender === 'user' ? (
                        <div key={msg.id} className="flex flex-col space-y-1 items-end animate-fadeIn max-w-xl ml-auto">
                          <div className="rounded-2xl px-4 py-2.5 bg-ayush-forest text-white shadow-2xs">
                            <p className="text-xs sm:text-sm font-semibold leading-relaxed">{msg.text}</p>
                          </div>
                          <span className="text-[10px] text-slate-400 font-medium px-2">
                            {msg.timestamp}
                          </span>
                        </div>
                      ) : (
                        <div key={msg.id} className="flex flex-col space-y-1 items-start w-full animate-fadeIn">
                          <ConversationalAnswer
                            questionText={idx > 0 ? messages[idx - 1]?.text : undefined}
                            answerText={msg.text}
                            answerData={msg.answerData}
                            jurisdiction={msg.answerData?.jurisdiction || jurisdiction}
                            activeCitation={inspectorCitation}
                            drawerOpen={drawerOpen}
                            onOpenCitation={(c, ans) => {
                              setInspectorCitation(c);
                              if (ans) setActiveContextAnswer(ans);
                              setDrawerOpen(true);
                            }}
                            onInspectAllEvidence={(ans) => {
                              if (ans.citations && ans.citations.length > 0) {
                                setInspectorCitation(ans.citations[0]);
                              }
                              setActiveContextAnswer(ans);
                              setDrawerOpen(true);
                            }}
                            onAskFollowUp={(q) => handleSendMessage(q)}
                          />
                          <span className="text-[10px] text-slate-400 font-medium px-2">
                            {msg.timestamp}
                          </span>
                        </div>
                      )
                    )
                  )}

                  {/* Real-time SSE Loading Stage */}
                  {loading && (
                    <div className="p-3.5 rounded-2xl bg-white border border-slate-200 shadow-2xs flex items-center space-x-3 text-xs font-semibold text-slate-700 animate-pulse">
                      <div className="w-4 h-4 border-2 border-ayush-forest border-t-transparent rounded-full animate-spin shrink-0" />
                      <span>{currentStage || 'Analyzing applicable statutory provisions & guidelines...'}</span>
                    </div>
                  )}

                  <div ref={messagesEndRef} />
                </div>

                {/* Chat Input Bar */}
                <div className="pt-2">
                  <div className="bg-white border border-slate-300 focus-within:border-ayush-forest rounded-2xl p-2 shadow-sm flex items-end space-x-2 transition-all">
                    <textarea
                      ref={textareaRef}
                      value={inputQuery}
                      onChange={handleInputChange}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSendMessage();
                        }
                      }}
                      placeholder="Ask IP-SAKTI Sahayak about formulation classification, Section 3(p) patenting bar, ABS, or licensing..."
                      className="flex-1 max-h-32 resize-none bg-transparent px-3 py-1.5 text-xs sm:text-sm focus:outline-none font-medium text-slate-800"
                      rows={1}
                      aria-label="Ask IP-SAKTI Sahayak a question"
                    />
                    <button
                      onClick={() => handleSendMessage()}
                      disabled={!inputQuery.trim() || loading}
                      className="p-2.5 bg-ayush-forest hover:bg-ayush-forestDark disabled:bg-slate-200 text-white rounded-xl transition-all shrink-0 shadow-2xs cursor-pointer disabled:cursor-not-allowed"
                      aria-label="Send message"
                    >
                      <Send className="w-4 h-4" />
                    </button>
                  </div>
                </div>

              </div>
            </ErrorBoundary>
          )}

          {/* WORKSPACE 2: ACTIVE COMPLIANCE DOSSIER VIEW */}
          {activeView === 'dossier' && (
            <ActiveDossierView
              activeCase={activeCase}
              onAskCopilot={(q) => {
                setActiveView('copilot');
                handleSendMessage(q);
              }}
            />
          )}

          {/* WORKSPACE 3: STATUTORY CORPUS & GRAPH SUITE */}
          {activeView === 'corpus_suite' && (
            <EvaluatorCorpusSuite
              onSelectCitation={(c) => {
                setInspectorCitation(c);
                setDrawerOpen(true);
              }}
              onAskCopilot={(q) => {
                setActiveView('copilot');
                handleSendMessage(q);
              }}
            />
          )}

          {/* SECONDARY VIEW: LANDING PAGE */}
          {activeView === 'landing' && (
            <LandingPage
              onStartAssessment={() => setActiveView('copilot')}
              onOpenCopilot={() => setActiveView('copilot')}
              onOpenDossier={() => setActiveView('dossier')}
              onNavigateView={() => setActiveView('corpus_suite')}
              activeCase={activeCase}
            />
          )}

          {/* SECONDARY VIEW: OBSERVABILITY */}
          {activeView === 'observability' && (
            <div className="h-full overflow-y-auto">
              <ObservabilityConsole />
            </div>
          )}

        </main>
      </div>

      {/* 4. ON-DEMAND EVIDENCE & DECISION SUPPORT DRAWER (Only opens on click!) */}
      <AnimatePresence>
        {drawerOpen && (inspectorCitation || activeContextAnswer) && (
          <>
            {/* Backdrop Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => {
                setDrawerOpen(false);
                setInspectorCitation(null);
              }}
              className="fixed inset-0 bg-black/30 backdrop-blur-xs z-40"
            />

            {/* Slide-over Drawer Panel */}
            <motion.div
              initial={{ opacity: 0, x: '100%' }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: '100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 300 }}
              className="fixed inset-y-0 right-0 w-full sm:w-[450px] md:w-[480px] bg-white border-l border-slate-200 shadow-2xl flex flex-col justify-between z-50 select-none overflow-hidden h-full min-h-0"
            >
              <EvidenceInspector
                citation={inspectorCitation || (activeContextAnswer?.citations && activeContextAnswer.citations[0]) || null}
                allCitations={activeContextAnswer?.citations || (inspectorCitation ? [inspectorCitation] : [])}
                activeAnswer={activeContextAnswer}
                jurisdiction={jurisdiction}
                onSelectCitation={(c) => setInspectorCitation(c)}
                onClose={() => {
                  setDrawerOpen(false);
                  setInspectorCitation(null);
                }}
              />
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Citation Modal */}
      <CitationModal
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />

    </div>
  );
}

export default App;
