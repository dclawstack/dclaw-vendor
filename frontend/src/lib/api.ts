const API_BASE = process.env.NEXT_PUBLIC_API_URL || "";

class ApiError extends Error {
  status: number;
  constructor(message: string, status: number) {
    super(message);
    this.status = status;
  }
}

async function fetchJson<T>(path: string, options?: RequestInit): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...options?.headers,
    },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(`API error ${response.status}: ${error}`, response.status);
  }
  return response.json();
}

async function fetchVoid(path: string, options?: RequestInit): Promise<void> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json", ...options?.headers },
    ...options,
  });
  if (!response.ok) {
    const error = await response.text();
    throw new ApiError(`API error ${response.status}: ${error}`, response.status);
  }
}

function qs(params: Record<string, string | number | undefined | null>): string {
  const sp = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v !== undefined && v !== null && v !== "") sp.set(k, String(v));
  }
  const s = sp.toString();
  return s ? `?${s}` : "";
}

export async function getHealth() {
  return fetchJson<{ status: string }>("/health/");
}

// ---------------------------------------------------------------------------
// Domain types (mirror the backend Pydantic schemas)
// ---------------------------------------------------------------------------

export type VendorStatus = "active" | "inactive" | "blacklisted";
export type VendorTier = "strategic" | "preferred" | "approved" | "transactional";
export type POStatus = "draft" | "sent" | "partial" | "received" | "cancelled";

export interface VendorEnrichment {
  company_size?: string | null;
  founded_year?: number | null;
  headquarters?: string | null;
  industry?: string | null;
  description?: string | null;
  source: "web" | "inferred";
  fetched_url: string | null;
  enriched_at: string;
}

export interface Vendor {
  id: string;
  name: string;
  contact_name: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  payment_terms: string | null;
  status: VendorStatus;
  category: string | null;
  industry: string | null;
  tier: VendorTier | null;
  website: string | null;
  enrichment: VendorEnrichment | null;
  created_at: string;
  updated_at: string;
}

export interface VendorCreate {
  name: string;
  contact_name?: string | null;
  email?: string | null;
  phone?: string | null;
  address?: string | null;
  payment_terms?: string | null;
  status?: VendorStatus;
  category?: string | null;
  industry?: string | null;
  tier?: VendorTier | null;
  website?: string | null;
}

export type VendorUpdate = Partial<VendorCreate>;

export interface POLineItem {
  id: string;
  po_id: string;
  product_name: string;
  description: string | null;
  quantity: number;
  unit_price: number;
  received_qty: number;
  created_at: string;
  updated_at: string;
}

export interface POLineItemNestedCreate {
  product_name: string;
  description?: string | null;
  quantity?: number;
  unit_price?: number;
  received_qty?: number;
}

export interface POLineItemCreate extends POLineItemNestedCreate {
  po_id: string;
}

export type POLineItemUpdate = Partial<{
  product_name: string;
  description: string | null;
  quantity: number;
  unit_price: number;
  received_qty: number;
}>;

export interface PurchaseOrder {
  id: string;
  vendor_id: string | null;
  status: POStatus;
  total: number;
  expected_delivery: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  line_items: POLineItem[];
}

export interface PurchaseOrderCreate {
  vendor_id?: string | null;
  status?: POStatus;
  expected_delivery?: string | null;
  notes?: string | null;
  line_items?: POLineItemNestedCreate[];
}

export type PurchaseOrderUpdate = Partial<{
  vendor_id: string | null;
  status: POStatus;
  expected_delivery: string | null;
  notes: string | null;
}>;

export interface Paginated<T> {
  items: T[];
  total: number;
}

// ---------------------------------------------------------------------------
// Vendors
// ---------------------------------------------------------------------------

export function listVendors(
  params: {
    search?: string;
    status?: VendorStatus | "";
    category?: string;
    tier?: VendorTier | "";
    limit?: number;
    offset?: number;
  } = {},
) {
  return fetchJson<Paginated<Vendor>>(`/api/v1/vendors${qs(params)}`);
}

export interface FacetCount {
  value: string;
  count: number;
}

export interface VendorFacets {
  status: FacetCount[];
  category: FacetCount[];
  tier: FacetCount[];
  industry: FacetCount[];
  total: number;
}

export function getVendorFacets() {
  return fetchJson<VendorFacets>("/api/v1/vendors/facets");
}

export interface VendorClassification {
  category: string;
  industry: string;
  tier: VendorTier;
  rationale: string;
}

