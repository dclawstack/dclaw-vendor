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
export type POStatus = "draft" | "sent" | "partial" | "received" | "cancelled";

export interface Vendor {
  id: string;
  name: string;
  contact_name: string | null;
  email: string | null;
  phone: string | null;
  address: string | null;
  payment_terms: string | null;
  status: VendorStatus;
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
    limit?: number;
    offset?: number;
  } = {},
) {
  return fetchJson<Paginated<Vendor>>(`/api/v1/vendors${qs(params)}`);
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

export { ApiError };
