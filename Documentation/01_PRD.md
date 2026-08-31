# AyuRaksha — Product Requirements Document (PRD)

**Version:** 1.0  
**Date:** 31 August 2026  
**Status:** Product baseline for SIH development  
**Product:** AyuRaksha  
**Problem Statement:** SIH 26045 — IP-SAKTI Sahayak  
**Sponsor:** Ministry of Ayush / All India Institute of Ayurveda

## 1. Product Vision

AyuRaksha is a multilingual, citation-grounded AI assistant that helps
Ayurveda practitioners, researchers, startups, MSMEs, cultivators and
facilitators understand intellectual-property, traditional-knowledge,
biodiversity/ABS and product-regulatory pathways across India and
selected international jurisdictions.

AyuRaksha is a **decision-support and research system**, not a
legal-advice or regulatory-approval system.

### Product promise

> **Ask → Classify → Research → Verify → Act**

AyuRaksha should turn a complex question such as “Can I patent and
export my new Ayurvedic formulation?” into a structured journey covering
product classification, relevant IP routes, traditional-knowledge
concerns, ABS considerations, jurisdiction-specific rules, authoritative
sources, uncertainty and recommended next actions.

## 2. Problem

Ayurvedic innovation sits at the intersection of several regimes:

- patents and prior art;
- trademarks, GIs, copyright and designs;
- plant-variety protection;
- biological-resource access and benefit sharing;
- traditional knowledge;
- drug, food and cosmetic classification;
- advertising, labelling and market-access requirements;
- international IP and export regimes.

Existing search engines and generic AI assistants do not reliably
provide:

1.  jurisdiction-separated answers;
2.  version-aware legal retrieval;
3.  exact authoritative citations;
4.  product-classification workflows;
5.  ABS/TK workflows;
6.  safe abstention when evidence is insufficient;
7.  a path from information to action.

## 3. Goals

### Primary goals

1.  Provide source-grounded answers to Ayurveda-specific IP and
    regulatory questions.
2.  Keep India and international legal regimes visibly and technically
    separate.
3.  Classify an Ayurvedic product before recommending downstream
    pathways.
4.  Surface relevant IP protection options.
5.  Provide an ABS/TK preliminary assessment workflow.
6.  Provide exact, traceable citations to authoritative evidence.
7.  Detect uncertainty, unsupported claims and conflicting sources.
8.  Support multilingual interaction, initially prioritising English and
    Hindi.
9.  Provide a human-escalation package for ambiguous/high-risk cases.
10. Maintain a versioned, auditable corpus.

### Secondary goals

- selected international/export-market guidance;
- knowledge graph for multi-hop questions;
- voice interaction;
- registry/database connectors;
- facilitator case management.

## 4. Non-goals

AyuRaksha will not:

- provide legal advice or represent a lawyer;
- guarantee patentability, registration, approval or market access;
- file legal applications automatically in the MVP;
- replace a patent attorney, IP facilitator, regulator or qualified
  consultant;
- claim access to restricted databases without authorised access;
- infer restricted TKDL results when the system has no lawful search
  capability;
- use third-party sources as substitutes for primary authority where
  primary authority is available.

## 5. Target Users

### U1 — AYUSH startup / MSME founder

Needs to understand whether a new product can be protected, what
compliance steps may apply, and where to start.

### U2 — Ayurveda practitioner

Needs plain-language guidance on classification, claims, advertising and
IP.

### U3 — Researcher / academic

Needs prior-art, patent, TK and regulatory research with citations.

### U4 — Cultivator / producer

Needs guidance around biological resources, provenance, varieties, GIs
and benefit-sharing.

### U5 — IP facilitator / professional

Needs faster research, evidence packs and structured case summaries.

### U6 — Institutional / government stakeholder

Needs an auditable information system and aggregate insight into
recurring user problems.

## 6. Core Features

### F1 — Ask AyuRaksha

Natural-language question answering with:

- intent detection;
- jurisdiction detection;
- source retrieval;
- answer synthesis;
- citations;
- confidence;
- uncertainty;
- escalation.

### F2 — Jurisdiction Switch

Two explicit modes:

- India
- International

The retrieval layer must enforce jurisdiction filters.

### F3 — Product Classification Journey

Determine the likely regulatory category using a minimum-question
decision tree.

Initial categories:

- classical/generic medicine;
- proprietary/patent medicine;
- new/non-classical drug;
- phytopharmaceutical;
- Ayurveda-Aahara/nutraceutical pathway;
- cosmetic;
- other/uncertain.

The result must be labelled as a **preliminary classification**, with
the evidence and missing facts shown.

### F4 — IP Navigator

