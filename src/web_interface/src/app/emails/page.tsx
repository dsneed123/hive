"use client";

import { useState } from "react";
import {
  Mail,
  RefreshCw,
  Loader2,
  Send,
  Sparkles,
  AlertTriangle,
  ChevronLeft,
  Inbox,
  Handshake,
  Tag,
  ShieldAlert,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Separator } from "@/components/ui/separator";
import { useEmails } from "@/hooks/use-emails";
import { cn } from "@/lib/utils";

const categories = [
  { value: "", label: "All", icon: Inbox },
  { value: "collaboration", label: "Collaborations", icon: Handshake },
  { value: "promotion", label: "Promotions", icon: Tag },
  { value: "spam", label: "Spam", icon: ShieldAlert },
];

const categoryColors: Record<string, string> = {
  collaboration: "bg-blue-500/15 text-blue-600 dark:text-blue-400",
  promotion: "bg-amber-500/15 text-amber-600 dark:text-amber-400",
  spam: "bg-red-500/15 text-red-600 dark:text-red-400",
  other: "bg-gray-500/15 text-gray-600 dark:text-gray-400",
};

export default function EmailsPage() {
  const {
    emails,
    loading,
    fetching,
    error,
    category,
    setCategory,
    mode,
    toggleMode,
    selectedEmail,
    setSelectedEmail,
    drafting,
    sending,
    fetchFromGmail,
    selectEmail,
    generateDraft,
    sendReply,
  } = useEmails();

  const [draftInstructions, setDraftInstructions] = useState("");
  const [fetchMessage, setFetchMessage] = useState<string | null>(null);
  const [sendMessage, setSendMessage] = useState<string | null>(null);

  const handleFetch = async () => {
    setFetchMessage(null);
    try {
      const msg = await fetchFromGmail();
      setFetchMessage(msg);
      setTimeout(() => setFetchMessage(null), 3000);
    } catch {
      // error handled by hook
    }
  };

  const handleGenerateDraft = async () => {
    if (!selectedEmail) return;
    try {
      await generateDraft(selectedEmail.id, draftInstructions);
      setDraftInstructions("");
    } catch {
      // error handled by hook
    }
  };

  const handleSend = async () => {
    if (!selectedEmail) return;
    setSendMessage(null);
    try {
      const msg = await sendReply(selectedEmail.id);
      setSendMessage(msg);
      setTimeout(() => setSendMessage(null), 3000);
    } catch {
      // error handled by hook
    }
  };

  // Email detail view
  if (selectedEmail) {
    return (
      <div className="mx-auto max-w-4xl space-y-4">
        <div className="flex items-center gap-2">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => setSelectedEmail(null)}
          >
            <ChevronLeft className="h-4 w-4" />
          </Button>
          <h1 className="text-xl font-bold">Email Detail</h1>
        </div>

        <Card>
          <CardHeader className="space-y-2">
            <div className="flex items-start justify-between gap-4">
              <div className="min-w-0 flex-1">
                <CardTitle className="text-lg">
                  {selectedEmail.subject || "(No subject)"}
                </CardTitle>
                <p className="mt-1 text-sm text-muted-foreground">
                  From: {selectedEmail.sender}
                </p>
                <p className="text-xs text-muted-foreground">
                  {selectedEmail.received_at
                    ? new Date(selectedEmail.received_at).toLocaleString()
                    : ""}
                </p>
              </div>
              <span
                className={cn(
                  "shrink-0 rounded-full px-2.5 py-0.5 text-xs font-medium",
                  categoryColors[selectedEmail.category] || categoryColors.other
                )}
              >
                {selectedEmail.category}
              </span>
            </div>
          </CardHeader>
          <Separator />
          <CardContent className="pt-4">
            <pre className="whitespace-pre-wrap text-sm leading-relaxed">
              {selectedEmail.body_preview}
            </pre>
          </CardContent>
        </Card>

        {/* AI Draft Section */}
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center gap-2 text-base">
              <Sparkles className="h-4 w-4" />
              AI Draft Reply
            </CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            {selectedEmail.ai_draft && (
              <div className="rounded-lg border bg-muted/50 p-4">
                {mode === "test" && (
                  <p className="mb-2 text-xs font-medium text-amber-600 dark:text-amber-400">
                    [TEST MODE - Draft will not be sent]
                  </p>
                )}
                <pre className="whitespace-pre-wrap text-sm leading-relaxed">
                  {selectedEmail.ai_draft}
                </pre>
              </div>
            )}

            <div className="flex gap-2">
              <Input
                placeholder="Optional instructions for the AI draft..."
                value={draftInstructions}
                onChange={(e) => setDraftInstructions(e.target.value)}
                className="flex-1"
              />
              <Button onClick={handleGenerateDraft} disabled={drafting}>
                {drafting ? (
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                ) : (
                  <Sparkles className="mr-2 h-4 w-4" />
                )}
                Generate Reply
              </Button>
            </div>

            {selectedEmail.ai_draft && (
              <div className="flex items-center gap-2">
                <Button
                  onClick={handleSend}
                  disabled={sending || mode !== "reply"}
                  variant={mode === "reply" ? "default" : "secondary"}
                >
                  {sending ? (
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  ) : (
                    <Send className="mr-2 h-4 w-4" />
                  )}
                  Send Reply
                </Button>
                {mode === "test" && (
                  <p className="text-xs text-muted-foreground">
                    Sending disabled in test mode
                  </p>
                )}
              </div>
            )}

            {sendMessage && (
              <div className="rounded-lg border border-emerald-500/50 bg-emerald-500/10 p-3 text-sm text-emerald-600 dark:text-emerald-400">
                {sendMessage}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    );
  }

  // Email list view
  return (
    <div className="mx-auto max-w-4xl space-y-4">
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Emails</h1>
          <p className="text-muted-foreground">
            Manage incoming emails with AI-powered replies
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleFetch}
            disabled={fetching}
          >
            {fetching ? (
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="mr-2 h-4 w-4" />
            )}
            Fetch Emails
          </Button>
        </div>
      </div>

      {/* Mode Toggle */}
      <div
        className={cn(
          "flex items-center justify-between rounded-lg border p-3",
          mode === "reply"
            ? "border-amber-500/50 bg-amber-500/10"
            : "border-border bg-muted/30"
        )}
      >
        <div className="flex items-center gap-2">
          {mode === "reply" && (
            <AlertTriangle className="h-4 w-4 text-amber-600 dark:text-amber-400" />
          )}
          <span className="text-sm font-medium">
            {mode === "test"
              ? "Test Mode — AI drafts only, no sending"
              : "Reply Mode — AI can send emails"}
          </span>
        </div>
        <Button variant="outline" size="sm" onClick={toggleMode}>
          Switch to {mode === "test" ? "Reply" : "Test"} Mode
        </Button>
      </div>

      {fetchMessage && (
        <div className="rounded-lg border border-emerald-500/50 bg-emerald-500/10 p-3 text-sm text-emerald-600 dark:text-emerald-400">
          {fetchMessage}
        </div>
      )}

      {error && (
        <div className="rounded-lg border border-red-500/50 bg-red-500/10 p-3 text-sm text-red-600 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Category Tabs */}
      <div className="flex gap-1 rounded-lg border bg-muted/30 p-1">
        {categories.map((cat) => (
          <button
            key={cat.value}
            onClick={() => setCategory(cat.value)}
            className={cn(
              "flex items-center gap-1.5 rounded-md px-3 py-1.5 text-sm font-medium transition-colors",
              category === cat.value
                ? "bg-background text-foreground shadow-sm"
                : "text-muted-foreground hover:text-foreground"
            )}
          >
            <cat.icon className="h-3.5 w-3.5" />
            {cat.label}
          </button>
        ))}
      </div>

      {/* Email List */}
      {loading ? (
        <div className="flex h-48 items-center justify-center">
          <Loader2 className="h-8 w-8 animate-spin text-primary" />
        </div>
      ) : emails.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12 text-center">
            <Mail className="mb-3 h-10 w-10 text-muted-foreground" />
            <p className="font-medium">No emails found</p>
            <p className="mt-1 text-sm text-muted-foreground">
              Click &quot;Fetch Emails&quot; to pull from Gmail
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-2">
          {emails.map((email) => (
            <button
              key={email.id}
              onClick={() => selectEmail(email.id)}
              className="w-full rounded-lg border bg-card p-4 text-left transition-colors hover:bg-accent"
            >
              <div className="flex items-start gap-3">
                <Mail className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground" />
                <div className="min-w-0 flex-1">
                  <div className="flex items-center gap-2">
                    <p className="truncate text-sm font-medium">
                      {email.subject || "(No subject)"}
                    </p>
                    <span
                      className={cn(
                        "shrink-0 rounded-full px-2 py-0.5 text-xs font-medium",
                        categoryColors[email.category] || categoryColors.other
                      )}
                    >
                      {email.category}
                    </span>
                  </div>
                  <p className="truncate text-xs text-muted-foreground">
                    {email.sender}
                  </p>
                  <p className="mt-1 line-clamp-2 text-xs text-muted-foreground">
                    {email.body_preview}
                  </p>
                </div>
                <span className="shrink-0 text-xs text-muted-foreground">
                  {email.received_at
                    ? new Date(email.received_at).toLocaleDateString()
                    : ""}
                </span>
              </div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
