# AyuRaksha — UI/UX Design System & Specification

**Document:** 04_UIUX_SPEC.md  
**Product:** AyuRaksha (आयुसुरक्षा)  
**Version:** 2.0 (Consolidated)  
**Status:** Canonical Visual & Interaction Design Specification  

---

## 1. Visual Design Ethos

AyuRaksha establishes a visual language tailored for legal scholars, innovators, and regulatory authorities. It explicitly rejects generic AI cliches (such as neon glowing gradients, purple sci-fi themes, and low-contrast borders) in favor of:

- **Authoritative Editorial Precision**: Clean, distraction-free canvases (`#F9F9F9`, `#FAFAFA`) paired with deep forest green and high-contrast slate typography.
- **Government-Grade Trust**: Authentic emblems, Gazette checksum badges, and formal statutory division lines.
- **Physical Motion**: Spring physics on collapsible drawers, interactive graph nodes, and micro-hover states powered by Framer Motion (`stiffness: 300, damping: 30`).
- **Typographic Scannability**: Multi-tiered visual hierarchy using Outfit (headings) and Inter (body) font pairings, numbered badge headers, and uppercase tracking labels.

---

## 2. Color Tokens & Semantic Meaning

### Core Palette
- **Forest Green (`#166534`, `#14532D`)**: Primary brand identity, authentic verification seals, and confirmed compliance badges.
- **Sage Emerald (`#059669`, `#10B981`)**: Active indicators, high-grounding citation pills, and botanical graph nodes.
- **Ayush Saffron (`#D97706`, `#B45309`)**: Classical texts, caution alerts, preliminary classification notices, and dossier highlights.
- **Deep Slate / Navy (`#0F172A`, `#1E293B`)**: Modal backgrounds, primary titles, and high-contrast dark-glass headers.
- **Canvas Neutral (`#F9F9F9`, `#FFFFFF`)**: Workspace background and card surfaces.
- **Border Hairline (`#E2E8F0`, `#CBD5E1`)**: Subtle structural division rules.

### Knowledge Graph Node Color System
| Category Key | Label | Color | Visual Meaning |
| :--- | :--- | :--- | :--- |
| `botanical` | Medicinal Resource | `#059669` (Emerald) | Botanicals & Biological Resources |
| `classical_text` | First Schedule Book | `#d97706` (Amber) | Classical Authoritative Ayurvedic Treatises |
| `statute` | Primary Statute | `#4338ca` (Indigo) | Parliament Acts (Patents Act, BDA, DCA) |
| `section` | Statutory Section | `#6366f1` (Periwinkle) | Specific Enacted Sub-Sections |
| `form` | Filing Form | `#0284c7` (Sky Blue) | Official CGPDTM & NBA Procedural Forms |
| `treaty` | International Treaty | `#9333ea` (Purple) | WIPO Conventions & Global Treaties |

---

## 3. Core Component Designs

### 3.1 `StatutoryMarkdownRenderer`
Transforms raw LLM Markdown into structured legal typography:
- **Numbered Section Headers (`### 1. ...`)**: Styled with solid emerald numbered badges (`[1]`, `[2]`), weighted typography, and subtle dividing rules.
- **Subheaders (`* **Key Criteria:**`)**: Converted from plain bullets into clean uppercase tracking labels with hairline dividers (`KEY CRITERIA ───────`).
- **Regulatory Callout Boxes (`* **Implication:** ...`)**: Rendered as highlighted emerald cards with a `CheckCircle2` icon.
- **Structured Definition Tiers**: Rendered with directional arrow indicators (`▸`).
- **Interactive Citation Pills (`[1]`, `[2]`)**: Clickable buttons that focus and highlight that statutory citation in the right-hand panel.

### 3.2 `CitationModal`
- High-contrast, dark-glass gradient header (`from-slate-950 via-slate-900 to-emerald-950`).
- Crisp white title typography with pulsating green status indicator.
- Section hash badge and direct external link to official India Code Gazette (`indiacode.nic.in`).

### 3.3 `KnowledgeGraphExplorer`
- **Zero-Dependency SVG Canvas**: Renders nodes as SVG `<circle>` elements with dual concentric glowing rings on hover/selection.
- **Directed Relation Edges**: SVG `<line>` elements with custom `<marker>` arrowheads (`#arrowhead-highlight` vs `#arrowhead-default`).
- **Edge Labeling**: Centered pill badges displaying relational semantics (`CODIFIED_IN`, `TRIGGERS_BAR`, `OPPOSED_VIA`, `MANDATORY_FILING`).
- **Sliding Legal Drawer**: Smooth spring-animated panel displaying full statutory text, legal rationale, and connected node hops.

### 3.4 `ComplianceDossierModal`
- Formal audit document view with Ministry of Ayush branding, digital audit seal, and SHA-256 integrity signature.
- One-click print-optimized CSS layout for direct PDF generation and Markdown export.
