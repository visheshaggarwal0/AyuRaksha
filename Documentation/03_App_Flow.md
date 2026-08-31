# AyuRaksha — App Flow & Information Architecture

## 1. Primary Navigation

### Mobile bottom navigation

1.  Home
2.  Research
3.  Journeys
4.  Sources
5.  Profile

### Desktop

Sidebar:

- Home
- Ask AyuRaksha
- Product Journey
- IP Navigator
- ABS & TK
- Export Navigator
- Saved Cases
- Sources
- Settings

## 2. Screen Inventory

### S01 — Splash

Purpose: - brand recognition; - session restoration.

Elements: - AyuRaksha logo; - tagline; - loading state.

### S02 — Onboarding

Collect: - preferred language; - user type; - optional interests.

Do not request unnecessary personal information.

### S03 — Home

Cards:

- Ask AyuRaksha
- Classify Product
- IP Navigator
- ABS Check
- Export Navigator
- Prior Art / TK

Also show: - recent journeys; - saved cases; - source update indicator.

### S04 — Ask AyuRaksha

Components:

- jurisdiction selector;
- language selector;
- query composer;
- suggested questions;
- chat history.

### S05 — Answer

Structure:

1.  short answer;
2.  assessment;
3.  important caveats;
4.  India/international section;
5.  sources;
6.  confidence;
7.  recommended next action;
8.  escalate button.

### S06 — Source Detail

Show:

- source title;
- authority;
- jurisdiction;
- version;
- effective date;
- exact section;
- source text;
- official link;
- retrieval date.

### S07 — Product Journey Intro

Explain:

> “We’ll ask a few questions to identify the likely regulatory pathway.”

### S08 — Product Questionnaire

One question per screen on mobile.

Show: - progress; - back; - save and exit; - uncertainty option.

### S09 — Classification Result

Show:

- likely category;
- confidence;
- reasons;
- evidence;
- missing facts;
- disclaimer.

### S10 — IP Matrix

Grid/cards for:

- Patent;
- Trademark;
- GI;
- Copyright;
- Design;
- Trade Secret;
- Plant Variety.

Each opens a detailed pathway.

### S11 — Patentability Journey

Stages:

1.  Novelty
2.  Inventive step
3.  Industrial applicability
4.  statutory exclusions
5.  TK/prior-art check
6.  biological-resource/ABS consideration
7.  professional review

### S12 — ABS Wizard

Questions: - resource; - source; - purpose; - traditional knowledge; -
commercialisation; - foreign involvement; - export.

### S13 — ABS Result

Show: - preliminary assessment; - reasons; - relevant provisions; - next
actions; - escalation.

### S14 — Export Navigator

Inputs: - product; - India status; - destination; - business objective.

Output: - India-side considerations; - destination-side
considerations; - unresolved questions; - sources.

### S15 — Prior Art / TK

Show: - detected traditional-knowledge relevance; - available public
sources; - search pathway; - limitations.

### S16 — Saved Case

A structured record of: - product; - questions; - assessments; -
sources; - status.

### S17 — Human Escalation

Generate case summary.

Fields: - case title; - user facts; - questions; - evidence; -
uncertainties; - requested help.

### S18 — Settings

- language;
- theme;
- privacy;
- data retention;
- account;
- disclaimer.

## 3. Core User Journey — Patentability

``` text
Home
 ↓
Ask / IP Navigator
 ↓
Select India
 ↓
Enter question
 ↓
Intent classification
 ↓
Missing facts?
 ├─ Yes → Clarifying questions
 └─ No
 ↓
Hybrid retrieval
 ↓
Answer
 ↓
Citation verification
 ↓
Patentability assessment
 ↓
IP matrix
 ↓
Save / Escalate
```

## 4. Core User Journey — Product Classification

``` text
Home
 ↓
Product Journey
 ↓
Basic product facts
 ↓
Classical text relationship
 ↓
Intended use
 ↓
Composition/process
 ↓
Product category
 ↓
Evidence
 ↓
IP matrix
 ↓
Regulatory checklist
```

## 5. Core User Journey — ABS

``` text
Home
 ↓
ABS Check
 ↓
Biological resource?
 ↓
Origin/source
 ↓
Traditional knowledge?
 ↓
Purpose
 ↓
Commercialisation
 ↓
Foreign involvement
 ↓
Assessment
 ↓
Sources
 ↓
Next steps
 ↓
Escalation
```

## 6. Core User Journey — Export

``` text
Home
 ↓
Export Navigator
 ↓
Select product
 ↓
Select destination
 ↓
India-side assessment
 ↓
Destination-market retrieval
 ↓
Compare requirements
 ↓
Checklist
 ↓
Sources
 ↓
Save
```

## 7. Error States

### E01 — No results

Message:

> “I couldn’t find sufficient authoritative evidence for this question.”

Actions: - refine question; - change jurisdiction; - escalate.

### E02 — Conflicting sources

Show:

> “Authoritative sources appear to conflict or apply to different
> dates.”

Actions: - compare sources; - inspect effective dates; - escalate.

### E03 — Missing facts

Show exact missing information.

Avoid asking 10 questions at once.

### E04 — Unsupported jurisdiction

> “AyuRaksha currently does not have sufficient authoritative coverage
> for this jurisdiction.”

### E05 — Source unavailable

> “The official source is temporarily unavailable. This answer is
> withheld rather than inferred.”

### E06 — LLM/provider failure

Retry once, then graceful fallback.

### E07 — Unsafe request

If the user requests professional legal representation or definitive
approval:

> “AyuRaksha can provide information and evidence, but cannot make a
> binding legal or regulatory determination.”

## 8. Accessibility

- WCAG-inspired contrast;
- large touch targets;
- keyboard navigation on web;
- screen-reader labels;
- no information conveyed only by colour;
- Hindi typography tested separately.
