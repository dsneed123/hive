"use client";

import { useState, useCallback } from "react";
import {
  getAnalytics,
  getAnalyticsHistory,
  type AnalyticsData,
  type AnalyticsSnapshot,
} from "@/lib/api";

export interface DerivedMetrics {
  engagementRate: number;
  avgLikesPerVideo: number;
  followRatio: number;
}

function deriveMetrics(data: AnalyticsData): DerivedMetrics {
  const avgLikesPerVideo = data.videos > 0 ? data.likes / data.videos : 0;
  const engagementRate =
    data.followers > 0 ? (avgLikesPerVideo / data.followers) * 100 : 0;
  const followRatio =
    data.following > 0 ? data.followers / data.following : data.followers;

  return { engagementRate, avgLikesPerVideo, followRatio };
}

export function useAnalytics() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [derived, setDerived] = useState<DerivedMetrics | null>(null);
  const [history, setHistory] = useState<AnalyticsSnapshot[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  const fetch = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [analytics, snapshots] = await Promise.all([
        getAnalytics(),
        getAnalyticsHistory(30),
      ]);
      setData(analytics);
      setDerived(deriveMetrics(analytics));
      setHistory(snapshots);
      setLastUpdated(new Date());
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load analytics");
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, derived, history, loading, error, lastUpdated, refresh: fetch };
}
