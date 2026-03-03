"use client";

import { useState } from "react";
import { useCalendar } from "@/hooks/use-calendar";
import { CalendarEvent } from "@/lib/api";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
  DialogDescription,
} from "@/components/ui/dialog";
import {
  ChevronLeft,
  ChevronRight,
  Plus,
  Trash2,
  Loader2,
} from "lucide-react";

const MONTH_NAMES = [
  "January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December",
];

const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

const EVENT_COLORS: Record<string, string> = {
  post: "bg-amber-500/20 text-amber-400 border-amber-500/40",
  idea: "bg-blue-500/20 text-blue-400 border-blue-500/40",
  note: "bg-stone-500/20 text-stone-400 border-stone-500/40",
};

const EVENT_LABELS: Record<string, string> = {
  post: "Scheduled Post",
  idea: "Content Idea",
  note: "Note",
};

function getDaysInMonth(month: number, year: number) {
  return new Date(year, month, 0).getDate();
}

function getFirstDayOfWeek(month: number, year: number) {
  return new Date(year, month - 1, 1).getDay();
}

export default function CalendarPage() {
  const {
    month, year, events, loading, error,
    addEvent, editEvent, removeEvent, prevMonth, nextMonth,
  } = useCalendar();

  const [dialogOpen, setDialogOpen] = useState(false);
  const [selectedDate, setSelectedDate] = useState("");
  const [editingEvent, setEditingEvent] = useState<CalendarEvent | null>(null);
  const [formTitle, setFormTitle] = useState("");
  const [formDescription, setFormDescription] = useState("");
  const [formTime, setFormTime] = useState("");
  const [formType, setFormType] = useState<"post" | "idea" | "note">("idea");
  const [saving, setSaving] = useState(false);

  const daysInMonth = getDaysInMonth(month, year);
  const firstDay = getFirstDayOfWeek(month, year);

  const openNewEvent = (date: string) => {
    setEditingEvent(null);
    setSelectedDate(date);
    setFormTitle("");
    setFormDescription("");
    setFormTime("");
    setFormType("idea");
    setDialogOpen(true);
  };

  const openEditEvent = (event: CalendarEvent) => {
    setEditingEvent(event);
    setSelectedDate(event.date);
    setFormTitle(event.title);
    setFormDescription(event.description);
    setFormTime(event.time);
    setFormType(event.event_type);
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!formTitle.trim()) return;
    setSaving(true);
    try {
      if (editingEvent) {
        await editEvent(editingEvent.id, {
          title: formTitle,
          description: formDescription,
          date: selectedDate,
          time: formTime,
          event_type: formType,
        });
      } else {
        await addEvent({
          title: formTitle,
          description: formDescription,
          date: selectedDate,
          time: formTime,
          event_type: formType,
        });
      }
      setDialogOpen(false);
    } catch {
      // error handled by hook
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!editingEvent) return;
    setSaving(true);
    try {
      await removeEvent(editingEvent.id);
      setDialogOpen(false);
    } catch {
      // error handled by hook
    } finally {
      setSaving(false);
    }
  };

  const getEventsForDay = (day: number) => {
    const dateStr = `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`;
    return events.filter((e) => e.date === dateStr);
  };

  const today = new Date();
  const isToday = (day: number) =>
    today.getFullYear() === year &&
    today.getMonth() + 1 === month &&
    today.getDate() === day;

  // Build calendar grid cells
  const cells: (number | null)[] = [];
  for (let i = 0; i < firstDay; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold">Content Calendar</h1>
          <p className="text-sm text-muted-foreground">
            Plan and schedule your content
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" size="icon" onClick={prevMonth}>
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <span className="min-w-[160px] text-center font-semibold">
            {MONTH_NAMES[month - 1]} {year}
          </span>
          <Button variant="outline" size="icon" onClick={nextMonth}>
            <ChevronRight className="h-4 w-4" />
          </Button>
        </div>
      </div>

      {/* Legend */}
      <div className="flex gap-4 text-sm">
        {Object.entries(EVENT_LABELS).map(([type, label]) => (
          <div key={type} className="flex items-center gap-1.5">
            <span className={`inline-block h-3 w-3 rounded-sm border ${EVENT_COLORS[type]}`} />
            <span className="text-muted-foreground">{label}</span>
          </div>
        ))}
      </div>

      {error && (
        <Card className="border-destructive">
          <CardContent className="p-4 text-sm text-destructive">{error}</CardContent>
        </Card>
      )}

      {/* Calendar Grid */}
      <Card>
        <CardContent className="p-0">
          {/* Day headers */}
          <div className="grid grid-cols-7 border-b">
            {DAY_NAMES.map((d) => (
              <div key={d} className="p-2 text-center text-xs font-medium text-muted-foreground">
                {d}
              </div>
            ))}
          </div>

          {/* Day cells */}
          {loading ? (
            <div className="flex items-center justify-center py-24">
              <Loader2 className="h-6 w-6 animate-spin text-muted-foreground" />
            </div>
          ) : (
            <div className="grid grid-cols-7">
              {cells.map((day, i) => {
                const dayEvents = day ? getEventsForDay(day) : [];
                const dateStr = day
                  ? `${year}-${String(month).padStart(2, "0")}-${String(day).padStart(2, "0")}`
                  : "";

                return (
                  <div
                    key={i}
                    className={`min-h-[100px] border-b border-r p-1.5 ${
                      day ? "cursor-pointer hover:bg-muted/50 transition-colors" : "bg-muted/20"
                    }`}
                    onClick={() => day && openNewEvent(dateStr)}
                  >
                    {day && (
                      <>
                        <div className={`mb-1 text-xs font-medium ${
                          isToday(day)
                            ? "flex h-6 w-6 items-center justify-center rounded-full bg-primary text-primary-foreground"
                            : "text-muted-foreground"
                        }`}>
                          {day}
                        </div>
                        <div className="space-y-0.5">
                          {dayEvents.map((evt) => (
                            <div
                              key={evt.id}
                              className={`rounded-sm border px-1.5 py-0.5 text-xs truncate cursor-pointer ${EVENT_COLORS[evt.event_type]}`}
                              onClick={(e) => {
                                e.stopPropagation();
                                openEditEvent(evt);
                              }}
                            >
                              {evt.time && (
                                <span className="opacity-70 mr-1">{evt.time}</span>
                              )}
                              {evt.title}
                            </div>
                          ))}
                        </div>
                      </>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Add/Edit Event Dialog */}
      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>
              {editingEvent ? "Edit Event" : "New Event"}
            </DialogTitle>
            <DialogDescription>
              {selectedDate}
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <div>
              <Label htmlFor="title">Title</Label>
              <Input
                id="title"
                value={formTitle}
                onChange={(e) => setFormTitle(e.target.value)}
                placeholder="e.g. Film product review video"
              />
            </div>

            <div>
              <Label htmlFor="description">Description / Notes</Label>
              <textarea
                id="description"
                className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                value={formDescription}
                onChange={(e) => setFormDescription(e.target.value)}
                placeholder="Script ideas, notes, hashtags..."
              />
            </div>

            <div className="flex gap-4">
              <div className="flex-1">
                <Label htmlFor="time">Time (optional)</Label>
                <Input
                  id="time"
                  type="time"
                  value={formTime}
                  onChange={(e) => setFormTime(e.target.value)}
                />
              </div>
              <div className="flex-1">
                <Label htmlFor="event_type">Type</Label>
                <select
                  id="event_type"
                  className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  value={formType}
                  onChange={(e) => setFormType(e.target.value as "post" | "idea" | "note")}
                >
                  <option value="post">Scheduled Post</option>
                  <option value="idea">Content Idea</option>
                  <option value="note">Note</option>
                </select>
              </div>
            </div>
          </div>

          <DialogFooter>
            {editingEvent && (
              <Button
                variant="destructive"
                onClick={handleDelete}
                disabled={saving}
                className="mr-auto"
              >
                <Trash2 className="mr-1 h-4 w-4" />
                Delete
              </Button>
            )}
            <Button onClick={handleSave} disabled={saving || !formTitle.trim()}>
              {saving && <Loader2 className="mr-1 h-4 w-4 animate-spin" />}
              {editingEvent ? "Update" : "Create"}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}