export interface VendorClassificationResult {
  vendor_id: string;
  vendor_name: string;
  classification: VendorClassification | null;
  error: string | null;
}

export function classifyVendor(id: string) {
  return fetchJson<VendorClassificationResult>(
    `/api/v1/vendors/${id}/classify`,
    { method: "POST" },
  );
}

export interface BatchClassificationResponse {
  results: VendorClassificationResult[];
  classified: number;
  failed: number;
}

export function classifyVendorsBatch(onlyUnclassified = true) {
  return fetchJson<BatchClassificationResponse>(
    `/api/v1/vendors/classify-batch${qs({ only_unclassified: onlyUnclassified ? "true" : "false" })}`,
    { method: "POST" },
  );
}

export interface VendorEnrichmentResult {
  vendor_id: string;
  vendor_name: string;
  enrichment: VendorEnrichment | null;
  error: string | null;
}

export function enrichVendor(id: string) {
  return fetchJson<VendorEnrichmentResult>(`/api/v1/vendors/${id}/enrich`, {
    method: "POST",
  });
}

export function getVendor(id: string) {
  return fetchJson<Vendor>(`/api/v1/vendors/${id}`);
}

export function createVendor(body: VendorCreate) {
  return fetchJson<Vendor>("/api/v1/vendors", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateVendor(id: string, body: VendorUpdate) {
  return fetchJson<Vendor>(`/api/v1/vendors/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function deleteVendor(id: string) {
  return fetchVoid(`/api/v1/vendors/${id}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Purchase orders
// ---------------------------------------------------------------------------

export function listPurchaseOrders(
  params: {
    vendor_id?: string;
    status?: POStatus | "";
    limit?: number;
    offset?: number;
  } = {},
) {
  return fetchJson<Paginated<PurchaseOrder>>(
    `/api/v1/purchase-orders${qs(params)}`,
  );
}

export function getPurchaseOrder(id: string) {
  return fetchJson<PurchaseOrder>(`/api/v1/purchase-orders/${id}`);
}

export function createPurchaseOrder(body: PurchaseOrderCreate) {
  return fetchJson<PurchaseOrder>("/api/v1/purchase-orders", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updatePurchaseOrder(id: string, body: PurchaseOrderUpdate) {
  return fetchJson<PurchaseOrder>(`/api/v1/purchase-orders/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function deletePurchaseOrder(id: string) {
  return fetchVoid(`/api/v1/purchase-orders/${id}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// PO line items
// ---------------------------------------------------------------------------

export function listLineItems(
  params: { po_id?: string; limit?: number; offset?: number } = {},
) {
  return fetchJson<Paginated<POLineItem>>(`/api/v1/po-line-items${qs(params)}`);
}

export function createLineItem(body: POLineItemCreate) {
  return fetchJson<POLineItem>("/api/v1/po-line-items", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function updateLineItem(id: string, body: POLineItemUpdate) {
  return fetchJson<POLineItem>(`/api/v1/po-line-items/${id}`, {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export function deleteLineItem(id: string) {
  return fetchVoid(`/api/v1/po-line-items/${id}`, { method: "DELETE" });
}

// ---------------------------------------------------------------------------
// Settings — LLM provider config
// ---------------------------------------------------------------------------

export type LLMProvider = "ollama" | "openrouter" | "auto";

export interface LLMSettings {
  llm_provider: LLMProvider;
  ollama_base_url: string;
  ollama_model: string;
  openrouter_model: string;
  openrouter_base_url: string;
  openrouter_api_key_set: boolean;
  openrouter_api_key_preview: string;
  updated_at: string;
}

export interface LLMSettingsUpdate {
  llm_provider?: LLMProvider;
  ollama_base_url?: string;
  ollama_model?: string;
  openrouter_api_key?: string;
  openrouter_model?: string;
  openrouter_base_url?: string;
}

export function getLLMSettings() {
  return fetchJson<LLMSettings>("/api/v1/settings/llm");
}

export function updateLLMSettings(body: LLMSettingsUpdate) {
  return fetchJson<LLMSettings>("/api/v1/settings/llm", {
    method: "PATCH",
    body: JSON.stringify(body),
  });
}

export interface LLMTestResult {
  ok: boolean;
  provider: string;
  detail: string;
}

export function testLLMConnection() {
  return fetchJson<LLMTestResult>("/api/v1/settings/llm/test", { method: "POST" });
}

// ---------------------------------------------------------------------------
// Copilot
// ---------------------------------------------------------------------------

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface CopilotReply {
  reply: string;
  suggested_actions: string[];
}

export function chatCopilot(messages: ChatMessage[], vendorId?: string) {
  return fetchJson<CopilotReply>("/api/v1/copilot/chat", {
    method: "POST",
    body: JSON.stringify({ messages, vendor_id: vendorId ?? null }),
  });
}

export interface VendorEvaluation {
  risk_level: "low" | "medium" | "high";
  risk_flags: string[];
  performance_outlook: string;
  summary: string;
  recommendation: "approve" | "monitor" | "review" | "avoid";
}

export interface VendorEvaluationResult {
  vendor_id: string;
  vendor_name: string;
  evaluation: VendorEvaluation | null;
  error: string | null;
}

export function evaluateVendor(vendorId: string) {
  return fetchJson<VendorEvaluationResult>(
    `/api/v1/copilot/vendors/${vendorId}/evaluate`,
    { method: "POST" },
  );
}

// ---------------------------------------------------------------------------
// Onboarding (Phase 4)
// ---------------------------------------------------------------------------

export type OnboardingStatus =
  | "draft"
  | "collecting"
  | "pending_approval"
  | "approved"
  | "rejected"
  | "activated";
export type ApprovalStatus = "pending" | "approved" | "rejected";
export type DocumentStatus = "uploaded" | "validated" | "rejected";

export interface ChecklistItem {
  item: string;
  doc_type: string;
  required: boolean;
}

export interface ApprovalStep {
  id: string;
  step_order: number;
  name: string;
  approver_role: string | null;
  status: ApprovalStatus;
  decided_by: string | null;
  decided_at: string | null;
  comment: string | null;
}

export interface OnboardingDocument {
  id: string;
  doc_type: string;
  filename: string;
  content_type: string | null;
  size: number | null;
  status: DocumentStatus;
  validation: {
    valid: boolean;
    doc_type_detected: string;
    issues: string[];
  } | null;
  uploaded_at: string;
}

export interface OnboardingCase {
  id: string;
  vendor_id: string;
  status: OnboardingStatus;
  checklist: ChecklistItem[] | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
  documents: OnboardingDocument[];
  steps: ApprovalStep[];
}

export function listOnboardingCases(
  params: { vendor_id?: string; status?: OnboardingStatus | ""; limit?: number } = {},
) {
  return fetchJson<Paginated<OnboardingCase>>(`/api/v1/onboarding/cases${qs(params)}`);
}

export function getOnboardingCase(id: string) {
  return fetchJson<OnboardingCase>(`/api/v1/onboarding/cases/${id}`);
}

export function createOnboardingCase(body: {
  vendor_id: string;
  notes?: string | null;
  steps?: { name: string; approver_role?: string | null }[];
}) {
  return fetchJson<OnboardingCase>("/api/v1/onboarding/cases", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function deleteOnboardingCase(id: string) {
  return fetchVoid(`/api/v1/onboarding/cases/${id}`, { method: "DELETE" });
}

export function generateChecklist(id: string) {
  return fetchJson<OnboardingCase>(`/api/v1/onboarding/cases/${id}/checklist`, {
    method: "POST",
  });
}

export function submitOnboardingCase(id: string) {
  return fetchJson<OnboardingCase>(`/api/v1/onboarding/cases/${id}/submit`, {
    method: "POST",
  });
}

export function activateOnboardingCase(id: string) {
  return fetchJson<OnboardingCase>(`/api/v1/onboarding/cases/${id}/activate`, {
    method: "POST",
  });
}

export async function uploadOnboardingDocument(
  caseId: string,
  docType: string,
  file: File,
): Promise<OnboardingDocument> {
  const fd = new FormData();
  fd.append("doc_type", docType);
  fd.append("file", file);
  const res = await fetch(`${API_BASE}/api/v1/onboarding/cases/${caseId}/documents`, {
    method: "POST",
    body: fd, // no Content-Type — browser sets the multipart boundary
  });
  if (!res.ok) throw new ApiError(`API error ${res.status}`, res.status);
  return res.json();
}

export function validateDocument(docId: string) {
  return fetchJson<OnboardingDocument>(
    `/api/v1/onboarding/documents/${docId}/validate`,
    { method: "POST" },
  );
}

export function decideApprovalStep(
  stepId: string,
  body: { decision: "approve" | "reject"; decided_by?: string; comment?: string },
) {
  return fetchJson<OnboardingCase>(
    `/api/v1/onboarding/steps/${stepId}/decision`,
    { method: "POST", body: JSON.stringify(body) },
  );
}

// ---------------------------------------------------------------------------
// Performance (Phase 5)
// ---------------------------------------------------------------------------

export interface PerformanceScore {
  id: string;
  vendor_id: string;
  period: string;
  quality_score: number;
  delivery_score: number;
  cost_score: number;
  compliance_score: number;
  overall_score: number;
  kpis: Record<string, number>;
  summary: string | null;
  created_at: string;
}

export interface TrendPoint {
  period: string;
  overall_score: number;
  created_at: string;
}

export interface BenchmarkResult {
  vendor_id: string;
  vendor_overall: number | null;
  peer_group: string;
  peer_count: number;
  peer_average: number | null;
  percentile: number | null;
}

export function scoreVendorPerformance(vendorId: string, period?: string) {
  return fetchJson<PerformanceScore>(
    `/api/v1/performance/vendors/${vendorId}/score`,
    { method: "POST", body: JSON.stringify({ period: period ?? null }) },
  );
}

export async function getLatestScore(vendorId: string): Promise<PerformanceScore | null> {
  try {
    return await fetchJson<PerformanceScore>(
      `/api/v1/performance/vendors/${vendorId}/latest`,
    );
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

export function getScoreTrend(vendorId: string) {
  return fetchJson<TrendPoint[]>(`/api/v1/performance/vendors/${vendorId}/trend`);
}

export function getBenchmark(vendorId: string) {
  return fetchJson<BenchmarkResult>(
    `/api/v1/performance/vendors/${vendorId}/benchmark`,
  );
}

// ---------------------------------------------------------------------------
// Risk (Phase 6, V6.1)
// ---------------------------------------------------------------------------

export type RiskLevel = "low" | "medium" | "high";

export interface RiskFactor {
  type: string;
  severity: "low" | "medium" | "high";
  note: string;
}

export interface RiskAssessment {
  id: string;
  vendor_id: string;
  overall_level: RiskLevel;
  overall_score: number;
  factors: RiskFactor[];
  summary: string | null;
  created_at: string;
}

export interface RiskChange {
  type: string;
  change: "new" | "increased" | "decreased" | "resolved";
  from_severity: string | null;
  to_severity: string | null;
}

export interface RiskMonitorResult {
  assessment: RiskAssessment;
  changes: RiskChange[];
}

export function assessVendorRisk(vendorId: string) {
  return fetchJson<RiskMonitorResult>(`/api/v1/risk/vendors/${vendorId}/assess`, {
    method: "POST",
  });
}

export async function getLatestRisk(vendorId: string): Promise<RiskAssessment | null> {
  try {
    return await fetchJson<RiskAssessment>(`/api/v1/risk/vendors/${vendorId}/latest`);
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) return null;
    throw e;
  }
}

// ---------------------------------------------------------------------------
// Contracts (Phase 6, V6.2)
// ---------------------------------------------------------------------------

export type ContractStatus =
  | "draft"
  | "active"
  | "expiring"
  | "expired"
  | "terminated";

export interface Contract {
  id: string;
  vendor_id: string;
  title: string;
  status: ContractStatus;
  start_date: string | null;
  end_date: string | null;
  value: number | null;
  auto_renew: boolean;
  key_terms: Record<string, string | null> | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export interface ContractCreate {
  vendor_id: string;
  title: string;
  start_date?: string | null;
  end_date?: string | null;
  value?: number | null;
  auto_renew?: boolean;
  notes?: string | null;
}

export interface RenewalItem {
  contract_id: string;
  vendor_id: string;
  title: string;
  end_date: string | null;
  days_to_expiry: number | null;
  auto_renew: boolean;
  status: ContractStatus;
}

export function listContracts(params: { vendor_id?: string; status?: ContractStatus | "" } = {}) {
  return fetchJson<Paginated<Contract>>(`/api/v1/contracts${qs(params)}`);
}

export function createContract(body: ContractCreate) {
  return fetchJson<Contract>("/api/v1/contracts", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function deleteContract(id: string) {
  return fetchVoid(`/api/v1/contracts/${id}`, { method: "DELETE" });
}

export function extractContractTerms(id: string, text: string) {
  return fetchJson<Contract>(`/api/v1/contracts/${id}/extract`, {
    method: "POST",
    body: JSON.stringify({ text }),
  });
}

export function listRenewals() {
  return fetchJson<RenewalItem[]>("/api/v1/contracts/renewals");
}

export { ApiError };
