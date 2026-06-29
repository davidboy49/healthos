export type EvidenceRef = {
  kind: "derived_metric" | "raw_payload" | "activity" | "manual_event" | "snapshot";
  id: string;
  label: string;
  value?: number | string | null;
};

export type HealthInsight = {
  title: string;
  summary: string;
  evidence: EvidenceRef[];
  confidence: "low" | "medium" | "high";
  severity: "info" | "watch" | "important";
  category: "sleep" | "recovery" | "training" | "stress" | "experiment";
  recommendedAction?: string | null;
  medicalDisclaimerRequired: boolean;
};

export type MetricResponse = {
  id: string;
  name: string;
  value: number;
  unit: string;
  window_start: string;
  window_end: string;
  confidence: "low" | "medium" | "high";
  explanation: string;
  source_refs: Record<string, unknown>[];
};

export type TodayResponse = {
  date: string;
  readiness_score: number | null;
  sleep_score: number | null;
  hrv_status: string | null;
  stress_load: number | null;
  training_recommendation: string | null;
  missing_data: string[];
  top_insight: HealthInsight | null;
  metrics: MetricResponse[];
};

export type GarminStatusResponse = {
  connected: boolean;
  scopes: string[];
  last_sync_at: string | null;
  last_error: string | null;
};

const fallbackToday: TodayResponse = {
  date: new Date().toISOString().slice(0, 10),
  readiness_score: 72,
  sleep_score: 81,
  hrv_status: "near baseline",
  stress_load: 44,
  training_recommendation: "moderate training",
  missing_data: ["live Garmin token"],
  top_insight: {
    title: "Controlled training window",
    summary: "The dashboard is running in local preview mode. Once Garmin sync is connected, this area will show evidence-backed Hermes insights from computed metrics.",
    evidence: [{ kind: "snapshot", id: "preview", label: "Preview readiness", value: 72 }],
    confidence: "medium",
    severity: "watch",
    category: "recovery",
    recommendedAction: "Connect Garmin and run the first sync before trusting recommendations.",
    medicalDisclaimerRequired: false
  },
  metrics: [
    { id: "m1", name: "sleep_debt_7d", value: 55, unit: "minutes", window_start: new Date().toISOString(), window_end: new Date().toISOString(), confidence: "medium", explanation: "Preview sleep debt against an 8 hour target.", source_refs: [] },
    { id: "m2", name: "hrv_deviation", value: -4, unit: "%", window_start: new Date().toISOString(), window_end: new Date().toISOString(), confidence: "medium", explanation: "Preview HRV deviation from personal baseline.", source_refs: [] },
    { id: "m3", name: "training_load_ratio", value: 1.08, unit: "ratio", window_start: new Date().toISOString(), window_end: new Date().toISOString(), confidence: "medium", explanation: "Preview acute to chronic load ratio.", source_refs: [] }
  ]
};

const fallbackGarmin: GarminStatusResponse = {
  connected: false,
  scopes: [],
  last_sync_at: null,
  last_error: "Garmin OAuth is not connected in local preview."
};

async function apiFetch<T>(path: string, fallback: T): Promise<T> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
  try {
    const response = await fetch(`${baseUrl}${path}`, { cache: "no-store" });
    if (!response.ok) return fallback;
    return (await response.json()) as T;
  } catch {
    return fallback;
  }
}

export async function getToday(): Promise<TodayResponse> {
  return apiFetch<TodayResponse>("/health/today", fallbackToday);
}

export async function getGarminStatus(): Promise<GarminStatusResponse> {
  return apiFetch<GarminStatusResponse>("/garmin/status", fallbackGarmin);
}
