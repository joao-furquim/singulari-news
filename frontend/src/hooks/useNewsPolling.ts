/**
 * Hook for fetching and polling the news feed.
 *
 * Manages three distinct concerns:
 *
 * 1. **Feed fetching** — re-fetches the current page whenever any filter
 *    changes (period, categories, page, limit, favorites mode).
 * 2. **New-article detection** — polls page 1 on a background interval,
 *    comparing the latest article ID to a stored baseline. When the ID
 *    changes `newArticlesCount` is incremented so the UI can surface a
 *    "N new articles" banner.
 * 3. **Manual refresh** — `refreshNews` fetches page 1, updates the
 *    displayed list, resets the counter, and resets the polling baseline.
 *
 * The polling baseline is reset whenever the filter *context* changes
 * (date range, categories, or favorites mode) so notifications remain
 * scoped to the current view.
 *
 * @module useNewsPolling
 */

import { useState, useEffect, useRef } from 'react';
import client from '../api/client';
import { NewsItem, PaginatedResponse } from '../types';
import { FeedFilters } from './useFeedFilters';

/** Polling interval in milliseconds. Shorter in development for faster feedback. */
const POLLING_INTERVAL = import.meta.env.DEV ? 10_000 : 30_000;

/**
 * Normalise a news API response that may be either paginated or a plain array.
 *
 * Some endpoints return a `PaginatedResponse`; others return a raw array.
 * This function coerces both shapes into a `PaginatedResponse` so callers
 * can always destructure `items`, `total`, and `pages`.
 *
 * @param raw - The raw API response body.
 * @returns A normalised `PaginatedResponse<NewsItem>`.
 */
function normalizeResponse(
  raw: PaginatedResponse<NewsItem> | NewsItem[],
): PaginatedResponse<NewsItem> {
  if (Array.isArray(raw)) {
    return { items: raw, total: raw.length, page: 1, limit: raw.length, pages: 1 };
  }
  return raw;
}

/**
 * Fetch and poll the news feed based on the given filter state.
 *
 * @param filters - Current feed filter and pagination parameters.
 * @returns An object containing:
 *   - `news` — articles for the current page.
 *   - `total` — total matching article count.
 *   - `pages` — total page count.
 *   - `loading` — `true` while a page fetch is in progress.
 *   - `newArticlesCount` — number of new articles detected since the last
 *     baseline reset.
 *   - `refreshNews` — imperative callback to refresh page 1 and reset the
 *     new-articles counter.
 */
export function useNewsPolling(filters: FeedFilters) {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);
  const [loading, setLoading] = useState(false);
  const [newArticlesCount, setNewArticlesCount] = useState(0);

  const endpoint = filters.favoritesOnly ? '/users/me/favorites' : '/news';

  // Tracks the latest article ID on page 1 — never depends on which page is viewed
  const firstNewsIdRef = useRef<string | null>(null);

  /**
   * Build query parameters for the news endpoint.
   *
   * @param overridePage - Override the page number (e.g. force page 1 for polling).
   * @param overrideLimit - Override the limit (e.g. 1 for lightweight polling checks).
   */
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

  /** Fetch the currently configured page and update the displayed list. */
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

  /**
   * Lightweight polling check — fetches only the first article (page=1, limit=1).
   *
   * Compares the latest article ID to the stored baseline. On a mismatch,
   * increments `newArticlesCount` so the UI can prompt the user to refresh.
   * Always operates on page 1 regardless of the page the user is currently
   * viewing, since new articles always appear at the top.
   */
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

  /**
   * Fetch page 1, update the displayed list, and reset the new-articles counter.
   *
   * Intended to be called when the user clicks the "N new articles" banner.
   */
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
