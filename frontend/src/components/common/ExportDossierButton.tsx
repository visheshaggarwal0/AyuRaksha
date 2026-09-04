import React, { useRef, useState } from "react";
import { Download, FileText, Shield, Loader2 } from "lucide-react";
import { ProductClassificationResponse, ABSAssessmentResponse, Citation } from "../../types";

export interface DossierData {
  productClassification?: ProductClassificationResponse | null;
  absAssessment?: ABSAssessmentResponse | null;
  queryContext?: string;
  jurisdiction?: string;
}

interface ExportDossierButtonProps {
  dossier: DossierData;
  fileNamePrefix?: string;
}

/**
 * ExportDossierButton — compiles Product Journey + ABS + IP Matrix into
 * an official-looking "Ayuरक्षा Regulatory & IP Compliance Dossier" PDF.
 * Strategy: uses browser print-to-PDF via hidden iframe (no extra deps).
 * Optionally lazy-loads jspdf if available, falling back to print.
 */
export const ExportDossierButton: React.FC<ExportDossierButtonProps> = ({
  dossier,
  fileNamePrefix = "Ayuरक्षा_Dossier",
}) => {
  const [exporting, setExporting] = useState(false);
  const hiddenRef = useRef<HTMLDivElement>(null);

  const hasData =
    dossier.productClassification || dossier.absAssessment || dossier.queryContext;

  const generateFileName = () => {
    const base = dossier.productClassification?.product_name || "Compliance_Dossier";
    const sanitized = base.replace(/[^a-zA-Z0-9]/g, "_").slice(0, 30);
    const date = new Date().toISOString().slice(0, 10);
    return `${fileNamePrefix}_${sanitized}_${date}.pdf`;
  };

  const buildPrintHtml = () => {
    const cls = dossier.productClassification;
    const abs = dossier.absAssessment;
    const today = new Date().toLocaleDateString("en-IN", {
      day: "2-digit",
      month: "long",
      year: "numeric",
    });

    const citationChip = (c: Citation) =>
      `<span style="display:inline-flex;align-items:center;gap:6px;padding:6px 10px;border:1px solid #a7f3d0;background:#ecfdf5;color:#065f46;border-radius:10px;font-size:11px;font-weight:600;margin:4px 6px 0 0;">${c.source_title} · ${c.section}</span>`;

    const html = `<!doctype html><html><head><meta charset="utf-8"/>
<title>Ayuरक्षा Regulatory & IP Compliance Dossier</title>
<style>
@page { size: A4; margin: 18mm 14mm 18mm 14mm; }
*{font-family: Inter, system-ui, -apple-system, Segoe UI, Roboto, sans-serif; box-sizing:border-box;}
body{color:#17211B; line-height:1.5; margin:0; padding:0;}
.header {border-bottom:3px solid #166534; padding-bottom:14px; margin-bottom:18px; display:flex; justify-content:space-between; align-items:flex-start;}
.brand {display:flex; gap:12px; align-items:center;}
.badge{width:44px;height:44px;border-radius:12px;background:#166534;display:flex;align-items:center;justify-content:center;color:white;font-weight:800;}
.h1{font-size:20px; font-weight:800; margin:0; color:#14532D;}
.subtitle{font-size:11px; color:#475569; margin-top:4px;}
.meta{font-size:11px; color:#334155; text-align:right;}
.section{border:1px solid #DDE5DE; border-radius:16px; padding:16px; margin-bottom:14px; background:white;}
.section h3{font-size:12px; letter-spacing:0.08em; text-transform:uppercase; color:#166534; margin:0 0 10px 0; border-bottom:1px solid #e2e8f0; padding-bottom:8px;}
.grid3{display:grid; grid-template-columns:1fr 1fr 1fr; gap:10px; margin-bottom:12px;}
.card{border-radius:12px; padding:12px; border:1px solid #e2e8f0;}
.card.emerald{background:#ecfdf5; border-color:#a7f3d0;}
.card.amber{background:#fffbeb; border-color:#fde68a;}
.card.blue{background:#eff6ff; border-color:#bfdbfe;}
.card label{font-size:10px; font-weight:700; letter-spacing:0.06em; text-transform:uppercase; color:#475569;}
.card p{font-size:13px; font-weight:700; margin:6px 0 0 0;}
.rationale{background:#f8fafc; border:1px solid #e2e8f0; border-radius:12px; padding:12px; font-size:13px;}
.steps{margin:0; padding-left:18px;}
.steps li{font-size:12.5px; margin:6px 0;}
.footer{margin-top:18px; border-top:1px solid #e2e8f0; padding-top:12px; font-size:10px; color:#64748b; display:flex; justify-content:space-between;}
.watermark{position:fixed; inset:0; display:flex; align-items:center; justify-content:center; opacity:0.04; font-size:120px; font-weight:900; color:#166534; transform:rotate(-18deg); pointer-events:none;}
@media print { .no-print{display:none;} }
</style></head><body>
<div class="watermark">Ayuरक्षा</div>
<div class="header">
  <div class="brand">
    <div class="badge">AR</div>
    <div>
      <div class="h1">Ayuरक्षा — Regulatory & IP Compliance Dossier</div>
      <div class="subtitle">SIH 26045 · Ministry of Ayush & AIIA · Citation-grounded Decision Support · Jurisdiction: ${dossier.jurisdiction || "IN"}</div>
    </div>
  </div>
  <div class="meta">
    <div><strong>Date:</strong> ${today}</div>
    <div><strong>Dossier ID:</strong> AR-${Date.now().toString().slice(-8)}</div>
    <div><strong>Confidential</strong> · For facilitator review</div>
  </div>
</div>

${
  cls
    ? `<div class="section">
  <h3>1 — Product Classification & IP Opportunity</h3>
  <div style="margin-bottom:8px; font-size:11px; color:#475569;">Product: <strong style="color:#17211B;">${cls.product_name}</strong> · Confidence: ${(cls.confidence * 100).toFixed(0)}%</div>
  <div class="grid3">
    <div class="card emerald"><label>Governing Statute</label><p>${cls.governing_act}</p><div style="font-size:11px;color:#065f46;margin-top:4px;">${cls.category}</div></div>
    <div class="card amber"><label>Patentability Status</label><p>${cls.patentability}</p></div>
    <div class="card blue"><label>Licensing Authority</label><p>${cls.regulatory_authority}</p></div>
  </div>
  <div class="rationale"><strong style="font-size:11px; letter-spacing:0.06em; text-transform:uppercase; color:#475569;">Statutory IP Analysis</strong><div style="margin-top:6px;">${cls.patent_rationale}</div></div>
  <div style="margin-top:12px;">
    <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#166534;">Supporting Authority</div>
    <div style="margin-top:6px;">${cls.citations.map(citationChip).join("") || '<span style="font-size:11px;color:#64748b;">No citations returned.</span>'}</div>
  </div>
  <div style="margin-top:12px;">
    <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#166534;">Mandatory Compliance Roadmap</div>
    <ol class="steps">${cls.next_actions.map((a) => `<li>${a}</li>`).join("")}</ol>
  </div>
</div>`
    : `<div class="section"><h3>1 — Product Classification</h3><p style="font-size:12px;color:#64748b;">No classification data provided for this dossier export. Run Product Journey wizard to include.</p></div>`
}

${
  abs
    ? `<div class="section">
  <h3>2 — Access & Benefit Sharing (ABS) Assessment</h3>
  <div class="grid3">
    <div class="card"><label>Biological Resource</label><p>${abs.resource}</p><div style="font-size:11px;color:#475569;">Trigger: ${abs.trigger_detected ? "Yes" : "No"}</div></div>
    <div class="card emerald"><label>Applicable Authority</label><p>${abs.applicable_authority}</p><div style="font-size:11px;color:#065f46;">${abs.approval_type}</div></div>
    <div class="card amber"><label>Risk Level</label><p>${abs.risk_level}</p><div style="font-size:11px;color:#92400e;">${abs.governing_statute}</div></div>
  </div>
  <div style="margin-top:10px;">
    <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#166534;">Statutory Citations</div>
    <div style="margin-top:6px;">${abs.statutory_citations.map(citationChip).join("") || '<span style="font-size:11px;color:#64748b;">No ABS citations.</span>'}</div>
  </div>
  <div style="margin-top:12px;">
    <div style="font-size:11px; font-weight:700; text-transform:uppercase; letter-spacing:0.06em; color:#166534;">Mandatory Filing Actions</div>
    <ol class="steps">${abs.mandatory_next_steps.map((s) => `<li>${s}</li>`).join("")}</ol>
  </div>
</div>`
    : `<div class="section"><h3>2 — ABS Assessment</h3><p style="font-size:12px;color:#64748b;">No ABS assessment included. Use ABS & Biodiversity Check wizard to add.</p></div>`
}

${
  dossier.queryContext
    ? `<div class="section"><h3>3 — Research Query Context</h3><p style="font-size:12.5px; background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px; padding:10px;">${dossier.queryContext}</p></div>`
    : ""
}

<div class="section" style="background:#f7faf7;">
  <h3>Disclaimer & Traceability</h3>
  <p style="font-size:11px; color:#475569; margin:0;">
    This dossier is a <strong>decision-support summary</strong> generated by deterministic statutory engines (Drugs & Cosmetics Act 1st Schedule, Patents Act Sec 3(p)/3(e)/10(4), Biological Diversity Act Sec 3/6/7 incl. 2023 amendments) plus verified citation entailment.
    It does <strong>not</strong> constitute legal advice. Final filings must be reviewed by a registered AYUSH IP facilitator / ABS attorney with official source versions (India Code, IP India, NBA). Authority hierarchy: Level 5 (Acts/Rules) preferred over Level 4 guidance.
    Jurisdiction firewall <strong>IN vs INT</strong> is enforced at retrieval.
  </p>
</div>

<div class="footer">
  <span>Ayuरक्षा · SIH 26045 · Ministry of Ayush & AIIA</span>
  <span>Generated ${today} · Neon + pgvector · Hash-verified sources recommended</span>
</div>
</body></html>`;

    return html;
  };

  const handleExport = async () => {
    if (!hasData) return;
    setExporting(true);
    try {
      // Try dynamic jspdf -> print HTML flow; fallback to iframe print
      const html = buildPrintHtml();
      // Attempt to use jspdf if installed without breaking build
      let usedJsPdf = false;
      try {
        // @ts-ignore - optional dep
        const mod: any = await import("jspdf").catch(() => null);
        if (mod?.jsPDF) {
          const { jsPDF: _JsPDF } = mod;
          void _JsPDF;
          // For now use HTML string via html2text fallback: render as text pages
          // Better UX is print flow, so we skip pure jsPDF html rendering which needs html2canvas
          throw new Error("prefer print flow");
        }
      } catch {
        // intentional fallthrough to print
      }

      if (!usedJsPdf) {
        const iframe = document.createElement("iframe");
        iframe.style.position = "fixed";
        iframe.style.right = "0";
        iframe.style.bottom = "0";
        iframe.style.width = "0";
        iframe.style.height = "0";
        iframe.style.border = "0";
        document.body.appendChild(iframe);
        const doc = iframe.contentDocument || iframe.contentWindow?.document;
        if (!doc) throw new Error("print iframe unavailable");
        doc.open();
        doc.write(html);
        doc.close();
        // Wait for fonts
        await new Promise((r) => setTimeout(r, 400));
        iframe.contentWindow?.focus();
        iframe.contentWindow?.print();
        setTimeout(() => {
          try {
            document.body.removeChild(iframe);
          } catch {}
        }, 1000);
      }

      // Also trigger file hint for users: create a .html download as backup trace
      // (optional, not required for PDF - print dialog handles save-as-PDF)
    } catch (e) {
      console.error("Dossier export failed", e);
      // Fallback: open new window
      const html = buildPrintHtml();
      const w = window.open("", "_blank");
      if (w) {
        w.document.open();
        w.document.write(html);
        w.document.close();
        w.focus();
        setTimeout(() => w.print(), 500);
      }
    } finally {
      setExporting(false);
    }
  };

  return (
    <>
      <button
        onClick={handleExport}
        disabled={!hasData || exporting}
        className="inline-flex items-center gap-2 px-4 py-2.5 bg-ayush-primary hover:bg-ayush-primaryDark disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold rounded-xl shadow-md transition-all text-sm"
        title={!hasData ? "Run classification/ABS first to export dossier" : generateFileName()}
      >
        {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
        <span>{exporting ? "Preparing Dossier..." : "Export Dossier PDF"}</span>
        <FileText className="w-3.5 h-3.5 opacity-80" />
      </button>

      {/* Hidden render target for style isolation (not visible) */}
      <div ref={hiddenRef} className="hidden" aria-hidden />

      {!hasData && (
        <p className="text-[11px] text-ayush-slate mt-2 flex items-center gap-1.5">
          <Shield className="w-3 h-3" /> Run wizards to populate dossier before export.
        </p>
      )}
    </>
  );
};

export default ExportDossierButton;
