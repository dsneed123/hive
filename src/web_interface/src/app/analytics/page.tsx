"use client";

import { useEffect } from "react";
import { RefreshCw, Users, Heart, UserPlus, Video, BadgeCheck, TrendingUp, Percent } from "lucide-react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell, Legend, type PieLabelRenderProps, LineChart, Line } from "recharts";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAnalytics } from "@/hooks/use-analytics";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return n.toString();
}

function SkeletonCard() {
  return (
    <Card>
      <CardHeader className="flex flex-row items-center justify-between pb-2">
        <div className="h-4 w-20 animate-pulse rounded bg-muted" />
        <div className="h-4 w-4 animate-pulse rounded bg-muted" />
      </CardHeader>
      <CardContent>
        <div className="h-7 w-16 animate-pulse rounded bg-muted" />
      </CardContent>
    </Card>
  );
}

function SkeletonProfile() {
  return (
    <Card>
      <CardContent className="flex items-center gap-4 p-6">
        <div className="h-16 w-16 animate-pulse rounded-full bg-muted" />
        <div className="space-y-2">
          <div className="h-5 w-32 animate-pulse rounded bg-muted" />
          <div className="h-4 w-20 animate-pulse rounded bg-muted" />
          <div className="h-4 w-48 animate-pulse rounded bg-muted" />
        </div>
      </CardContent>
    </Card>
  );
}

const PIE_COLORS = ["#f59e0b", "#ef4444", "#3b82f6", "#10b981"];

