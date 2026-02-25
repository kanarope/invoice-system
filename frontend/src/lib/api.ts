import type { Invoice, InvoiceList, Department, Vendor, User, DashboardSummary, ComplianceCheck, AuditLogEntry } from "@/types";

const API = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

class ApiClient {
  private token: string | null = null;

  setToken(t: string) { this.token = t; if (typeof window !== "undefined") localStorage.setItem("token", t); }
  getToken(): string | null { if (!this.token && typeof window !== "undefined") this.token = localStorage.getItem("token"); return this.token; }
  clearToken() { this.token = null; if (typeof window !== "undefined") localStorage.removeItem("token"); }

  private async req<T>(path: string, opts: RequestInit = {}): Promise<T> {
    const h: Record<string, string> = { ...(opts.headers as Record<string, string>) };
    const tk = this.getToken();
    if (tk) h["Authorization"] = "Bearer " + tk;
    if (!(opts.body instanceof FormData)) h["Content-Type"] = "application/json";
    const r = await fetch(API + path, { ...opts, headers: h });
    if (r.status === 401) { this.clearToken(); if (typeof window !== "undefined") window.location.href = "/login"; throw new Error("認証エラー"); }
    if (!r.ok) { const e = await r.json().catch(() => ({ detail: r.statusText })); throw new Error(e.detail || "APIエラー"); }
    return r.json();
  }

  get<T>(p: string) { return this.req<T>(p); }
  post<T>(p: string, b?: unknown) { return this.req<T>(p, { method: "POST", body: b instanceof FormData ? b : JSON.stringify(b) }); }
  put<T>(p: string, b: unknown) { return this.req<T>(p, { method: "PUT", body: JSON.stringify(b) }); }
  del<T>(p: string) { return this.req<T>(p, { method: "DELETE" }); }

  login(email: string, password: string) { return this.post<{ access_token: string }>("/api/auth/login", { email, password }); }
  me() { return this.get<User>("/api/auth/me"); }
  uploadInvoices(files: File[]) { const fd = new FormData(); files.forEach(f => fd.append("files", f)); return this.post<Invoice[]>("/api/invoices/upload", fd); }
  getInvoices(p: Record<string, string | number> = {}) { const q = new URLSearchParams(); Object.entries(p).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== "") q.set(k, String(v)); }); return this.get<InvoiceList>("/api/invoices?" + q); }
  getInvoice(id: number) { return this.get<Invoice>("/api/invoices/" + id); }
  updateInvoice(id: number, d: Partial<Invoice>) { return this.put<Invoice>("/api/invoices/" + id, d); }
  approveInvoice(id: number) { return this.post<Invoice>("/api/invoices/" + id + "/approve"); }
  rejectInvoice(id: number) { return this.post<Invoice>("/api/invoices/" + id + "/reject"); }
  deleteInvoice(id: number) { return this.del<{ ok: boolean }>("/api/invoices/" + id); }
  verifyHash(id: number) { return this.get<{ valid: boolean }>("/api/invoices/" + id + "/verify-hash"); }
  executeTransfer(id: number) { return this.post<{ ok: boolean }>("/api/transfers/" + id + "/execute"); }
  getMfAuthUrl() { return this.get<{ url: string }>("/api/transfers/mf/auth-url"); }
  getDepartments() { return this.get<Department[]>("/api/departments"); }
  createDepartment(d: { name: string; code: string }) { return this.post<Department>("/api/departments", d); }
  updateDepartment(id: number, d: Partial<Department>) { return this.put<Department>("/api/departments/" + id, d); }
  getVendors() { return this.get<Vendor[]>("/api/vendors"); }
  checkCompliance(id: number) { return this.post<ComplianceCheck>("/api/compliance/check/" + id); }
  getComplianceDashboard() { return this.get<{ total_invoices: number; valid_registration: number; invalid_registration: number; unchecked_registration: number }>("/api/compliance/dashboard"); }
  getDashboard() { return this.get<DashboardSummary>("/api/dashboard/summary"); }
  getAuditLogs(p: Record<string, string | number> = {}) { const q = new URLSearchParams(); Object.entries(p).forEach(([k, v]) => { if (v !== undefined && v !== null && v !== "") q.set(k, String(v)); }); return this.get<AuditLogEntry[]>("/api/audit?" + q); }
  fetchGmail() { return this.post<{ ok: boolean; created_count: number }>("/api/gmail/fetch"); }
  getUsers() { return this.get<User[]>("/api/users"); }
  createUser(d: { email: string; name: string; password: string; role: string; department_id?: number }) { return this.post<User>("/api/users", d); }
}

export const api = new ApiClient();
