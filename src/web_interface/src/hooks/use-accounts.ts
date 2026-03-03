"use client";

import { useState, useEffect, useCallback } from "react";
import {
  Account,
  getAccounts,
  createAccount,
  activateAccount,
  deleteAccount,
} from "@/lib/api";

export function useAccounts() {
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getAccounts();
      setAccounts(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load accounts");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const active = accounts.find((a) => a.is_active) || null;

  const add = async (username: string, tiktok_url: string) => {
    const account = await createAccount(username, tiktok_url);
    await refresh();
    return account;
  };

  const switchTo = async (id: number) => {
    await activateAccount(id);
    await refresh();
  };

  const remove = async (id: number) => {
    await deleteAccount(id);
    await refresh();
  };

  return { accounts, active, loading, error, add, switchTo, remove, refresh };
}