export default function AnalyticsPage() {
  const { data, derived, history, loading, error, lastUpdated, refresh } = useAnalytics();

  useEffect(() => {
    refresh();
  }, [refresh]);

  const chartData = data
    ? [
        { name: "Followers", value: data.followers, fill: "#f59e0b" },
        { name: "Likes", value: data.likes, fill: "#ef4444" },
        { name: "Following", value: data.following, fill: "#3b82f6" },
        { name: "Videos", value: data.videos, fill: "#10b981" },
      ]
    : [];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Analytics</h1>
          <p className="text-muted-foreground">Your TikTok performance overview</p>
          {lastUpdated && (
            <p className="text-xs text-muted-foreground/60">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>
        <Button variant="outline" size="sm" onClick={refresh} disabled={loading}>
          <RefreshCw className={`mr-2 h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          Refresh
        </Button>
      </div>

      {/* Error */}
      {error && (
        <Card className="border-amber-500/50 bg-amber-500/10">
          <CardContent className="p-4 text-sm text-amber-600 dark:text-amber-400">
            {error} — Make sure your TikTok URL is configured in Settings.
          </CardContent>
        </Card>
      )}

      {/* Loading skeletons */}
      {loading && !data && (
        <>
          <SkeletonProfile />
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 4 }).map((_, i) => (
              <SkeletonCard key={i} />
            ))}
          </div>
        </>
      )}

      {data && (
        <>
          {/* Profile card */}
          <Card>
            <CardContent className="flex items-center gap-4 p-6">
              {data.avatar_url ? (
                <img
                  src={data.avatar_url}
                  alt={data.nickname}
                  className="h-16 w-16 rounded-full object-cover"
                />
              ) : (
                <div className="flex h-16 w-16 items-center justify-center rounded-full bg-primary/15 text-2xl font-bold text-primary">
                  {(data.nickname || data.username || "?")[0].toUpperCase()}
                </div>
              )}
              <div>
                <div className="flex items-center gap-2">
                  <h2 className="text-xl font-bold">{data.nickname || data.username}</h2>
                  {data.verified && <BadgeCheck className="h-5 w-5 text-primary" />}
                </div>
                {data.username && (
                  <p className="text-sm text-muted-foreground">@{data.username}</p>
                )}
                {data.bio && <p className="mt-1 text-sm">{data.bio}</p>}
              </div>
            </CardContent>
          </Card>

          {/* Core metrics grid */}
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {[
              { label: "Followers", value: data.followers, icon: Users, color: "text-amber-500" },
              { label: "Likes", value: data.likes, icon: Heart, color: "text-rose-500" },
              { label: "Following", value: data.following, icon: UserPlus, color: "text-blue-500" },
              { label: "Videos", value: data.videos, icon: Video, color: "text-emerald-500" },
            ].map((stat) => (
              <Card key={stat.label}>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">{stat.label}</CardTitle>
                  <stat.icon className={`h-4 w-4 ${stat.color}`} />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatNumber(stat.value)}</div>
                </CardContent>
              </Card>
            ))}
          </div>

          {/* Derived metrics */}
          {derived && (
            <div className="grid gap-4 sm:grid-cols-3">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Engagement Rate</CardTitle>
                  <Percent className="h-4 w-4 text-violet-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{derived.engagementRate.toFixed(2)}%</div>
                  <p className="text-xs text-muted-foreground">Avg likes per video / followers</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Avg Likes / Video</CardTitle>
                  <TrendingUp className="h-4 w-4 text-pink-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{formatNumber(Math.round(derived.avgLikesPerVideo))}</div>
                  <p className="text-xs text-muted-foreground">Total likes / total videos</p>
                </CardContent>
              </Card>
              <Card>
                <CardHeader className="flex flex-row items-center justify-between pb-2">
                  <CardTitle className="text-sm font-medium text-muted-foreground">Follow Ratio</CardTitle>
                  <Users className="h-4 w-4 text-cyan-500" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{derived.followRatio.toFixed(1)}x</div>
                  <p className="text-xs text-muted-foreground">Followers / following</p>
                </CardContent>
              </Card>
            </div>
          )}

          {/* Charts row */}
          <div className="grid gap-4 lg:grid-cols-2">
            {/* Bar chart */}
            <Card>
              <CardHeader>
                <CardTitle>Metrics Overview</CardTitle>
                <CardDescription>Visual breakdown of your TikTok metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData}>
                      <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                      <XAxis dataKey="name" className="text-xs" />
                      <YAxis className="text-xs" tickFormatter={(v) => formatNumber(v)} />
                      <Tooltip
                        formatter={(value) => [formatNumber(value as number), "Count"]}
                        contentStyle={{
                          backgroundColor: "var(--card)",
                          border: "1px solid var(--border)",
                          borderRadius: "0.5rem",
                          color: "var(--foreground)",
                        }}
                      />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]} />
                    </BarChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>

            {/* Pie chart */}
            <Card>
              <CardHeader>
                <CardTitle>Distribution</CardTitle>
                <CardDescription>Proportional breakdown of account metrics</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="h-64">
                  <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                      <Pie
                        data={chartData}
                        dataKey="value"
                        nameKey="name"
                        cx="50%"
                        cy="50%"
                        outerRadius={80}
                        label={(props: PieLabelRenderProps) => `${props.name ?? ""} ${(((props.percent as number) ?? 0) * 100).toFixed(0)}%`}
                      >
                        {chartData.map((entry, index) => (
                          <Cell key={entry.name} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                        ))}
                      </Pie>
                      <Tooltip
                        formatter={(value) => [formatNumber(value as number), "Count"]}
                        contentStyle={{
                          backgroundColor: "var(--card)",
                          border: "1px solid var(--border)",
                          borderRadius: "0.5rem",
                          color: "var(--foreground)",
                        }}
                      />
                      <Legend />
                    </PieChart>
                  </ResponsiveContainer>
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Growth Over Time */}
          {history.length > 1 && (
            <div className="grid gap-4 lg:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>Follower Growth</CardTitle>
                  <CardDescription>Followers over time (last 30 days)</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={history.map((s) => ({
                        date: new Date(s.timestamp).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
                        followers: s.followers,
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                        <XAxis dataKey="date" className="text-xs" />
                        <YAxis className="text-xs" tickFormatter={(v) => formatNumber(v)} />
                        <Tooltip
                          formatter={(value) => [formatNumber(value as number), "Followers"]}
                          contentStyle={{
                            backgroundColor: "var(--card)",
                            border: "1px solid var(--border)",
                            borderRadius: "0.5rem",
                            color: "var(--foreground)",
                          }}
                        />
                        <Line type="monotone" dataKey="followers" stroke="#f59e0b" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Likes Growth</CardTitle>
                  <CardDescription>Total likes over time (last 30 days)</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={history.map((s) => ({
                        date: new Date(s.timestamp).toLocaleDateString("en-US", { month: "short", day: "numeric" }),
                        likes: s.likes,
                      }))}>
                        <CartesianGrid strokeDasharray="3 3" className="stroke-border" />
                        <XAxis dataKey="date" className="text-xs" />
                        <YAxis className="text-xs" tickFormatter={(v) => formatNumber(v)} />
                        <Tooltip
                          formatter={(value) => [formatNumber(value as number), "Likes"]}
                          contentStyle={{
                            backgroundColor: "var(--card)",
                            border: "1px solid var(--border)",
                            borderRadius: "0.5rem",
                            color: "var(--foreground)",
                          }}
                        />
                        <Line type="monotone" dataKey="likes" stroke="#ef4444" strokeWidth={2} dot={false} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </CardContent>
              </Card>
            </div>
          )}

          {history.length <= 1 && (
            <Card className="border-dashed">
              <CardContent className="p-6 text-center text-sm text-muted-foreground">
                Growth charts will appear here once analytics have been tracked over multiple sessions. Keep refreshing to build your history.
              </CardContent>
            </Card>
          )}
        </>
      )}
    </div>
  );
}
