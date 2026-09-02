# AyuRaksha — App Flow, Screen Map & User Journeys

**Document:** 03_APP_FLOW.md  
**Product:** AyuRaksha (आयुसुरक्षा)  
**Version:** 2.0 (Consolidated)  
**Status:** Canonical Interaction Specification  

---

## 1. Information Architecture & Navigation

AyuRaksha features a clean, responsive layout designed around deep focus and rapid access:

```
AyuRaksha Application Shell
├── Collapsible Sidebar (Left)
│   ├── Ministry of Ayush & Brand Header
│   ├── "New Consultation" Trigger (Cmd/Ctrl + N)
│   └── Regulatory Tools Navigation
│       ├── 1. Copilot Chat (`/chat`)
│       ├── 2. Product Classifier (`/classification`)
│       ├── 3. IP Opportunity Matrix (`/ip_matrix`)
│       ├── 4. ABS Compliance Check (`/abs_wizard`)
│       ├── 5. Statutory Corpus & TKDL (`/corpus`)
│       └── 6. Knowledge Graph (`/knowledge_graph`) [NEW]
├── Persistent Top Bar
│   ├── Jurisdiction Pill Selector (India / International / Cross-Border)
│   ├── Language Toggle (English / हिन्दी / संस्कृतम्)
│   └── "Compliance Dossier" Modal Trigger
├── Center Dynamic Workspace (Active View)
└── Right Statutory Authority Drawer (Perplexity-Style Deep Citation Inspection)
```

---

## 2. Core User Journeys

### Journey 1: Natural Language Inquiry & Citation Deep-Dive
1. **User Input**: Innovator inputs: *"Can I patent a modified Ashwagandha extract for anxiety and stress?"*
2. **Intent & Jurisdiction Resolution**: System identifies jurisdiction (`IN`) and targets regimes (`DCA 1940`, `Patents Act § 3(p)`, `BDA 2002 § 6`).
3. **SSE Stage Streaming**: Real-time progress badges display pipeline status:
   - `TRI_RETRIEVAL`: Querying vector embeddings, GIN index, and statutory graph.
   - `RERANKING`: Applying domain-intent bonuses (+0.25 for DCA/Patents).
   - `GENERATION`: Streaming tokens via Gemini 2.5 Flash (~500ms).
   - `CITATION_PROVENANCE`: Validating claims against Gazette checksums.
4. **Interactive Answer Presentation**:
   - `StatutoryMarkdownRenderer` renders numbered section badges (`[1]`, `[2]`), tracking labels (`KEY CRITERIA ───────`), and highlighted implication callouts.
   - Interactive citation pills (`[1]`, `[2]`) appear inline with legal claims.
5. **Deep Citation Inspection**:
   - Clicking an inline pill smoothly slides open the right-hand **Statutory Authority** drawer.
   - Clicking **"View Authentic Gazette Record"** opens the dark-glass Gazette modal with direct links to `indiacode.nic.in` and cryptographic SHA-256 hash verification.

---

### Journey 2: Multi-Hop Knowledge Graph Exploration
1. **Open Visualizer**: User selects **Knowledge Graph** in the sidebar.
2. **Topology Canvas**: 28 color-coded nodes render in a balanced radial spring layout.
3. **Interactive Filtering**: User types *"Ashwagandha"* or clicks the **Medicinal Resource** filter chip.
4. **Inspect Node**: User clicks *Withania somnifera (Ashwagandha)*:
   - Direct connected neighbors (*Charaka Samhita*, *Bhaishajya Ratnavali*, *BDA § 6*) light up; unrelated nodes smoothly dim to 15% opacity.
   - Right inspector drawer slides open displaying API Vol. I references, traditional rasayana attributes, and legal substance.
   - User clicks `CODIFIED_IN → Charaka Samhita` to traverse the statutory path to First Schedule recognition under DCA Section 3(a).
5. **Handoff to Copilot**: User clicks **"Ask Copilot about this Node"** → transitions automatically to Chat Copilot with pre-filled relational prompt.

---

### Journey 3: Product Classification Decision Tree
1. **Start Wizard**: User selects **Product Classifier** from sidebar.
2. **Question 1 (Textual Alignment)**: Is the formulation described verbatim in one of the 56 books in the First Schedule?
   - *Yes* → **Classical ASU Drug** (Form 25D manufacturing license, barred from patents under § 3(p)).
   - *No* → Proceed to Question 2.
3. **Question 2 (Modified ASU)**: Does it introduce new excipients, aqueous extracts, or novel dosage forms?
   - *Yes* → **Patent or Proprietary ASU Medicine** (Rule 158B, Form 25D + Safety Dossier). Patentable if synergistic under § 3(e).
   - *No* → Proceed to Question 3.
4. **Question 3 (Purified Fractions)**: Is it an isolated, standardized chemical fraction?
   - *Yes* → **Phytopharmaceutical Drug** (CDSCO Rule 122E, Form CT-18 + Phase I–IV clinical trials).
   - *No* → Proceed to Question 4.
5. **Question 4 (Food & Dietary Supplements)**: Is it marketed as a food supplement or general nutritional support?
   - *Yes* → **FSSAI Ayurveda Aahara** (FoSCoS registration, strictly barred from disease claims under Regulation 5).
6. **Result Presentation**: Displays comprehensive statutory breakdown, governing forms, and an "Add to Compliance Dossier" action.

---

### Journey 4: ABS Compliance & Form Routing
1. **Start Wizard**: User selects **ABS Compliance Check**.
2. **Applicant Entity Determination**:
   - Indian Citizen / Domestic Entity → Governed by Section 7 (State Biodiversity Board prior intimation).
   - Non-Indian / Foreign Entity / NRI → Governed by Section 3 (National Biodiversity Authority prior approval via Form I).
3. **Ayush Practitioner Exemption**: Evaluates 2023 Amendment Section 7 exemption for registered Vaidyas/Hakims.
4. **Commercial Patent Filing**:
   - If user intends to file an Indian or foreign patent based on Indian biological resources → Mandatory **NBA Form III** approval under Section 6 before grant of patent.

---

### Journey 5: Active Compliance Dossier Export
1. **Trigger**: User clicks **Compliance Dossier** in the top action bar.
2. **Aggregation**: System aggregates:
   - Product classification determination.
   - ABS regulatory status and required NBA/SBB forms.
   - Patent risk score (assessing Section 3(p) TKDL exposure).
   - Complete list of cited primary statutes with SHA-256 hashes.
3. **Audit Verification**: Displays digital audit seal and timestamp.
4. **Actions**: One-click **Print to PDF** or **Download Dossier (Markdown)** for formal state licensing authority submission.
