import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import {
  Home,
  Compass,
  MessageSquare,
  Scale,
  Leaf,
  Globe,
  Network,
  BookOpen,
  Send,
  PanelLeftClose,
  PanelLeftOpen,
  FileCheck,
  Plus,
  Sparkles,
  ShieldCheck,
  ArrowRight
} from 'lucide-react';
import { api } from './services/api';
import {
  Citation,
  StructuredAnswer,
  Jurisdiction,
  ActiveCaseState,
  InnovationProfile,
  ProductClassificationRequest,
  ProductClassificationResponse,
  ABSAssessmentRequest,
  ABSAssessmentResponse
} from './types';
import { LandingPage } from './components/landing/LandingPage';
import { ProductJourneyWizard } from './components/wizards/ProductJourneyWizard';
import { IPMatrixView } from './components/cards/IPMatrixView';
import { ABSWizard } from './components/wizards/ABSWizard';
import { CitationModal } from './components/modals/CitationModal';
import { BrandLogo } from './components/common/BrandLogo';
import { BrandWordmark } from './components/common/BrandWordmark';
import { DecisionBriefAnswer } from './components/chat/DecisionBriefAnswer';
import { InnovationDiscoveryWorkflow } from './components/wizards/InnovationDiscoveryWorkflow';
import { EvidenceInspector } from './components/evidence/EvidenceInspector';
import { InitialLoadingScreen } from './components/common/InitialLoadingScreen';
import { BRAND_NAME, HACKATHON_ID, MINISTRY_NAME } from './constants/branding';

// Dynamic code-splitting for heavy non-critical modules
const InternationalView = React.lazy(() =>
  import('./components/international/InternationalView').then((m) => ({ default: m.InternationalView }))
);
const CorpusExplorer = React.lazy(() =>
  import('./components/corpus/CorpusExplorer').then((m) => ({ default: m.CorpusExplorer }))
);
const KnowledgeGraphExplorer = React.lazy(() =>
  import('./components/graph/KnowledgeGraphExplorer').then((m) => ({ default: m.KnowledgeGraphExplorer }))
);
const ComplianceDossierModal = React.lazy(() =>
  import('./components/common/ComplianceDossierModal').then((m) => ({ default: m.ComplianceDossierModal }))
);

interface ChatMessage {
  id: string;
  sender: 'user' | 'assistant';
  text: string;
  timestamp: string;
  answerData?: StructuredAnswer;
}

type ActiveView = 'landing' | 'classification' | 'chat' | 'ip_matrix' | 'abs_wizard' | 'international' | 'corpus' | 'knowledge_graph';

