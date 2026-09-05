# Ministry of Ayush - Problem Statement 26045

**Problem Statement ID:** 26045  
**Problem Statement Title:** IP-SAKTI Sahayak: A multilingual, RAG-based (source-cited) AI assistant for Intellectual Property and regulatory guidance in Ayurveda, across national and international regimes.  
**Organization:** Ministry of Ayush  
**Department:** All India Institute of Ayurveda  
**Category:** Software  
**Theme:** MedTech / BioTech / HealthTech  

---

## Background
Ayurveda rests on a vast corpus of codified and community-held traditional knowledge (TK) and on therapeutics derived from plant, microbial and animal sources. Protecting and commercialising an Ayurvedic product means navigating several overlapping regimes at once: patents, geographical indications (GI), trademarks, copyright, designs, trade secrets and plant-variety rights; the Access-and-Benefit-Sharing (ABS) duties that flow from India's sovereignty over its biological resources; and the drug-regulatory framework that decides whether a formulation is a classical medicine, a proprietary medicine, a new drug, a phytopharmaceutical, a food or a cosmetic. 

Practitioners, researchers, AYUSH startups and MSMEs and cultivators routinely struggle with this. The result is twofold: legitimate Ayurvedic innovation is under-protected and under-commercialised, while India's traditional knowledge remains exposed to misappropriation abroad. 

Recent shifts — the 2024 patent and biodiversity rules, the WIPO Treaty on Genetic Resources and Associated Traditional Knowledge (2024) and a fast-moving advertising and regulatory landscape — make authoritative, plain-language guidance more necessary than ever, yet no such tool exists for the AYUSH community.

---

## Description
The assistant answers IPR questions specific to Ayurveda with accuracy, source citation and jurisdictional clarity, keeping the national and the international layers distinct through an explicit jurisdiction switch so that answers are never conflated.

Because intellectual property for an Ayurvedic product is inseparable from how the product is regulated, **the assistant first helps classify the formulation.** It asks the **minimum clarifying questions** to determine whether the product is:
1. A **classical/generic medicine** (formulation and method drawn from a First-Schedule authoritative text),
2. A **patent-or-proprietary medicine**,
3. A **new or non-classical drug** requiring proof of safety and effectiveness,
4. A **phytopharmaceutical**,
5. An **Ayurveda-Aahar / nutraceutical**, or
6. A **cosmetic**

— and then states what each category requires and its very different IP and ABS posture. For example, a classical formulation is largely traditional knowledge that faces the Section 3(p) patenting bar and is defended through the Traditional Knowledge Digital Library (TKDL), whereas a new drug gains genuine patent potential but must generate clinical evidence.

### Regulatory & Statutory Regimes Covered:
* **National Coverage:**
  * The Patents Act (and 2024 Rules, including Sec 3(p))
  * Geographical Indications (GI), Trade Marks, Designs, Copyright, Plant-Variety protection
  * Biological Diversity Act (BDA 2002, amended 2023, 2024 Rules) and ABS obligations
  * Drugs and Cosmetics Act, 1940 (and Rules, including Rule 158B)
  * Drugs and Magic Remedies (Objectionable Advertisements) Act, 1954
  * FSSAI Ayurveda-Aahar Regulations, 2022
* **International Coverage:**
  * TRIPS Agreement
  * Convention on Biological Diversity (CBD) & Nagoya Protocol
  * WIPO Treaty on Intellectual Property, Genetic Resources and Associated Traditional Knowledge (WIPO GRATK Treaty, 2024)
  * Patent Cooperation Treaty (PCT), Madrid System, Hague System, Budapest Treaty (micro-organism deposits)
  * Major export market herbal regulatory regimes (US FDA DSHEA, EU THMPD)

### Key Functional Requirements:
1. **Authoritative Sources & Registries:** Free official databases directly (TKDL, India Code, IP India, InPASS, NBA), with specific citations to statutes, rules, treaty articles, or records.
2. **Legal Disclaimer:** Explicit standing disclaimer that it provides authoritative information, not formal legal advice.
3. **Strict Fact-Grounding:** Minimal hallucinations, verifiable legal authority, safe abstention on out-of-scope or uncertain queries.

---

## Expected Solution Architecture
A deployable, multilingual assistant built on retrieval-augmented generation (RAG) grounded in a curated, version-tracked corpus of statutes, rules, treaties, pharmacopoeial standards, registry records, and case law:
1. **Explicit Jurisdiction Toggle:** India vs International, keeping the two answer sets visibly separate.
2. **Formulation-Classification Flow First:** Interactive routing across IP types coupled with minimal clarifying intake.
3. **ABS-Compliance Helper & TKDL / Prior-Art Pointer:** Sourcing checks (cultivated vs wild), foreign entity triggers, benefit-sharing duties.
4. **Mandatory Source Citations & Confidence Indicator:** Visible confidence metrics and clear escalation path to human IP facilitators.
5. **Multilingual Delivery:** Leveraging national language infrastructure (Bhashini).
6. **Guardrails & Compliance:** Safe abstention on medical advice/unsupported queries, privacy, DPDP alignment, audit logs.
7. **Relational Knowledge Graph & Multi-Source Orchestration:** Deeper multi-step legal reasoning across regimes.
