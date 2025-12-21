/**
 * Example React hooks and usage patterns for FloorEye API services.
 * 
 * Copy and adapt these patterns for your components.
 */

import { useState, useEffect, useCallback } from "react";
import { fetchHistory, type HistoryItem } from "./history.service";
import { 
  listRecipients, 
  createRecipient, 
  toggleRecipient, 
  deleteRecipient, 
  type EmailRecipient 
} from "./emailRecipients.service";
import axios from "axios";

// ============================================================================
// HISTORY HOOK EXAMPLE
// ============================================================================

interface UseHistoryResult {
  history: HistoryItem[];
  loading: boolean;
  error: string | null;
  loadMore: () => void;
  refresh: () => void;
}

/**
 * Example hook for fetching detection history with pagination.
 */
export function useHistory(pageSize = 20): UseHistoryResult {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);

  const loadHistory = useCallback(async (reset = false) => {
    setLoading(true);
    setError(null);

    try {
      const currentOffset = reset ? 0 : offset;
      const data = await fetchHistory({ limit: pageSize, offset: currentOffset });
      
      if (reset) {
        setHistory(data);
        setOffset(pageSize);
      } else {
        setHistory((prev) => [...prev, ...data]);
        setOffset((prev) => prev + pageSize);
      }
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message 
        : "Failed to load history";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [offset, pageSize]);

  // Initial load
  useEffect(() => {
    loadHistory(true);
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const refresh = useCallback(() => {
    loadHistory(true);
  }, [loadHistory]);

  const loadMore = useCallback(() => {
    loadHistory(false);
  }, [loadHistory]);

  return { history, loading, error, loadMore, refresh };
}

// ============================================================================
// EMAIL RECIPIENTS HOOK EXAMPLE
// ============================================================================

interface UseEmailRecipientsResult {
  recipients: EmailRecipient[];
  loading: boolean;
  error: string | null;
  addRecipient: (email: string) => Promise<void>;
  toggleActive: (id: number, active: boolean) => Promise<void>;
  removeRecipient: (id: number) => Promise<void>;
  refresh: () => void;
}

/**
 * Example hook for managing email recipients.
 */
export function useEmailRecipients(): UseEmailRecipientsResult {
  const [recipients, setRecipients] = useState<EmailRecipient[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Fetch recipients
  const fetchRecipients = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const data = await listRecipients();
      setRecipients(data);
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message 
        : "Failed to load recipients";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchRecipients();
  }, [fetchRecipients]);

  // Add new recipient
  const addRecipient = useCallback(async (email: string) => {
    try {
      await createRecipient({ email, active: true });
      await fetchRecipients(); // Refresh list
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message 
        : "Failed to add recipient";
      throw new Error(message);
    }
  }, [fetchRecipients]);

  // Toggle active status
  const toggleActive = useCallback(async (id: number, active: boolean) => {
    try {
      const updated = await toggleRecipient(id, active);
      setRecipients((prev) =>
        prev.map((r) => (r.id === id ? updated : r))
      );
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message 
        : "Failed to update recipient";
      throw new Error(message);
    }
  }, []);

  // Delete recipient
  const removeRecipient = useCallback(async (id: number) => {
    try {
      await deleteRecipient(id);
      setRecipients((prev) => prev.filter((r) => r.id !== id));
    } catch (err) {
      const message = axios.isAxiosError(err)
        ? err.response?.data?.detail || err.message 
        : "Failed to delete recipient";
      throw new Error(message);
    }
  }, []);

  return {
    recipients,
    loading,
    error,
    addRecipient,
    toggleActive,
    removeRecipient,
    refresh: fetchRecipients,
  };
}

// ============================================================================
// SIMPLE USAGE EXAMPLE (Copy to your component)
// ============================================================================

/*
import { useEffect, useState } from "react";
import { fetchHistory, HistoryItem } from "./services/history.service";

function HistoryPage() {
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;

    async function load() {
      try {
        const data = await fetchHistory({ limit: 50, offset: 0 });
        if (!cancelled) {
          setHistory(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : "Failed to load");
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    load();

    return () => {
      cancelled = true;
    };
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {history.map((item) => (
        <li key={item.id}>
          {item.source} - {item.is_dirty ? "Dirty" : "Clean"} - {item.created_at}
        </li>
      ))}
    </ul>
  );
}
*/