export function App() {
  const [appInitializing, setAppInitializing] = useState(true);
  const [isAppReady, setIsAppReady] = useState(false);
  const [activeView, setActiveView] = useState<ActiveView>('landing');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [jurisdiction, setJurisdiction] = useState<Jurisdiction>('IN');
  const [language, setLanguage] = useState<'en' | 'hi' | 'sa'>('en');
  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedCitation, setSelectedCitation] = useState<Citation | null>(null);
  const [inspectorCitation, setInspectorCitation] = useState<Citation | null>(null);
  const [activeContextAnswer, setActiveContextAnswer] = useState<StructuredAnswer | null>(null);
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [isDossierOpen, setIsDossierOpen] = useState(false);
  const [currentStage, setCurrentStage] = useState<string | null>(null);

  useEffect(() => {
    // Authentically check statutory corpus / backend health
    api.getCorpusStats()
      .then(() => setIsAppReady(true))
      .catch(() => setIsAppReady(true));
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

  const handleClassificationComplete = (req: ProductClassificationRequest, res: ProductClassificationResponse) => {
    updateActiveCase((prev) => {
      const now = new Date().toISOString();
      const caseId = prev?.caseId || `AYR-2026-${Math.floor(1000 + Math.random() * 9000)}`;
      return {
        caseId,
        createdAt: prev?.createdAt || now,
        updatedAt: now,
        productRequest: req,
        classificationResult: res,
        absRequest: prev?.absRequest || null,
        absResult: prev?.absResult || null,
        recentCitations: res.citations || [],
        status: 'EVALUATED'
      };
    });
  };

  const handleABSComplete = (req: ABSAssessmentRequest, res: ABSAssessmentResponse) => {
    updateActiveCase((prev) => {
      const now = new Date().toISOString();
      const caseId = prev?.caseId || `AYR-2026-${Math.floor(1000 + Math.random() * 9000)}`;
      return {
        caseId,
        createdAt: prev?.createdAt || now,
        updatedAt: now,
        productRequest: prev?.productRequest || null,
        classificationResult: prev?.classificationResult || null,
        absRequest: req,
        absResult: res,
        innovationProfile: prev?.innovationProfile || null,
        recentCitations: [...(prev?.recentCitations || []), ...(res.statutory_citations || [])],
        status: prev?.status || 'ACTIVE'
      };
    });
  };

  const [chatMode, setChatMode] = useState<'copilot' | 'innovation_discovery'>('copilot');

  const handleInnovationComplete = (profile: InnovationProfile) => {
    updateActiveCase((prev) => {
      const now = new Date().toISOString();
      const caseId = prev?.caseId || `AYR-2026-${Math.floor(1000 + Math.random() * 9000)}`;
      const productReq: ProductClassificationRequest = prev?.productRequest || {
        name: profile.productName,
        in_classical_text: profile.isTraditionalKnowledge === 'YES',
        is_formulation_modified: profile.isTraditionalKnowledge !== 'YES',
        has_novel_excipients: false,
        is_purified_standardized_fraction: false,
        intended_use: 'therapeutic',
        disease_treatment_claims: true,
        has_biological_resources: true,
        target_market: profile.targetJurisdiction || 'IN'
      };
      return {
        caseId,
        createdAt: prev?.createdAt || now,
        updatedAt: now,
        productRequest: productReq,
        classificationResult: prev?.classificationResult || null,
        absRequest: prev?.absRequest || null,
        absResult: prev?.absResult || null,
        innovationProfile: profile,
        recentCitations: prev?.recentCitations || [],
        status: prev?.status === 'EVALUATED' ? 'EVALUATED' : 'ACTIVE'
      };
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
    setActiveView('chat');
  };

  const handleSendMessage = async (queryText?: string) => {
    const textToSend = queryText || inputQuery;
    if (!textToSend.trim() || loading) return;

    if (activeView !== 'chat') {
      setActiveView('chat');
    }

    // Reset previous drawer context for each new question
    setDrawerOpen(false);
    setInspectorCitation(null);
    setActiveContextAnswer(null);

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
    setCurrentStage('Understanding your question & detecting statutory jurisdiction...');

    const assistantMsgId = (Date.now() + 1).toString();
    let accumulatedText = '';

    await api.streamChatQuery(
      textToSend,
      jurisdiction,
      language,
      (stageData) => {
        const msg = stageData.message || '';
        if (msg.toLowerCase().includes('bhashini') || msg.toLowerCase().includes('language')) {
          setCurrentStage('Understanding your question & verifying language...');
        } else if (msg.toLowerCase().includes('router') || msg.toLowerCase().includes('intent')) {
          setCurrentStage('Reviewing applicable legal acts & First Schedule texts...');
        } else if (msg.toLowerCase().includes('retrieval') || msg.toLowerCase().includes('vector')) {
          setCurrentStage('Retrieving authoritative statutory provisions & citations...');
        } else if (msg.toLowerCase().includes('rerank') || msg.toLowerCase().includes('section')) {
          setCurrentStage('Checking Section 3(p) patentability & ABS compliance requirements...');
        } else if (msg.toLowerCase().includes('verifier') || msg.toLowerCase().includes('claim')) {
          setCurrentStage('Verifying regulatory citations & grounding evidence...');
        } else {
          setCurrentStage(msg);
        }
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

        // Contextual Drawer: Automatically open supporting drawer if contextual material is available
        const hasContextualMaterial =
          (structuredResult.citations && structuredResult.citations.length > 0) ||
          (structuredResult.verified_claims && structuredResult.verified_claims.length > 0) ||
          Boolean(structuredResult.recommended_next_action);

        if (hasContextualMaterial) {
          setActiveContextAnswer(structuredResult);
          if (structuredResult.citations && structuredResult.citations.length > 0) {
            setInspectorCitation(structuredResult.citations[0]);
          }
          setDrawerOpen(true);
        }
      },
      async (err) => {
        console.warn('Stream fallback to sync query:', err);
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

          if (fallback) {
            const hasContextualMaterial =
              (fallback.citations && fallback.citations.length > 0) ||
              (fallback.verified_claims && fallback.verified_claims.length > 0) ||
              Boolean(fallback.recommended_next_action);

            if (hasContextualMaterial) {
              setActiveContextAnswer(fallback);
              if (fallback.citations && fallback.citations.length > 0) {
                setInspectorCitation(fallback.citations[0]);
              }
              setDrawerOpen(true);
            }
          }
        } catch (syncErr: any) {
          console.error('Query error:', syncErr);
          setMessages((prev) => [
            ...prev,
            {
              id: assistantMsgId,
              sender: 'assistant',
              text: 'Unable to retrieve statutory information. Please ensure backend services are active.',
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
            }
          ]);
        } finally {
          setCurrentStage(null);
        }
      }
    );

    setLoading(false);
  };

  const navItems = [
    { id: 'landing', label: 'Home', icon: Home },
    { id: 'classification', label: 'Assess Product', icon: Compass },
    { id: 'chat', label: `Ask ${BRAND_NAME}`, icon: MessageSquare },
    { id: 'ip_matrix', label: 'IP Strategy', icon: Scale },
    { id: 'abs_wizard', label: 'ABS Navigator', icon: Leaf },
    { id: 'international', label: 'International', icon: Globe },
    { id: 'knowledge_graph', label: 'Knowledge Connections', icon: Network },
    { id: 'corpus', label: 'Statutory Corpus', icon: BookOpen },
  ];

  return (
    <div className="flex h-screen w-screen overflow-hidden bg-ayush-canvas text-ayush-navy font-sans antialiased relative">
      {/* 0. BRANDED INITIAL LOADING SCREEN */}
      {appInitializing && (
        <InitialLoadingScreen
          isReady={isAppReady}
          onComplete={() => setAppInitializing(false)}
        />
      )}

      {/* 1. LEFT SIDEBAR */}
      <aside
        className={`h-full bg-white border-r border-slate-200 transition-all duration-300 flex flex-col justify-between z-30 shrink-0 select-none ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}
      >
        <div className="flex flex-col h-full overflow-y-auto">
          {/* Brand Header */}
          <div className="p-4 border-b border-slate-100 flex items-center justify-between">
            {sidebarOpen ? (
              <BrandLogo
                size="lg"
                showSubtitle={true}
                onClick={() => {
                  setActiveView('landing');
                  setDrawerOpen(false);
                  setInspectorCitation(null);
                  setActiveContextAnswer(null);
                }}
              />
            ) : (
              <BrandLogo
                size="md"
                iconOnly={true}
                onClick={() => {
                  setActiveView('landing');
                  setDrawerOpen(false);
                  setInspectorCitation(null);
                  setActiveContextAnswer(null);
                }}
              />
            )}
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-1.5 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              title={sidebarOpen ? 'Collapse Sidebar' : 'Expand Sidebar'}
            >
              {sidebarOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeftOpen className="w-4 h-4" />}
            </button>
          </div>

          {/* New Assessment / New Chat Quick Button */}
          <div className="p-3">
            <button
              onClick={() => {
                setDrawerOpen(false);
                setInspectorCitation(null);
                setActiveContextAnswer(null);
                if (activeView === 'chat') {
                  handleNewChat();
                } else {
                  setActiveView('classification');
                }
              }}
              className={`w-full py-2.5 px-3 bg-ayush-forest hover:bg-ayush-forestDark text-white font-bold rounded-xl text-xs flex items-center justify-center space-x-2 shadow-subtle transition-all ${
                !sidebarOpen && 'px-0'
              }`}
            >
              <Plus className="w-4 h-4" />
              {sidebarOpen && <span>{activeView === 'chat' ? 'New Inquiry' : 'New Assessment'}</span>}
            </button>
          </div>

          {/* Navigation Items */}
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
                    setActiveContextAnswer(null);
                  }}
                  className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-xl text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-emerald-50 text-ayush-forest border border-emerald-200/80 shadow-subtle'
                      : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-transparent'
                  }`}
                  title={!sidebarOpen ? item.label : undefined}
                >
                  <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-ayush-forest' : 'text-slate-500'}`} />
                  {sidebarOpen && <span className="truncate">{item.label}</span>}
                </button>
              );
            })}
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="p-3 border-t border-slate-100 space-y-2 bg-slate-50/50">
          <button
            onClick={() => setIsDossierOpen(true)}
            className={`w-full py-2 px-3 rounded-xl border border-slate-200 hover:border-ayush-forest bg-white hover:bg-emerald-50 text-slate-800 text-xs font-bold flex items-center justify-between transition-all shadow-subtle ${
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
            <div className="text-[10px] text-slate-400 font-semibold text-center pt-1">
              {HACKATHON_ID} · {MINISTRY_NAME}
            </div>
          )}
        </div>
      </aside>

      {/* 2. MAIN APP WORKSPACE */}
      <div className="flex-1 flex flex-col min-w-0 min-h-0 h-full overflow-hidden">
        
        {/* Top Header Bar */}
        <header className="h-16 border-b border-slate-200 bg-white/95 backdrop-blur-md px-5 flex items-center justify-between shrink-0 z-20">
          {/* Breadcrumb / Journey Indicator */}
          <div className="flex items-center space-x-3">
            <BrandWordmark size="xs" className="hidden sm:inline-flex" />
            {activeView !== 'landing' && (
              <>
                <span className="text-slate-300 hidden sm:inline">/</span>
                <div className="flex items-center space-x-1.5 text-xs font-bold text-slate-700">
                  <span className="capitalize">
                    {activeView === 'chat'
                      ? `Ask ${BRAND_NAME}`
                      : activeView === 'classification'
                      ? 'Assess Product'
                      : activeView === 'ip_matrix'
                      ? 'IP Strategy'
                      : activeView === 'abs_wizard'
                      ? 'ABS Navigator'
                      : activeView === 'knowledge_graph'
                      ? 'Knowledge Connections'
                      : activeView === 'corpus'
                      ? 'Statutory Corpus'
                      : activeView.replace('_', ' ')}
                  </span>
                </div>
              </>
            )}
          </div>

          {/* Right Controls: Bhashini Language & Assessment Jurisdiction */}
          <div className="flex items-center space-x-3">
            {/* Multilingual Switcher (Bhashini) */}
            <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-[11px] font-bold">
              <button
                onClick={() => setLanguage('en')}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  language === 'en' ? 'bg-white text-slate-900 shadow-subtle' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                English
              </button>
              <button
                onClick={() => setLanguage('hi')}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  language === 'hi' ? 'bg-white text-slate-900 shadow-subtle' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                हिंदी
              </button>
              <button
                onClick={() => setLanguage('sa')}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  language === 'sa' ? 'bg-white text-slate-900 shadow-subtle' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                संस्कृतम्
              </button>
            </div>

            {/* Assessment Jurisdiction Selector */}
            <div className="hidden md:flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-[11px] font-bold">
              <button
                onClick={() => setJurisdiction('IN')}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  jurisdiction === 'IN' ? 'bg-white text-slate-900 shadow-subtle' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                🇮🇳 India
              </button>
              <button
                onClick={() => setJurisdiction('CROSS_BORDER')}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  jurisdiction === 'CROSS_BORDER' ? 'bg-ayush-forest text-white shadow-subtle' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                ⚖️ Cross-Border
              </button>
              <button
                onClick={() => setJurisdiction('INT')}
                className={`px-2.5 py-1 rounded-lg transition-all ${
                  jurisdiction === 'INT' ? 'bg-white text-slate-900 shadow-subtle' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                🌍 International
              </button>
            </div>
          </div>
        </header>

        {/* Content Body Routing */}
        <main className="flex-1 min-w-0 min-h-0 overflow-y-auto p-4 sm:p-6 relative">
          
          {/* 1. LANDING PAGE VIEW */}
          {activeView === 'landing' && (
            <LandingPage
              activeCase={activeCase}
              onStartAssessment={() => setActiveView('classification')}
              onOpenCopilot={(prompt) => {
                if (prompt) {
                  handleSendMessage(prompt);
                } else {
                  setActiveView('chat');
                }
              }}
              onNavigateView={(v) => setActiveView(v as ActiveView)}
              onOpenDossier={() => setIsDossierOpen(true)}
            />
          )}

          {/* 2. CLASSIFICATION WIZARD VIEW */}
          {activeView === 'classification' && (
            <ProductJourneyWizard
              activeCase={activeCase}
              jurisdiction={jurisdiction}
              onOpenCitation={(c) => {
                setInspectorCitation(c);
                setDrawerOpen(true);
              }}
              onNavigateView={(v) => setActiveView(v as ActiveView)}
              onOpenDossier={() => setIsDossierOpen(true)}
              onClassificationComplete={handleClassificationComplete}
              onAskCopilot={(q) => handleSendMessage(q)}
            />
          )}

          {/* 3. IP OPPORTUNITY MATRIX VIEW */}
          {activeView === 'ip_matrix' && (
            <IPMatrixView
              activeCase={activeCase}
              onOpenCitation={(c) => {
                setInspectorCitation(c);
                setDrawerOpen(true);
              }}
              onAskCopilot={(q) => handleSendMessage(q)}
            />
          )}

          {/* 4. ABS COMPLIANCE VIEW */}
          {activeView === 'abs_wizard' && (
            <ABSWizard
              activeCase={activeCase}
              onOpenCitation={(c) => {
                setInspectorCitation(c);
                setDrawerOpen(true);
              }}
              onABSComplete={handleABSComplete}
              onNavigateView={(v) => setActiveView(v as ActiveView)}
              onAskCopilot={(q) => handleSendMessage(q)}
              onOpenDossier={() => setIsDossierOpen(true)}
            />
          )}

          {/* 5. INTERNATIONAL VIEW */}
          {activeView === 'international' && (
            <React.Suspense fallback={<div className="p-12 text-center text-xs text-slate-400 font-mono">Loading International Regulatory Module...</div>}>
              <InternationalView
                onOpenCitation={(c) => {
                  setInspectorCitation(c);
                  setDrawerOpen(true);
                }}
                onAskCopilot={(q) => handleSendMessage(q)}
              />
            </React.Suspense>
          )}

          {/* 6. STATUTORY CORPUS EXPLORER */}
          {activeView === 'corpus' && (
            <React.Suspense fallback={<div className="p-12 text-center text-xs text-slate-400 font-mono">Loading Statutory Corpus...</div>}>
              <CorpusExplorer />
            </React.Suspense>
          )}

          {/* 7. KNOWLEDGE GRAPH EXPLORER */}
          {activeView === 'knowledge_graph' && (
            <div className="h-full min-h-0">
              <React.Suspense fallback={<div className="p-12 text-center text-xs text-slate-400 font-mono">Loading Knowledge Graph...</div>}>
                <KnowledgeGraphExplorer
                  onSelectCitation={(c) => {
                    setInspectorCitation(c);
                    setDrawerOpen(true);
                  }}
                  onAskCopilot={(q) => handleSendMessage(q)}
                />
              </React.Suspense>
            </div>
          )}

          {/* 8. ASK AYUरक्षा (COPILOT & INNOVATION DISCOVERY) VIEW */}
          {activeView === 'chat' && (
            <div className="max-w-4xl mx-auto h-full min-h-0 flex flex-col justify-between space-y-4">
              
              {/* Mode Switcher Pill */}
              <div className="flex items-center justify-between pb-2 border-b border-slate-200 shrink-0">
                <div className="flex items-center space-x-1.5 p-1 bg-slate-100 rounded-xl border border-slate-200/80 text-xs font-bold">
                  <button
                    onClick={() => setChatMode('copilot')}
                    className={`px-3 py-1.5 rounded-lg transition-all flex items-center space-x-1.5 ${
                      chatMode === 'copilot'
                        ? 'bg-white text-slate-900 shadow-subtle'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <MessageSquare className="w-3.5 h-3.5 text-ayush-forest" />
                    <span>Statutory Copilot</span>
                  </button>
                  <button
                    onClick={() => setChatMode('innovation_discovery')}
                    className={`px-3 py-1.5 rounded-lg transition-all flex items-center space-x-1.5 ${
                      chatMode === 'innovation_discovery'
                        ? 'bg-ayush-forest text-white shadow-subtle'
                        : 'text-slate-600 hover:text-slate-900'
                    }`}
                  >
                    <Sparkles className="w-3.5 h-3.5 text-emerald-200" />
                    <span>Innovation Discovery Guide</span>
                  </button>
                </div>

                {activeCase?.productRequest && (
                  <span className="text-[10px] font-bold text-slate-600 bg-slate-100 px-2.5 py-1 rounded-lg border border-slate-200 hidden sm:inline-flex items-center space-x-1.5">
                    <ShieldCheck className="w-3.5 h-3.5 text-emerald-600" />
                    <span>Active Case: {activeCase.productRequest.name}</span>
                  </span>
                )}
              </div>

              {chatMode === 'innovation_discovery' ? (
                <div className="flex-1 min-h-0 overflow-y-auto pr-2 pb-4">
                  <InnovationDiscoveryWorkflow
                    initialProductName={activeCase?.productRequest?.name || ''}
                    jurisdiction={jurisdiction}
                    onComplete={handleInnovationComplete}
                    onNavigateView={(v) => setActiveView(v as ActiveView)}
                    onAskCopilot={(q) => {
                      setChatMode('copilot');
                      handleSendMessage(q);
                    }}
                  />
                </div>
              ) : (
                <>
                  {/* Conversation Stream Area */}
                  <div className="flex-1 min-h-0 overflow-y-auto space-y-5 pr-2">
                    {messages.length === 0 ? (
                      <div className="py-10 text-center space-y-4 max-w-xl mx-auto animate-fadeIn">
                        <div className="w-12 h-12 rounded-2xl bg-emerald-50 text-ayush-forest mx-auto flex items-center justify-center border border-emerald-200 shadow-subtle">
                          <MessageSquare className="w-6 h-6" />
                        </div>
                        <div>
                          <h2 className="text-xl font-extrabold text-slate-900 font-display">
                            Ask {BRAND_NAME} Copilot
                          </h2>
                          <p className="text-xs text-slate-600 mt-1 leading-relaxed">
                            Inquire about Ayurvedic product patentability under Section 3(p), Rule 158B licensing requirements, Biological Diversity Act (BDA 2023) ABS obligations, or US FDA / EU export pathways.
                          </p>
                        </div>

                        {/* Active Product Context Banner */}
                        {activeCase?.productRequest && (
                          <div className="p-3 rounded-2xl bg-emerald-50/70 border border-emerald-200 text-left space-y-1">
                            <span className="text-[10px] font-black uppercase tracking-wider text-ayush-forest block">
                              Active Case Context Detected
                            </span>
                            <p className="text-xs font-semibold text-emerald-950">
                              Product: <strong>{activeCase.productRequest.name}</strong> ({activeCase.classificationResult?.category || 'Evaluating'}) · Jurisdiction: <strong>{jurisdiction === 'IN' ? 'India' : 'Cross-Border'}</strong>
                            </p>
                          </div>
                        )}

                        {/* Direct Innovation Discovery Button */}
                        <div className="pt-1">
                          <button
                            onClick={() => setChatMode('innovation_discovery')}
                            className="w-full p-3.5 rounded-2xl bg-emerald-950 text-white hover:bg-slate-900 transition-all text-xs font-bold flex items-center justify-between shadow-subtle border border-emerald-800/80"
                          >
                            <div className="flex items-center space-x-2.5 text-left">
                              <div className="p-1.5 bg-emerald-800 text-emerald-200 rounded-lg">
                                <Sparkles className="w-4 h-4" />
                              </div>
                              <div>
                                <span className="block font-extrabold text-white text-xs">
                                  New Formulation or Process? Start Innovation Discovery
                                </span>
                                <span className="text-[11px] text-slate-300 font-normal">
                                  Establish technical baseline, differences, and experimental evidence step-by-step
                                </span>
                              </div>
                            </div>
                            <ArrowRight className="w-4 h-4 text-emerald-400 shrink-0 ml-2" />
                          </button>
                        </div>

                        {/* Dynamic Grounded Prompts */}
                        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 pt-1 text-left">
                          {(activeCase?.productRequest
                            ? [
                                `What is the patentability of ${activeCase.productRequest.name} under Section 3(p)?`,
                                `What licensing proofs are needed under Rule 158B for ${activeCase.productRequest.name}?`,
                                `What are my ABS obligations under BDA 2023 for the biological herbs in ${activeCase.productRequest.name}?`,
                                `How to export ${activeCase.productRequest.name} under US FDA DSHEA / EU THMPD?`
                              ]
                            : [
                                'Can I patent an Ayurvedic formulation of Ashwagandha and Guduchi for arthritis?',
                                'What are my ABS obligations under BDA 2023 for sourcing Kutki from Himachal Pradesh?',
                                'What is the difference between Classical Shastriya and Proprietary ASU licensing?',
                                'How do I comply with US FDA DSHEA when exporting Ayurvedic herbal supplements?'
                              ]
                          ).map((prompt, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleSendMessage(prompt)}
                              className="p-3 rounded-xl border border-slate-200 hover:border-ayush-forest bg-white hover:bg-emerald-50/50 text-xs font-semibold text-slate-800 transition-all text-left shadow-subtle"
                            >
                              {prompt}
                            </button>
                          ))}
                        </div>
                      </div>
                    ) : (
                  messages.map((msg) =>
                    msg.sender === 'user' ? (
                      <div key={msg.id} className="flex flex-col space-y-1.5 items-end animate-fadeIn max-w-2xl ml-auto">
                        <div className="rounded-2xl px-5 py-3 bg-ayush-forest text-white shadow-subtle">
                          <p className="text-xs sm:text-sm font-semibold leading-relaxed">{msg.text}</p>
                        </div>
                        <span className="text-[10px] text-slate-400 font-medium px-2">
                          {msg.timestamp}
                        </span>
                      </div>
                    ) : (
                      <div key={msg.id} className="flex flex-col space-y-1.5 items-start w-full animate-fadeIn">
                        <DecisionBriefAnswer
                          questionText={messages[messages.findIndex((m) => m.id === msg.id) - 1]?.text}
                          answerText={msg.text}
                          answerData={msg.answerData}
                          jurisdiction={msg.answerData?.jurisdiction || jurisdiction}
                          activeCitation={inspectorCitation}
                          drawerOpen={drawerOpen}
                          onOpenCitation={(c, ans) => {
                            setInspectorCitation(c);
                            if (ans) {
                              setActiveContextAnswer(ans);
                            }
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
                  <div className="p-4 rounded-2xl bg-white border border-slate-200 shadow-subtle flex items-center space-x-3 text-xs font-semibold text-slate-700 animate-pulse">
                    <div className="w-4 h-4 border-2 border-ayush-forest border-t-transparent rounded-full animate-spin shrink-0" />
                    <span>{currentStage || 'Synthesizing statutory citations & evidence...'}</span>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Chat Input Bar */}
              <div className="pt-2">
                <div className="bg-white border border-slate-300 focus-within:border-ayush-forest rounded-2xl p-2.5 shadow-card flex items-end space-x-2 transition-all">
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
                    placeholder={`Ask ${BRAND_NAME} about Ayurvedic product classification, patentability under Sec 3(p), ABS, or export rules...`}
                    className="flex-1 max-h-32 resize-none bg-transparent px-3 py-1.5 text-xs sm:text-sm focus:outline-none font-medium text-slate-800"
                    rows={1}
                  />
                  <button
                    onClick={() => handleSendMessage()}
                    disabled={!inputQuery.trim() || loading}
                    className="p-2.5 bg-ayush-forest hover:bg-ayush-forestDark disabled:bg-slate-200 text-white rounded-xl transition-all shrink-0 shadow-subtle"
                  >
                    <Send className="w-4 h-4" />
                  </button>
                </div>
              </div>
            </>
          )}
        </div>
      )}

        </main>
      </div>

      {/* 3. RIGHT-SIDE CONTEXTUAL EVIDENCE & DECISION SUPPORT DRAWER */}
      <AnimatePresence>
        {drawerOpen && (inspectorCitation || activeContextAnswer) && (
          <>
            {/* Mobile Backdrop Overlay */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => {
                setDrawerOpen(false);
                setInspectorCitation(null);
              }}
              className="fixed inset-0 bg-black/40 backdrop-blur-xs z-40 md:hidden"
            />

            {/* Slide-over Drawer Panel */}
            <motion.div
              initial={{ opacity: 0, x: '100%' }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: '100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 300 }}
              className="fixed md:relative inset-y-0 right-0 w-full sm:w-96 md:w-96 lg:w-[420px] bg-white border-l border-slate-200 shadow-2xl md:shadow-modal flex flex-col justify-between z-50 md:z-30 shrink-0 select-none overflow-hidden h-full min-h-0"
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

      {/* 4. MODALS */}
      <CitationModal
        citation={selectedCitation}
        onClose={() => setSelectedCitation(null)}
      />

      {isDossierOpen && (
        <React.Suspense fallback={null}>
          <ComplianceDossierModal
            isOpen={isDossierOpen}
            onClose={() => setIsDossierOpen(false)}
            activeCase={activeCase}
            onStartAssessment={() => setActiveView('classification')}
            onOpenCitation={(c) => {
              setIsDossierOpen(false);
              setInspectorCitation(c);
              setDrawerOpen(true);
            }}
          />
        </React.Suspense>
      )}

    </div>
  );
}

export default App;