Generate an IP opportunity matrix covering:

- patent;
- trademark;
- GI;
- copyright;
- design;
- trade secret;
- plant-variety protection;
- other relevant routes.

Each route has:

- applicability;
- conditions;
- evidence;
- risk/uncertainty;
- next action.

### F5 — ABS Navigator

A guided questionnaire covering:

- biological resource;
- source/provenance;
- Indian origin;
- commercial/research purpose;
- traditional knowledge;
- foreign involvement;
- intended use/export;
- relevant authority pathway.

Output is a preliminary assessment, not a legal determination.

### F6 — TK / Prior-Art Pathway

Identify when traditional knowledge may be relevant and guide the user
to legitimate prior-art/TK resources. The system must clearly
distinguish public evidence from restricted databases.

### F7 — Export Navigator

For a selected destination:

- retain India-side analysis;
- add destination-market research;
- identify missing facts;
- separate IP from product-regulatory requirements.

### F8 — Evidence & Citation Layer

Every material legal/regulatory proposition should be traceable to:

- document;
- section/article/regulation;
- jurisdiction;
- version/effective date;
- source URL/record;
- retrieval timestamp.

### F9 — Confidence & Safe Abstention

The system should abstain when:

- evidence is insufficient;
- sources conflict materially;
- jurisdiction is unclear;
- current law cannot be established;
- the question requires professional determination.

### F10 — Human Escalation

Generate a case brief containing:

- user question;
- product facts;
- jurisdiction;
- classification;
- findings;
- sources;
- unresolved issues;
- confidence;
- missing information.

### F11 — Multilingual Interface

Phase 1:

- English;
- Hindi.

Architecture should support additional Indian languages and Bhashini
integration without changing the legal evidence layer.

## 7. User Stories

### Startup founder

- As a startup founder, I want to classify my Ayurvedic product so that
  I know which regulatory regime I should investigate.
- As a founder, I want to see which IP routes may apply so that I can
  prioritise protection.
- As a founder, I want citations so that I can verify important claims
  myself.
- As a founder, I want an export checklist so that I know which
  questions remain unresolved.

### Researcher

- As a researcher, I want to search authoritative sources using natural
  language.
- As a researcher, I want section-level citations.
- As a researcher, I want to compare India and international regimes
  without conflation.

### Facilitator

- As a facilitator, I want an evidence-backed case summary.
- As a facilitator, I want to see the corpus version used by the answer.
- As a facilitator, I want uncertain claims highlighted.

## 8. Success Metrics

### Product

| Metric                            | MVP target |
|-----------------------------------|-----------:|
| Task completion rate              |       ≥80% |
| Product-classification completion |       ≥85% |
| User-rated helpfulness            |     ≥4.2/5 |
| Citation click-through            |       ≥30% |

### AI quality

| Metric                       | Target |
|------------------------------|-------:|
| Retrieval Recall@5           |   ≥90% |
| Citation precision           |   ≥95% |
| Citation completeness        |   ≥90% |
| Supported-claim rate         |   ≥95% |
| Jurisdiction leakage         |   \<1% |
| Unsafe confident-answer rate |   \<2% |
| Correct abstention rate      |   ≥90% |

Targets are engineering goals; final values must be measured on an
expert-reviewed benchmark.

### Multilingual

- Hindi semantic equivalence ≥90% on the benchmark.
- Legal entity/section preservation ≥95%.
- Citation preservation ≥99%.

## 9. Risk Principles

AyuRaksha must prioritise:

1.  correctness over fluency;
2.  primary authority over secondary commentary;
3.  explicit uncertainty over fabricated certainty;
4.  traceability over convenience;
5.  jurisdictional separation over generic answers.

## 10. Legal/Regulatory Corpus Baseline

The corpus should prioritise official sources. For example, IP India
publishes the Patents Rules and amendment material, including the 2024
amendments; FSSAI publishes the Ayurveda-Aahara Regulations and
subsequent orders; WIPO provides the 2024 GRATK Treaty materials; and
MeitY publishes the DPDP Rules 2025 and enforcement information. These
are examples of the source hierarchy and should be revalidated during
corpus ingestion rather than treated as a frozen list.

## 11. Release Strategy

### MVP

- India-first;
- English + Hindi;
- core IP/regulatory RAG;
- citations;
- classification;
- IP matrix;
- ABS preliminary workflow;
- confidence/abstention;
- human escalation.

### V2

- international regimes;
- knowledge graph;
- multi-hop retrieval;
- selected export markets;
- registry connectors.

### V3

- agentic orchestration;
- voice;
- broader Indian-language support;
- facilitator workspace;
- authorised paid-source connectors.
