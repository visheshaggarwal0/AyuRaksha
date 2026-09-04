import React, { createContext, useContext, useState } from 'react';
import { translations, Language } from './translations';

interface LanguageContextType {
  language: Language;
  setLanguage: (lang: Language) => void;
  t: (key: string) => string;
}

const LanguageContext = createContext<LanguageContextType | undefined>(undefined);

export const LanguageProvider: React.FC<{children: React.ReactNode}> = ({ children }) => {
  // Try to load from localStorage, otherwise default to 'en'
  const [language, setLanguageState] = useState<Language>(() => {
    const saved = localStorage.getItem('ayuraksha_lang');
    return (saved === 'en' || saved === 'hi' || saved === 'sa') ? saved : 'en';
  });

  const setLanguage = (lang: Language) => {
    setLanguageState(lang);
    localStorage.setItem('ayuraksha_lang', lang);
  };

  const t = (key: string): string => {
    const keys = key.split('.');
    
    // Helper to traverse object
    const traverse = (obj: any, path: string[]) => {
      return path.reduce((acc, curr) => (acc && acc[curr] !== undefined) ? acc[curr] : undefined, obj);
    };

    // Try target language
    let value = traverse(translations[language], keys);
    
    // Fallback to English
    if (value === undefined && language !== 'en') {
      value = traverse(translations['en'], keys);
    }
    
    return value !== undefined ? value : key;
  };

  return (
    <LanguageContext.Provider value={{ language, setLanguage, t }}>
      {children}
    </LanguageContext.Provider>
  );
};

export const useTranslation = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useTranslation must be used within a LanguageProvider');
  }
  return context;
};
