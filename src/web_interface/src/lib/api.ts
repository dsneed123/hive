const API_BASE = "http://localhost:8001/api";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface AnalyticsData {
  username: string;
  nickname: string;
  bio: string;
  followers: number;
  following: number;
  likes: number;
  videos: number;
  verified: boolean;
  avatar_url: string;
}

export interface SettingsData {
  claude_key: string;
  gmail_address: string;
  gmail_app_password: string;
}

// --- Accounts ---

export interface Account {
  id: number;
  username: string;
  tiktok_url: string;
  is_active: boolean;
  created_at: string;
}

// --- Emails ---

export interface Email {
  id: number;
  message_id: string;
  sender: string;
  subject: string;
  body_preview: string;
  category: string;
  is_read: boolean;
  ai_draft: string;
  received_at: string;
  fetched_at: string;
}

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || "Request failed");
  }
  return res.json();
}

export async function sendChatMessage(
  message: string,
  history: ChatMessage[]
): Promise<string> {
  const data = await request<{ response: string }>("/chat", {
    method: "POST",
    body: JSON.stringify({ message, history }),
  });
  return data.response;
}

export async function getAnalytics(): Promise<AnalyticsData> {
  return request<AnalyticsData>("/analytics");
}

export async function getSettings(): Promise<SettingsData> {
  const data = await request<{ settings: SettingsData }>("/settings");
  return data.settings;
}

export async function updateSettings(
  settings: Partial<SettingsData>
): Promise<{ settings: SettingsData; message: string }> {
  return request("/settings", {
    method: "PUT",
    body: JSON.stringify(settings),
  });
}

// --- Calendar ---

export interface CalendarEvent {
  id: number;
  title: string;
  description: string;
  date: string; // YYYY-MM-DD
  time: string;
  event_type: "post" | "idea" | "note";
  created_at: string;
  updated_at: string;
}

export async function getCalendarEvents(
  month: number,
  year: number
): Promise<CalendarEvent[]> {
  const data = await request<{ events: CalendarEvent[] }>(
    `/calendar?month=${month}&year=${year}`
  );
  return data.events;
}

export async function createCalendarEvent(
  event: Omit<CalendarEvent, "id" | "created_at" | "updated_at">
): Promise<CalendarEvent> {
  return request<CalendarEvent>("/calendar", {
    method: "POST",
    body: JSON.stringify(event),
  });
}

export async function updateCalendarEvent(
  id: number,
  event: Partial<Omit<CalendarEvent, "id" | "created_at" | "updated_at">>
): Promise<CalendarEvent> {
  return request<CalendarEvent>(`/calendar/${id}`, {
    method: "PUT",
    body: JSON.stringify(event),
  });
}

export async function deleteCalendarEvent(id: number): Promise<void> {
  await request(`/calendar/${id}`, { method: "DELETE" });
}

// --- Analytics History ---

export interface AnalyticsSnapshot {
  id: number;
  timestamp: string;
  username: string;
  nickname: string;
  followers: number;
  following: number;
  likes: number;
  videos: number;
}

export async function getAnalyticsHistory(
  days: number = 30
): Promise<AnalyticsSnapshot[]> {
  const data = await request<{ snapshots: AnalyticsSnapshot[] }>(
    `/analytics/history?days=${days}`
  );
  return data.snapshots;
}

// --- Accounts ---

export async function getAccounts(): Promise<Account[]> {
  const data = await request<{ accounts: Account[] }>("/accounts");
  return data.accounts;
}

export async function createAccount(
  username: string,
  tiktok_url: string
): Promise<Account> {
  return request<Account>("/accounts", {
    method: "POST",
    body: JSON.stringify({ username, tiktok_url }),
  });
}

export async function activateAccount(id: number): Promise<Account> {
  return request<Account>(`/accounts/${id}/activate`, { method: "PUT" });
}

export async function deleteAccount(id: number): Promise<void> {
  await request(`/accounts/${id}`, { method: "DELETE" });
}

// --- Emails ---

export async function getEmails(
  category: string = "",
  page: number = 1
): Promise<{ emails: Email[]; page: number }> {
  const params = new URLSearchParams();
  if (category) params.set("category", category);
  params.set("page", String(page));
  return request<{ emails: Email[]; page: number }>(`/emails?${params}`);
}

export async function getEmail(id: number): Promise<Email> {
  return request<Email>(`/emails/${id}`);
}

export async function fetchEmailsFromGmail(): Promise<{ message: string }> {
  return request<{ message: string }>("/emails/fetch", { method: "POST" });
}

export async function generateEmailDraft(
  id: number,
  instructions: string = ""
): Promise<Email> {
  return request<Email>(`/emails/${id}/draft`, {
    method: "POST",
    body: JSON.stringify({ instructions }),
  });
}

export async function sendEmailReply(
  id: number,
  body: string = ""
): Promise<{ message: string }> {
  return request<{ message: string }>(`/emails/${id}/send`, {
    method: "POST",
    body: JSON.stringify({ body }),
  });
}

export async function getEmailMode(): Promise<string> {
  const data = await request<{ mode: string }>("/emails/mode");
  return data.mode;
}

export async function setEmailMode(mode: string): Promise<string> {
  const data = await request<{ mode: string }>("/emails/mode", {
    method: "PUT",
    body: JSON.stringify({ mode }),
  });
  return data.mode;
}
