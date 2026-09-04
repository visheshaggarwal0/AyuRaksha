export type Jurisdiction = 'IN' | 'INT' | 'CROSS_BORDER';

export interface Citation {
  source_id: string;
  source_title: string;
  section: string;
  subsection?: string;
  jurisdiction: Jurisdiction;
  official_url?: string;
  support_score: number;
  verbatim_quote: string;
}

export interface ClaimVerification {
  claim: string;
  is_supported: boolean;
  confidence_score: number;
  supporting_citations: Citation[];
}

export interface StructuredAnswer {
  direct_answer: string;
  jurisdiction: Jurisdiction;
  assessment_table: Record<string, any>;
  verified_claims: ClaimVerification[];
  citations: Citation[];
  confidence_level: 'HIGH' | 'MODERATE' | 'LOW';
  caveats: string[];
  safe_abstention: boolean;
  abstention_reason?: string;
  recommended_next_action: string;
  cross_border_posture?: {
    india_posture: string;
    international_posture: string;
  };
  language?: string;
}

export interface ProductClassificationRequest {
  name: string;
  in_classical_text: boolean;
  is_formulation_modified: boolean;
  has_novel_excipients: boolean;
  is_purified_standardized_fraction?: boolean;
  intended_use: string;
  disease_treatment_claims: boolean;
  has_biological_resources: boolean;
  target_market: string;
}

export interface ProductClassificationResponse {
  product_name: string;
  category: string;
  governing_act: string;
  patentability: string;
  patent_rationale: string;
  abs_required: boolean;
  regulatory_authority: string;
  citations: Citation[];
  confidence: number;
  next_actions: string[];
}

export interface ABSAssessmentRequest {
  biological_resource: string;
  origin_country: string;
  sourced_from_state?: string;
  is_commercial_utilization: boolean;
  is_traditional_knowledge_associated: boolean;
  is_indian_entity: boolean;
  is_export_intended: boolean;
}

export interface ABSAssessmentResponse {
  resource: string;
  trigger_detected: boolean;
  governing_statute: string;
  applicable_authority: string;
  approval_type: string;
  benefit_sharing_applicable: boolean;
  risk_level: string;
  statutory_citations: Citation[];
  mandatory_next_steps: string[];
}

export interface InnovationProfile {
  productName: string;
  baseline: string;
  differenceType: string;
  userStatedDifference: string;
  technicalFeature: string;
  technicalEffect: string;
  evidenceTypes: string[];
  evidenceDetails?: string;
  isTraditionalKnowledge: 'YES' | 'NO' | 'PARTIALLY' | 'UNSURE';
  classicalSourceText?: string;
  commercialIntent: string;
  targetJurisdiction: Jurisdiction;
  completedAt?: string;
}

export interface ActiveCaseState {
  caseId: string;
  createdAt: string;
  updatedAt: string;
  productRequest: ProductClassificationRequest | null;
  classificationResult: ProductClassificationResponse | null;
  absRequest?: ABSAssessmentRequest | null;
  absResult?: ABSAssessmentResponse | null;
  innovationProfile?: InnovationProfile | null;
  recentCitations?: Citation[];
  status: 'NO_CASE' | 'ACTIVE' | 'EVALUATED';
}


