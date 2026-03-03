"use client";

import { useEffect } from "react";
import Link from "next/link";
import { Users, Heart, UserPlus, Video, MessageSquare, BarChart3, Settings, RefreshCw } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useAnalytics } from "@/hooks/use-analytics";

function formatNumber(n: number): string {
  if (n >= 1_000_000) return (n / 1_000_000).toFixed(1) + "M";
  if (n >= 1_000) return (n / 1_000).toFixed(1) + "K";
  return n.toString();
}

export default function DashboardPage() {
  const { data, loading, error, lastUpdated, refresh } = useAnalytics();

  useEffect(() => {
    refresh();
  }, [refresh]);

  const stats = [
    { label: "Followers", value: data?.followers ?? 0, icon: Users, color: "text-amber-500" },
    { label: "Likes", value: data?.likes ?? 0, icon: Heart, color: "text-rose-500" },
    { label: "Following", value: data?.following ?? 0, icon: UserPlus, color: "text-blue-500" },
    { label: "Videos", value: data?.videos ?? 0, icon: Video, color: "text-emerald-500" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            {data?.username ? `Welcome back, @${data.username}` : "Your Hive overview"}
          </p>
          {lastUpdated && (
            <p className="text-xs text-muted-foreground/60">
              Last updated: {lastUpdated.toLocaleTimeString()}
            </p>
          )}
        </div>
        <Button variant="outline" size="icon" onClick={refresh} disabled={loading}>
          <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
        </Button>
      </div>

      {error && (
        <Card className="border-amber-500/50 bg-amber-500/10">
          <CardContent className="p-4 text-sm text-amber-600 dark:text-amber-400">
            {error} — Add a TikTok account in Settings to see live data.
          </CardContent>
        </Card>
      )}

      {/* Loading skeletons */}
      {loading && !data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Card key={i}>
              <CardHeader className="flex flex-row items-center justify-between pb-2">
                <div className="h-4 w-20 animate-pulse rounded bg-muted" />
                <div className="h-4 w-4 animate-pulse rounded bg-muted" />
              </CardHeader>
              <CardContent>
                <div className="h-7 w-16 animate-pulse rounded bg-muted" />
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {data && (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          {stats.map((stat) => (
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
      )}

      <div>
        <h2 className="mb-3 text-lg font-semibold">Quick Actions</h2>
        <div className="grid gap-3 sm:grid-cols-3">
          <Link href="/chat">
            <Card className="cursor-pointer transition-colors hover:bg-accent">
              <CardContent className="flex items-center gap-3 p-4">
                <MessageSquare className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">Chat with Hive</p>
                  <p className="text-xs text-muted-foreground">Get AI growth advice</p>
                </div>
              </CardContent>
            </Card>
          </Link>
          <Link href="/analytics">
            <Card className="cursor-pointer transition-colors hover:bg-accent">
              <CardContent className="flex items-center gap-3 p-4">
                <BarChart3 className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">View Analytics</p>
                  <p className="text-xs text-muted-foreground">See detailed metrics</p>
                </div>
              </CardContent>
            </Card>
          </Link>
          <Link href="/settings">
            <Card className="cursor-pointer transition-colors hover:bg-accent">
              <CardContent className="flex items-center gap-3 p-4">
                <Settings className="h-5 w-5 text-primary" />
                <div>
                  <p className="font-medium">Settings</p>
                  <p className="text-xs text-muted-foreground">Configure your account</p>
                </div>
              </CardContent>
            </Card>
          </Link>
        </div>
      </div>
    </div>
  );
}
