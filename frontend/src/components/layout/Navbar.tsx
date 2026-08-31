import { useState } from 'react';
import { Shield, Globe, Compass, Scale, Leaf, Search, BookOpen, Menu, X } from 'lucide-react';
import { Jurisdiction } from '../../types';

interface NavbarProps {
  currentTab: string;
  setCurrentTab: (tab: string) => void;
  jurisdiction: Jurisdiction;
  setJurisdiction: (j: Jurisdiction) => void;
  language: string;
  setLanguage: (lang: string) => void;
}

export function Navbar({
  currentTab,
  setCurrentTab,
  jurisdiction,
  setJurisdiction,
  language,
  setLanguage,
}: NavbarProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { id: 'home', label: 'Overview', icon: Shield },
    { id: 'product-journey', label: 'Product Classification', icon: Compass },
    { id: 'ip-matrix', label: 'IP Opportunity Matrix', icon: Scale },
    { id: 'abs', label: 'ABS & Biodiversity', icon: Leaf },
    { id: 'chat', label: 'Ask AyuRaksha (RAG)', icon: Search },
    { id: 'corpus', label: 'Statutory Corpus', icon: BookOpen },
  ];

  return (
    <header className="bg-white border-b border-ayush-border sticky top-0 z-40 shadow-subtle">
      {/* Top Banner: Official Hackathon & Ministry Context */}
      <div className="bg-ayush-forestDark text-white px-4 py-1.5 text-xs font-medium">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-1">
          <div className="flex items-center space-x-2">
            <span className="bg-ayush-forest text-emerald-200 px-2 py-0.5 rounded text-[11px] font-bold tracking-wider uppercase">
              SIH 26045
            </span>
            <span className="text-slate-200">
              Ministry of Ayush & AIIA · IP-SAKTI Sahayak
            </span>
          </div>

          <div className="flex items-center space-x-4">
            {/* Language Selector */}
            <div className="flex items-center space-x-1">
              <span className="text-slate-400 text-[11px]">Language:</span>
              <button
                onClick={() => setLanguage('en')}
                className={`px-1.5 py-0.5 rounded text-[11px] font-semibold ${
                  language === 'en' ? 'bg-white text-ayush-forestDark' : 'text-slate-300 hover:text-white'
                }`}
              >
                EN
              </button>
              <button
                onClick={() => setLanguage('hi')}
                className={`px-1.5 py-0.5 rounded text-[11px] font-semibold ${
                  language === 'hi' ? 'bg-white text-ayush-forestDark' : 'text-slate-300 hover:text-white'
                }`}
              >
                हिन्दी
              </button>
            </div>

            {/* Jurisdiction Firewall Switcher */}
            <div className="flex items-center space-x-1.5 bg-black/30 px-2 py-0.5 rounded border border-white/10">
              <Globe className="w-3 h-3 text-ayush-saffron" />
              <span className="text-[11px] text-slate-300">Jurisdiction:</span>
              <select
                value={jurisdiction}
                onChange={(e) => setJurisdiction(e.target.value as Jurisdiction)}
                className="bg-transparent text-white text-[11px] font-bold focus:outline-none cursor-pointer"
              >
                <option value="IN" className="text-black">🇮🇳 India (IN)</option>
                <option value="INT" className="text-black">🌎 International (INT)</option>
                <option value="CROSS_BORDER" className="text-black">🌐 Cross-Border</option>
              </select>
            </div>
          </div>
        </div>
      </div>

      {/* Main Navigation Bar */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo & Brand Identity */}
          <div
            onClick={() => setCurrentTab('home')}
            className="flex items-center space-x-3 cursor-pointer group"
          >
            <div className="w-10 h-10 bg-ayush-forest rounded-xl flex items-center justify-center text-white shadow-card group-hover:bg-ayush-forestDark transition-colors">
              <Shield className="w-6 h-6 text-emerald-300" />
            </div>
            <div>
              <div className="flex items-center space-x-1.5">
                <span className="font-extrabold text-lg text-ayush-forestDark tracking-tight">
                  AyuRaksha
                </span>
                <span className="text-[10px] font-bold bg-amber-100 text-amber-900 px-1.5 py-0.2 rounded border border-amber-300">
                  DECISION ENGINE
                </span>
              </div>
              <p className="text-[11px] text-ayush-slate font-medium">
                AI IP & Regulatory Navigator for Ayurvedic Innovation
              </p>
            </div>
          </div>

          {/* Desktop Navigation Tabs */}
          <nav className="hidden lg:flex items-center space-x-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentTab === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => setCurrentTab(item.id)}
                  className={`flex items-center space-x-2 px-3.5 py-2 rounded-lg text-xs font-bold transition-all ${
                    isActive
                      ? 'bg-ayush-forest text-white shadow-subtle'
                      : 'text-slate-600 hover:text-ayush-forestDark hover:bg-slate-100'
                  }`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-emerald-300' : 'text-slate-500'}`} />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </nav>

          {/* Mobile Menu Button */}
          <div className="lg:hidden">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="p-2 rounded-lg text-slate-600 hover:bg-slate-100 focus:outline-none"
            >
              {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div className="lg:hidden bg-white border-b border-ayush-border px-4 pt-2 pb-4 space-y-1">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => {
                  setCurrentTab(item.id);
                  setMobileMenuOpen(false);
                }}
                className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-semibold ${
                  isActive
                    ? 'bg-ayush-forest text-white'
                    : 'text-slate-700 hover:bg-slate-100'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
}
