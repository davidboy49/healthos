import { Activity, Brain, CalendarDays, DatabaseZap, Dumbbell, HeartPulse, Moon, ShieldCheck, Sparkles, Watch } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { getGarminStatus, getToday, type MetricResponse } from "@/lib/api";

const nav = [
  { label: "Today", icon: HeartPulse },
  { label: "Timeline", icon: CalendarDays },
  { label: "Sleep", icon: Moon },
  { label: "Recovery", icon: Activity },
  { label: "Training", icon: Dumbbell },
  { label: "Insights", icon: Brain },
  { label: "Data", icon: DatabaseZap }
];

function scoreTone(score: number | null) {
  if (score === null) return "neutral" as const;
  if (score >= 76) return "good" as const;
  if (score >= 55) return "warn" as const;
  return "danger" as const;
}

function MetricTile({ label, value, unit, tone = "neutral" }: { label: string; value: string | number; unit?: string; tone?: "neutral" | "good" | "warn" | "danger" }) {
  return (
    <div className="min-h-28 rounded-lg border bg-background/55 p-4">
      <div className="text-xs font-medium uppercase text-muted-foreground">{label}</div>
      <div className="mt-3 flex items-end gap-2">
        <span className="text-3xl font-semibold leading-none">{value}</span>
        {unit ? <span className="pb-1 text-sm text-muted-foreground">{unit}</span> : null}
      </div>
      <Badge className="mt-4" tone={tone}>{tone === "good" ? "strong" : tone === "warn" ? "watch" : tone === "danger" ? "low" : "pending"}</Badge>
    </div>
  );
}

function MetricRow({ metric }: { metric: MetricResponse }) {
  return (
    <div className="grid gap-3 border-b py-3 last:border-b-0 md:grid-cols-[180px_100px_1fr]">
      <div className="font-medium">{metric.name.replaceAll("_", " ")}</div>
      <div className="text-muted-foreground">{metric.value} {metric.unit}</div>
      <div className="text-sm text-muted-foreground">{metric.explanation}</div>
    </div>
  );
}

