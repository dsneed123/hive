"use client";

import { useState, useEffect, useCallback } from "react";
import {
  CalendarEvent,
  getCalendarEvents,
  createCalendarEvent,
  updateCalendarEvent,
  deleteCalendarEvent,
} from "@/lib/api";

export function useCalendar() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1); // 1-indexed
  const [year, setYear] = useState(now.getFullYear());
  const [events, setEvents] = useState<CalendarEvent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEvents = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getCalendarEvents(month, year);
      setEvents(data);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load events");
    } finally {
      setLoading(false);
    }
  }, [month, year]);

  useEffect(() => {
    fetchEvents();
  }, [fetchEvents]);

  const addEvent = async (
    event: Omit<CalendarEvent, "id" | "created_at" | "updated_at">
  ) => {
    const created = await createCalendarEvent(event);
    setEvents((prev) => [...prev, created]);
    return created;
  };

  const editEvent = async (
    id: number,
    updates: Partial<Omit<CalendarEvent, "id" | "created_at" | "updated_at">>
  ) => {
    const updated = await updateCalendarEvent(id, updates);
    setEvents((prev) => prev.map((e) => (e.id === id ? updated : e)));
    return updated;
  };

  const removeEvent = async (id: number) => {
    await deleteCalendarEvent(id);
    setEvents((prev) => prev.filter((e) => e.id !== id));
  };

  const prevMonth = () => {
    if (month === 1) {
      setMonth(12);
      setYear((y) => y - 1);
    } else {
      setMonth((m) => m - 1);
    }
  };

  const nextMonth = () => {
    if (month === 12) {
      setMonth(1);
      setYear((y) => y + 1);
    } else {
      setMonth((m) => m + 1);
    }
  };

  return {
    month,
    year,
    events,
    loading,
    error,
    addEvent,
    editEvent,
    removeEvent,
    prevMonth,
    nextMonth,
    refresh: fetchEvents,
  };
}
