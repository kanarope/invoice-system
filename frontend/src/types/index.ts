export interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  department_id: number | null;
  is_active: boolean;
  created_at: string;
}

export interface Department {
  id: number;
  name: string;
  code: string;
  is_active: boolean;
  created_at: string;
}

export interface Vendor {
  id: number;
  name: string;
  invoice_registration_number: string | null;
  registration_status: string | null;
  default_department_id: number | null;
  created_at: string;
}

export interface InvoiceDetail {
  id: number;
  description: string | null;
  amount: string | null;
  tax: string | null;
  tax_rate: string | null;
}

export interface BankAccount {
  id: number;
  bank_name: string | null;
  branch_name: string | null;
  account_type: string | null;
  account_number: string | null;
  account_holder: string | null;
}

export interface Invoice {
  id: number;
  invoice_number: string | null;
  vendor_id: number | null;
  department_id: number | null;
  status: string;
  invoice_date: string | null;
  due_date: string | null;
  total_amount: string | null;
  tax_amount: string | null;
  tax_8_amount: string | null;
  tax_10_amount: string | null;
  subtotal_amount: string | null;
  file_path: string | null;
  file_hash_sha256: string | null;
  original_filename: string | null;
  source_type: string;
  invoice_registration_number: string | null;
  invoice_registration_status: string | null;
  ai_raw_result: Record<string, unknown> | null;
  compliance_check_result: ComplianceCheck | null;
  is_deleted: boolean;
  retention_until: string | null;
  description: string | null;
  recipient_name: string | null;
  created_at: string;
  updated_at: string;
  approved_at: string | null;
  details: InvoiceDetail[];
  bank_account: BankAccount | null;
  vendor_name: string | null;
  department_name: string | null;
}

export interface InvoiceList {
  items: Invoice[];
  total: number;
  page: number;
  per_page: number;
}

export interface ComplianceCheck {
  has_registration_number: boolean;
  has_invoice_date: boolean;
  has_description: boolean;
  has_tax_breakdown: boolean;
  has_tax_amount: boolean;
  has_recipient_name: boolean;
  registration_valid: boolean | null;
  missing_items: string[];
  passed: boolean;
}

export interface DashboardSummary {
  total_invoices: number;
  by_status: Record<string, number>;
  upcoming_due_7days: number;
  overdue: number;
  by_department: { name: string; total_amount: number; count: number }[];
}

export interface AuditLogEntry {
  id: number;
  user_id: number | null;
  entity_type: string;
  entity_id: number;
  action: string;
  old_values: Record<string, unknown> | null;
  new_values: Record<string, unknown> | null;
  ip_address: string | null;
  created_at: string;
}
