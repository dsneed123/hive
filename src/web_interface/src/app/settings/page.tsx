"use client";

import { useEffect, useState } from "react";
import {
  Save,
  Eye,
  EyeOff,
  Loader2,
  Check,
  Plus,
  Trash2,
  User,
} from "lucide-react";
import {
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  CardDescription,
} from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Separator } from "@/components/ui/separator";
import { getSettings, updateSettings } from "@/lib/api";
import { useAccounts } from "@/hooks/use-accounts";

export default function SettingsPage() {
  // Settings state
  const [claudeKey, setClaudeKey] = useState("");
  const [gmailAddress, setGmailAddress] = useState("");
  const [gmailAppPassword, setGmailAppPassword] = useState("");
  const [showKey, setShowKey] = useState(false);
  const [showGmailPass, setShowGmailPass] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [feedback, setFeedback] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  // Account management
  const {
    accounts,
    loading: accountsLoading,
    error: accountsError,
    add: addAccount,
    remove: removeAccount,
    refresh: refreshAccounts,
  } = useAccounts();
  const [newUsername, setNewUsername] = useState("");
  const [newUrl, setNewUrl] = useState("");
  const [addingAccount, setAddingAccount] = useState(false);

  useEffect(() => {
    getSettings()
      .then((s) => {
        setClaudeKey(s.claude_key);
        setGmailAddress(s.gmail_address);
        setGmailAppPassword(s.gmail_app_password);
      })
      .catch((e) =>
        setError(e instanceof Error ? e.message : "Failed to load settings")
      )
      .finally(() => setLoading(false));
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setFeedback(null);
    setError(null);
    try {
      const result = await updateSettings({
        claude_key: claudeKey,
        gmail_address: gmailAddress,
        gmail_app_password: gmailAppPassword,
      });
      setFeedback(result.message || "Settings saved");
      setTimeout(() => setFeedback(null), 3000);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to save settings");
    } finally {
      setSaving(false);
    }
  };

  const handleAddAccount = async () => {
    if (!newUsername.trim() || !newUrl.trim()) return;
    setAddingAccount(true);
    try {
      await addAccount(newUsername.trim(), newUrl.trim());
      setNewUsername("");
      setNewUrl("");
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to add account");
    } finally {
      setAddingAccount(false);
    }
  };

  const handleRemoveAccount = async (id: number) => {
    try {
      await removeAccount(id);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to remove account");
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-2xl space-y-6">
      <div>
        <h1 className="text-2xl font-bold">Settings</h1>
        <p className="text-muted-foreground">
          Manage your accounts, API keys, and email integration
        </p>
      </div>

      {/* TikTok Accounts Management */}
      <Card>
        <CardHeader>
          <CardTitle>TikTok Accounts</CardTitle>
          <CardDescription>
            Manage your TikTok accounts. The active account is used for analytics and chat context.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* Existing accounts list */}
          {accounts.length > 0 && (
            <div className="space-y-2">
              {accounts.map((account) => (
                <div
                  key={account.id}
                  className="flex items-center gap-3 rounded-lg border p-3"
                >
                  <User className="h-4 w-4 text-muted-foreground" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium">@{account.username}</p>
                    <p className="truncate text-xs text-muted-foreground">
                      {account.tiktok_url}
                    </p>
                  </div>
                  {account.is_active && (
                    <span className="rounded-full bg-primary/15 px-2 py-0.5 text-xs font-medium text-primary">
                      Active
                    </span>
                  )}
                  <Button
                    type="button"
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8 text-muted-foreground hover:text-red-500"
                    onClick={() => handleRemoveAccount(account.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </div>
              ))}
            </div>
          )}

          {/* Add new account form */}
          <Separator />
          <p className="text-sm font-medium">Add Account</p>
          <div className="flex gap-2">
            <Input
              placeholder="username"
              value={newUsername}
              onChange={(e) => setNewUsername(e.target.value)}
              className="flex-1"
            />
            <Input
              placeholder="https://www.tiktok.com/@username"
              value={newUrl}
              onChange={(e) => setNewUrl(e.target.value)}
              className="flex-[2]"
            />
            <Button
              type="button"
              size="icon"
              disabled={addingAccount || !newUsername.trim() || !newUrl.trim()}
              onClick={handleAddAccount}
            >
              {addingAccount ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* API Keys + Gmail Settings */}
      <form onSubmit={handleSave}>
        <Card>
          <CardHeader>
            <CardTitle>API Keys</CardTitle>
            <CardDescription>
              Required for AI chat functionality
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="claude-key">Claude API Key</Label>
              <div className="relative">
                <Input
                  id="claude-key"
                  type={showKey ? "text" : "password"}
                  placeholder="sk-ant-..."
                  value={claudeKey}
                  onChange={(e) => setClaudeKey(e.target.value)}
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-10 w-10"
                  onClick={() => setShowKey(!showKey)}
                >
                  {showKey ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </CardContent>

          <Separator />

          <CardHeader>
            <CardTitle>Gmail Integration</CardTitle>
            <CardDescription>
              Connect your Gmail for email management. Use an App Password (not
              your regular password).
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="gmail-address">Gmail Address</Label>
              <Input
                id="gmail-address"
                type="email"
                placeholder="you@gmail.com"
                value={gmailAddress}
                onChange={(e) => setGmailAddress(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="gmail-password">App Password</Label>
              <div className="relative">
                <Input
                  id="gmail-password"
                  type={showGmailPass ? "text" : "password"}
                  placeholder="xxxx xxxx xxxx xxxx"
                  value={gmailAppPassword}
                  onChange={(e) => setGmailAppPassword(e.target.value)}
                  className="pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="icon"
                  className="absolute right-0 top-0 h-10 w-10"
                  onClick={() => setShowGmailPass(!showGmailPass)}
                >
                  {showGmailPass ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
            </div>
          </CardContent>

          <Separator />

          <CardContent className="pt-6">
            {(error || accountsError) && (
              <div className="mb-4 rounded-lg border border-red-500/50 bg-red-500/10 p-3 text-sm text-red-600 dark:text-red-400">
                {error || accountsError}
              </div>
            )}
            {feedback && (
              <div className="mb-4 flex items-center gap-2 rounded-lg border border-emerald-500/50 bg-emerald-500/10 p-3 text-sm text-emerald-600 dark:text-emerald-400">
                <Check className="h-4 w-4" />
                {feedback}
              </div>
            )}
            <Button type="submit" disabled={saving} className="w-full sm:w-auto">
              {saving ? (
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              ) : (
                <Save className="mr-2 h-4 w-4" />
              )}
              Save Settings
            </Button>
          </CardContent>
        </Card>
      </form>
    </div>
  );
}