export default async function DashboardPage() {
  const [today, garmin] = await Promise.all([getToday(), getGarminStatus()]);
  const readiness = today.readiness_score;
  const insight = today.top_insight;

  return (
    <main className="min-h-screen bg-background">
      <aside className="fixed inset-y-0 left-0 hidden w-20 border-r bg-card/80 px-3 py-5 backdrop-blur lg:block">
        <div className="flex h-11 w-11 items-center justify-center rounded-lg bg-primary text-primary-foreground">
          <HeartPulse className="h-5 w-5" aria-hidden />
        </div>
        <nav className="mt-8 flex flex-col gap-2" aria-label="Primary">
          {nav.map((item) => (
            <button key={item.label} title={item.label} className="flex h-11 w-11 items-center justify-center rounded-md text-muted-foreground transition hover:bg-muted hover:text-foreground">
              <item.icon className="h-5 w-5" aria-hidden />
              <span className="sr-only">{item.label}</span>
            </button>
          ))}
        </nav>
      </aside>

      <div className="lg:pl-20">
        <header className="border-b bg-card/70 px-4 py-4 backdrop-blur md:px-8">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div>
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Watch className="h-4 w-4" aria-hidden />
                Garmin fenix pipeline
              </div>
              <h1 className="mt-1 text-2xl font-semibold leading-tight md:text-3xl">Personal Health OS</h1>
            </div>
            <div className="flex flex-wrap items-center gap-2">
              <Badge tone={garmin.connected ? "good" : "warn"}>{garmin.connected ? "Garmin connected" : "Garmin pending"}</Badge>
              <Badge tone={today.missing_data.length ? "warn" : "good"}>{today.missing_data.length ? `${today.missing_data.length} data gaps` : "data complete"}</Badge>
              <Button variant="secondary"><ShieldCheck className="h-4 w-4" aria-hidden /> Evidence mode</Button>
            </div>
          </div>
        </header>

        <section className="grid gap-4 px-4 py-5 md:grid-cols-2 md:px-8 xl:grid-cols-4">
          <MetricTile label="Readiness" value={readiness ?? "--"} unit={readiness === null ? undefined : "/100"} tone={scoreTone(readiness)} />
          <MetricTile label="Sleep" value={today.sleep_score ?? "--"} unit={today.sleep_score === null ? undefined : "/100"} tone={scoreTone(today.sleep_score)} />
          <MetricTile label="HRV" value={today.hrv_status ?? "pending"} tone={today.hrv_status ? "good" : "neutral"} />
          <MetricTile label="Stress load" value={today.stress_load ?? "--"} unit={today.stress_load === null ? undefined : "pts"} tone={today.stress_load !== null && today.stress_load < 55 ? "good" : "warn"} />
        </section>

        <section className="grid gap-4 px-4 pb-8 md:px-8 xl:grid-cols-[1.15fr_0.85fr]">
          <Card>
            <CardHeader>
              <CardTitle>Today</CardTitle>
              <Badge tone={scoreTone(readiness)}>{today.training_recommendation ?? "awaiting sync"}</Badge>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-3">
                <div className="md:col-span-2">
                  <div className="flex items-center gap-2 text-sm font-medium text-muted-foreground">
                    <Sparkles className="h-4 w-4" aria-hidden /> Hermes daily coach
                  </div>
                  <h2 className="mt-2 text-xl font-semibold">{insight?.title ?? "No insight generated yet"}</h2>
                  <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">{insight?.summary ?? "Run the daily agent job after Garmin sync to generate an evidence-backed brief."}</p>
                  {insight?.recommendedAction ? <p className="mt-4 rounded-lg border bg-muted/40 p-4 text-sm">{insight.recommendedAction}</p> : null}
                </div>
                <div className="rounded-lg border bg-background/55 p-4">
                  <div className="text-sm font-medium">Evidence</div>
                  <div className="mt-3 space-y-2">
                    {(insight?.evidence ?? []).map((item) => (
                      <div key={`${item.kind}-${item.id}`} className="flex items-center justify-between gap-3 text-sm">
                        <span className="text-muted-foreground">{item.label}</span>
                        <span className="font-medium">{item.value ?? item.kind}</span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Data Health</CardTitle>
              <Badge tone={garmin.last_error ? "warn" : "good"}>{garmin.last_sync_at ? "synced" : "not synced"}</Badge>
            </CardHeader>
            <CardContent>
              <div className="space-y-3 text-sm">
                <div className="flex justify-between gap-4"><span className="text-muted-foreground">Last Garmin sync</span><span>{garmin.last_sync_at ?? "never"}</span></div>
                <div className="flex justify-between gap-4"><span className="text-muted-foreground">Scopes</span><span>{garmin.scopes.length || "none"}</span></div>
                <div className="flex justify-between gap-4"><span className="text-muted-foreground">Missing data</span><span>{today.missing_data.join(", ") || "none"}</span></div>
                {garmin.last_error ? <p className="rounded-lg border border-warning/30 bg-warning/10 p-3 text-warning">{garmin.last_error}</p> : null}
              </div>
            </CardContent>
          </Card>
        </section>

        <section className="grid gap-4 px-4 pb-10 md:px-8 xl:grid-cols-[0.9fr_1.1fr]">
          <Card>
            <CardHeader><CardTitle>Derived Metrics</CardTitle></CardHeader>
            <CardContent>
              {today.metrics.map((metric) => <MetricRow key={metric.id} metric={metric} />)}
            </CardContent>
          </Card>

          <Card>
            <CardHeader><CardTitle>Operating Loop</CardTitle></CardHeader>
            <CardContent>
              <div className="grid gap-3 md:grid-cols-2">
                {["Garmin raw payload stored", "Normalization complete", "Metrics computed", "Hermes insight generated", "Evidence reviewed", "Experiment updated"].map((step, index) => (
                  <div key={step} className="flex items-center gap-3 rounded-lg border bg-background/55 p-3 text-sm">
                    <span className="flex h-7 w-7 items-center justify-center rounded-md bg-primary/15 text-xs font-semibold text-primary">{index + 1}</span>
                    <span>{step}</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </section>
      </div>
    </main>
  );
}
