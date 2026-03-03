"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Email,
  getEmails,
  getEmail as getEmailById,
  fetchEmailsFromGmail,
  generateEmailDraft,
  sendEmailReply,
  getEmailMode,
  setEmailMode,
} from "@/lib/api";

export function useEmails() {
  const [emails, setEmails] = useState<Email[]>([]);
  const [loading, setLoading] = useState(true);
  const [fetching, setFetching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [category, setCategory] = useState("");
  const [page, setPage] = useState(1);
  const [mode, setMode] = useState("test");
  const [selectedEmail, setSelectedEmail] = useState<Email | null>(null);
  const [drafting, setDrafting] = useState(false);
  const [sending, setSending] = useState(false);

  const loadEmails = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getEmails(category, page);
      setEmails(data.emails);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load emails");
    } finally {
      setLoading(false);
    }
  }, [category, page]);

  const loadMode = useCallback(async () => {
    try {
      const m = await getEmailMode();
      setMode(m);
    } catch {
      // ignore
    }
  }, []);

  useEffect(() => {
    loadEmails();
  }, [loadEmails]);

  useEffect(() => {
    loadMode();
  }, [loadMode]);

  const fetchFromGmail = async () => {
    setFetching(true);
    setError(null);
    try {
      const result = await fetchEmailsFromGmail();
      await loadEmails();
      return result.message;
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Failed to fetch emails";
      setError(msg);
      throw e;
    } finally {
      setFetching(false);
    }
  };

  const selectEmail = async (id: number) => {
    try {
      const email = await getEmailById(id);
      setSelectedEmail(email);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load email");
    }
  };

  const generateDraft = async (id: number, instructions: string = "") => {
    setDrafting(true);
    try {
      const updated = await generateEmailDraft(id, instructions);
      setSelectedEmail(updated);
      // Update in list too
      setEmails((prev) =>
        prev.map((e) => (e.id === id ? { ...e, ai_draft: updated.ai_draft } : e))
      );
      return updated;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to generate draft");
      throw e;
    } finally {
      setDrafting(false);
    }
  };

  const sendReply = async (id: number, body: string = "") => {
    setSending(true);
    try {
      const result = await sendEmailReply(id, body);
      return result.message;
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to send reply");
      throw e;
    } finally {
      setSending(false);
    }
  };

  const toggleMode = async () => {
    const newMode = mode === "test" ? "reply" : "test";
    try {
      const m = await setEmailMode(newMode);
      setMode(m);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to change mode");
    }
  };

  return {
    emails,
    loading,
    fetching,
    error,
    category,
    setCategory,
    page,
    setPage,
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
    refresh: loadEmails,
  };
}
