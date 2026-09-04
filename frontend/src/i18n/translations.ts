export type Language = 'en' | 'hi' | 'sa';

export const translations = {
  en: {
    nav: {
      overview: 'Overview',
      productClassification: 'Product Classification',
      ipMatrix: 'IP Opportunity Matrix',
      abs: 'ABS & Biodiversity',
      askAyuraksha: 'Ask AyuRaksha (RAG)',
      corpus: 'Statutory Corpus',
    },
    topBanner: {
      ministry: 'Ministry of Ayush & AIIA · IP-SAKTI Sahayak',
      language: 'Language:',
      jurisdiction: 'Jurisdiction:',
      india: '🇮🇳 India (IN)',
      international: '🌎 International (INT)',
      crossBorder: '🌐 Cross-Border',
    },
    brand: {
      title: 'AyuRaksha',
      badge: 'DECISION ENGINE',
      subtitle: 'AI IP & Regulatory Navigator for Ayurvedic Innovation',
    },
    app: {
      complianceDossier: 'Compliance Dossier',
      heroTitleLine1: 'Ayurvedic IP &',
      heroTitleLine2: 'Regulatory Copilot',
      heroSubtitle: 'Instant, citation-grounded guidance for Section 3(p) patents, BDA 2023 ABS compliance, and classical ASU licensing.',
      typeMessage: 'Type your regulatory or IP query here (e.g., "Is Ashwagandha extract patentable?")...',
      ask: 'Ask',
      analyzing: 'Analyzing query & detecting statutory jurisdiction...',
    },
    wizard: {
      module1: 'Module 1 · Deterministic Regulatory Classifier',
      title: 'Product Classification & Regulatory Pathway',
      subtitle: 'Map your formulation to the Drugs & Cosmetics Act 1940 (First Schedule), Rule 158B, FSSAI Ayurveda Aahara, and Patents Act Section 3(p) statutory exclusions.',
    }
  },
  hi: {
    nav: {
      overview: 'अवलोकन (Overview)',
      productClassification: 'उत्पाद वर्गीकरण (Product Classification)',
      ipMatrix: 'बौद्धिक संपदा अवसर (IP Matrix)',
      abs: 'एबीएस और जैव विविधता (ABS & Biodiversity)',
      askAyuraksha: 'आयु-रक्षा से पूछें (Ask AyuRaksha)',
      corpus: 'वैधानिक संग्रह (Statutory Corpus)',
    },
    topBanner: {
      ministry: 'आयुष मंत्रालय और एआईआईए (AIIA) · आईपी-शक्ति सहायक',
      language: 'भाषा:',
      jurisdiction: 'अधिकार क्षेत्र:',
      india: '🇮🇳 भारत (IN)',
      international: '🌎 अंतर्राष्ट्रीय (INT)',
      crossBorder: '🌐 सीमा पार (Cross-Border)',
    },
    brand: {
      title: 'आयु-रक्षा (AyuRaksha)',
      badge: 'निर्णय इंजन (Decision Engine)',
      subtitle: 'आयुर्वेदिक नवाचार के लिए एआई आईपी और विनियामक नेविगेटर',
    },
    app: {
      complianceDossier: 'अनुपालन डोजियर (Compliance Dossier)',
      heroTitleLine1: 'आयुर्वेदिक आईपी और',
      heroTitleLine2: 'विनियामक को-पायलट',
      heroSubtitle: 'धारा 3(पी) पेटेंट, बीडीए 2023 एबीएस अनुपालन, और शास्त्रीय एएसयू लाइसेंसिंग के लिए त्वरित, प्रमाण-आधारित मार्गदर्शन।',
      typeMessage: 'अपना विनियामक या आईपी प्रश्न यहां लिखें...',
      ask: 'पूछें (Ask)',
      analyzing: 'क्वेरी का विश्लेषण और वैधानिक अधिकार क्षेत्र का पता लगाया जा रहा है...',
    },
    wizard: {
      module1: 'मॉड्यूल 1 · नियतात्मक विनियामक वर्गीकरण',
      title: 'उत्पाद वर्गीकरण एवं विनियामक मार्ग',
      subtitle: 'अपने फार्मूले को औषधि और प्रसाधन सामग्री अधिनियम 1940 (पहली अनुसूची), नियम 158B, FSSAI आयुर्वेद आहार, और पेटेंट अधिनियम की धारा 3(p) के तहत वैधानिक बहिष्करण के साथ मैप करें।',
    }
  },
  sa: {
    nav: {
      overview: 'सिंहावलोकनम् (Overview)',
      productClassification: 'उत्पादवर्गीकरणम् (Product Classification)',
      ipMatrix: 'बौद्धिकसम्पदा-अवसरः (IP Matrix)',
      abs: 'एबीएस-जैवविविधता च (ABS & Biodiversity)',
      askAyuraksha: 'आयुरक्षां पृच्छतु (Ask AyuRaksha)',
      corpus: 'वैधानिकसङ्ग्रहः (Statutory Corpus)',
    },
    topBanner: {
      ministry: 'आयुष-मन्त्रालयः तथा एआईआईए (AIIA) · आईपी-शक्ति-सहायकः',
      language: 'भाषा:',
      jurisdiction: 'अधिकारक्षेत्रम्:',
      india: '🇮🇳 भारतम् (IN)',
      international: '🌎 अन्ताराष्ट्रियम् (INT)',
      crossBorder: '🌐 सीमापारम् (Cross-Border)',
    },
    brand: {
      title: 'आयुरक्षा (AyuRaksha)',
      badge: 'निर्णययन्त्रम् (Decision Engine)',
      subtitle: 'आयुर्वेदिकनवाचाराय एआई-आईपी तथा विनियामक-मार्गदर्शकः',
    },
    app: {
      complianceDossier: 'अनुपालन-सञ्चिका (Compliance Dossier)',
      heroTitleLine1: 'आयुर्वेदिक-आईपी तथा',
      heroTitleLine2: 'विनियामक-सहयात्री (Copilot)',
      heroSubtitle: 'धारा ३(p) पेटेण्ट्, बीडीए २०२३ एबीएस अनुपालनम्, तथा शास्त्रीय-एएसयू-अनुज्ञप्तिकरणाय त्वरितं, प्रमाण-आधारितं मार्गदर्शनम्।',
      typeMessage: 'अत्र स्वस्य विनियामकं वा आईपी-प्रश्नं टङ्कयतु...',
      ask: 'पृच्छतु (Ask)',
      analyzing: 'प्रश्नानां विश्लेषणं तथा वैधानिक-अधिकारक्षेत्रस्य अन्वेषणं क्रियते...',
    },
    wizard: {
      module1: 'अध्यायः १ · नियतात्मक-विनियामक-वर्गीकरणम्',
      title: 'उत्पादवर्गीकरणं तथा विनियामकमार्गः',
      subtitle: 'भवतः योगम् ओषधि-सौन्दर्य-प्रसाधन-अधिनियमः १९४० (प्रथम-अनुसूची), नियमः १५८B, FSSAI आयुर्वेद-आहारः, तथा पेटेण्ट्-अधिनियमस्य धारा ३(p) इत्येतैः सह योजयतु।',
    }
  }
};
