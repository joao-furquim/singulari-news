import { useState, useEffect, useRef } from 'react';
import client from '../api/client';
import { NewsItem, PaginatedResponse } from '../types';
import { FeedFilters } from './useFeedFilters';

const POLLING_INTERVAL = import.meta.env.DEV ? 10_000 : 30_000;

function normalizeResponse(
  raw: PaginatedResponse<NewsItem> | NewsItem[],
): PaginatedResponse<NewsItem> {
  if (Array.isArray(raw)) {
    return { items: raw, total: raw.length, page: 1, limit: raw.length, pages: 1 };
  }
  return raw;
}

export function useNewsPolling(filters: FeedFilters) {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [newArticlesCount, setNewArticlesCount] = useState(0);

  const endpoint = filters.favoritesOnly ? '/users/me/favorites' : '/news';

  // Tracks the latest article ID on page 1 — never depends on which page is viewed
  const firstNewsIdRef = useRef<string | null>(null);

  // Builds query params; optionally override page and limit
  const buildParams = (overridePage?: number, overrideLimit?: number) => {
    const params: Record<string, string | number> = {
      page: overridePage ?? filters.page,
      limit: overrideLimit ?? filters.limit,
    };
    if (filters.date_from) params.date_from = filters.date_from;
    if (filters.date_to) params.date_to = filters.date_to;
    if (filters.categories.length > 0)
      params.categories = filters.categories.join(',');
    return params;
  };

  // Loads the currently-paginated view
  const loadNews = async () => {
    setLoading(true);
    try {
      const params = buildParams();
      console.log('[feed] fetch', { endpoint, params });
      const response = await client.get<PaginatedResponse<NewsItem> | NewsItem[]>(
        endpoint,
        { params },
      );
      console.log('[feed] response', response.data);
      const data = normalizeResponse(response.data);
      setNews(data.items);
      setTotal(data.total);
      setPages(data.pages);

      // When loading page 1, use it as the polling baseline if not yet set
      if (filters.page === 1 && firstNewsIdRef.current === null) {
        firstNewsIdRef.current = data.items[0]?.id ?? null;
        console.log('[polling] initialized with id:', firstNewsIdRef.current);
      }
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  };

  // Polling check — ALWAYS fetches page=1, limit=1 regardless of which page is viewed.
  // This is the only correct way to detect new arrivals since they always appear at the top.
  const checkForNewArticles = async () => {
    if (filters.favoritesOnly) return; // favorites don't need polling
    console.log('[polling] checking...');
    try {
      const response = await client.get<PaginatedResponse<NewsItem>>(
        '/news',
        { params: buildParams(1, 1) },
      );
      const data = normalizeResponse(response.data);
      const latestId = data.items[0]?.id;

      if (!latestId) return;

      if (firstNewsIdRef.current === null) {
        // First execution after a filter reset — just store the baseline
        firstNewsIdRef.current = latestId;
        console.log('[polling] initialized with id:', latestId);
        return;
      }

      if (latestId !== firstNewsIdRef.current) {
        setNewArticlesCount((prev) => prev + 1);
        console.log('[polling] new articles detected!');
      } else {
        console.log('[polling] no changes');
      }
    } catch (error) {
      console.error('[polling] error:', error);
    }
  };

  // Called when the user clicks the notification banner.
  // Fetches page 1 with the current filters, updates the display, and resets the counter.
  const refreshNews = async () => {
    try {
      const params = buildParams(1); // page 1, current limit
      const response = await client.get<PaginatedResponse<NewsItem> | NewsItem[]>(
        endpoint,
        { params },
      );
      const data = normalizeResponse(response.data);
      setNews(data.items);
      setTotal(data.total);
      setPages(data.pages);
      firstNewsIdRef.current = data.items[0]?.id ?? null;
      setNewArticlesCount(0);
      console.log('[polling] refreshed, new baseline:', firstNewsIdRef.current);
    } catch {
      // ignore
    }
  };

  // Reset the polling baseline whenever the filter CONTEXT changes (period → date range,
  // categories, or favorites mode). A new article in "AI" should not trigger a notification
  // while the active filter is "Sports".
  useEffect(() => {
    firstNewsIdRef.current = null;
    setNewArticlesCount(0);
    console.log('[polling] filter context changed — resetting baseline');
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [endpoint, filters.date_from, filters.date_to, filters.categories.join(',')]);

  // Refetch the displayed list whenever any filter (including page/limit) changes
  useEffect(() => {
    void loadNews();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [
    endpoint,
    filters.page,
    filters.limit,
    filters.date_from,
    filters.date_to,
    filters.categories.join(','),
  ]);

  // Background polling — ref pattern ensures checkForNewArticles always sees latest filters
  const checkRef = useRef(checkForNewArticles);
  checkRef.current = checkForNewArticles;
  useEffect(() => {
    const id = setInterval(() => void checkRef.current(), POLLING_INTERVAL);
    return () => clearInterval(id);
  }, []);

  return { news, total, pages, loading, newArticlesCount, refreshNews };
}
