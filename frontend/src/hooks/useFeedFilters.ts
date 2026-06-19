/**
 * Hook for managing the news feed filter state.
 *
 * Maintains a single `FeedFilters` state object and provides helpers to
 * update individual dimensions (period, date range, categories, favorites,
 * pagination). Syncs the `categories` array with the authenticated user's
 * preferences automatically:
 *
 * - On login / preferences save → categories are set to the user's slugs.
 * - On logout → all filters reset to their defaults.
 * - On session restore → localStorage-cached preferences initialise the
 *   categories before any API call completes.
 *
 * @module useFeedFilters
 */

import { useState, useEffect } from 'react';
import { startOfDay, startOfWeek, startOfMonth } from 'date-fns';
import { useAuth } from '../contexts/AuthContext';

/** Named time-window shortcuts for the feed. */
export type Period = 'today' | 'week' | 'month' | 'custom';

/** Complete set of parameters used to query the news feed. */
export interface FeedFilters {
  period: Period;
  date_from: string;
  date_to: string;
  /** Active category slugs, e.g. `["technology", "ai"]`. Empty = no filter. */
  categories: string[];
  favoritesOnly: boolean;
  page: number;
  limit: number;
}

const toISO = (d: Date) => d.toISOString();

/**
 * Compute an absolute UTC date range for a named period.
 *
 * @param period - One of `'today'`, `'week'`, or `'month'`.
 * @returns Object with `date_from` and `date_to` as ISO 8601 strings.
 */
function getDateRange(period: Exclude<Period, 'custom'>) {
  const now = new Date();
  switch (period) {
    case 'today':
      return { date_from: toISO(startOfDay(now)), date_to: toISO(now) };
    case 'week':
      return {
        date_from: toISO(startOfWeek(now, { weekStartsOn: 1 })),
        date_to: toISO(now),
      };
    case 'month':
      return { date_from: toISO(startOfMonth(now)), date_to: toISO(now) };
  }
}

const DEFAULT_LIMIT = 10;

/**
 * Manage the news feed filter state with preference-aware category sync.
 *
 * @returns An object containing the current `filters` and the following
 *   setter helpers:
 *   - `setPeriod` — switch to a named or custom period.
 *   - `setDateRange` — set an arbitrary ISO date range (sets period to `'custom'`).
 *   - `toggleCategory` — add or remove a single category slug.
 *   - `setPage` / `setLimit` — control pagination.
 *   - `setFavoritesOnly` — toggle the favorites-only view.
 *   - `resetCategories` — replace the categories array wholesale.
 */
export function useFeedFilters() {
  const { isAuthenticated, preferences } = useAuth();

  const getInitial = (): FeedFilters => ({
    period: 'today',
    ...getDateRange('today'),
    categories: [],
    favoritesOnly: false,
    page: 1,
    limit: DEFAULT_LIMIT,
  });

  const [filters, setFilters] = useState<FeedFilters>(getInitial);

  // Sync category filters with auth state:
  // - logout → reset to defaults
  // - login / preferences update / session restore → load from preferences
  useEffect(() => {
    if (!isAuthenticated) {
      setFilters(getInitial());
    } else {
      setFilters((prev) => ({ ...prev, categories: preferences, page: 1 }));
    }
  }, [isAuthenticated, preferences]); // eslint-disable-line react-hooks/exhaustive-deps

  /**
   * Switch to a named period or enable the custom-range state.
   *
   * For named periods (`today`, `week`, `month`) the `date_from`/`date_to`
   * values are recalculated immediately. For `'custom'` only the `period`
   * label is updated; call `setDateRange` to supply the actual bounds.
   *
   * @param period - The period to activate.
   */
  const setPeriod = (period: Period) => {
    if (period === 'custom') {
      setFilters((prev) => ({ ...prev, period, page: 1 }));
    } else {
      setFilters((prev) => ({
        ...prev,
        period,
        ...getDateRange(period),
        page: 1,
      }));
    }
  };

  /**
   * Set an explicit ISO date range and switch to the `'custom'` period.
   *
   * @param date_from - Inclusive lower bound (ISO 8601).
   * @param date_to - Inclusive upper bound (ISO 8601).
   */
  const setDateRange = (date_from: string, date_to: string) => {
    setFilters((prev) => ({
      ...prev,
      period: 'custom',
      date_from,
      date_to,
      page: 1,
    }));
  };

  /**
   * Add a category slug to the active filter, or remove it if already present.
   *
   * @param categoryId - Category slug to toggle (e.g. `"technology"`).
   */
  const toggleCategory = (categoryId: string) => {
    setFilters((prev) => ({
      ...prev,
      page: 1,
      categories: prev.categories.includes(categoryId)
        ? prev.categories.filter((id) => id !== categoryId)
        : [...prev.categories, categoryId],
    }));
  };

  /** @param page - 1-based page number to navigate to. */
  const setPage = (page: number) =>
    setFilters((prev) => ({ ...prev, page }));

  /** @param limit - Number of articles per page. */
  const setLimit = (limit: number) =>
    setFilters((prev) => ({ ...prev, limit, page: 1 }));

  /** @param favoritesOnly - When `true` only favorited articles are shown. */
  const setFavoritesOnly = (favoritesOnly: boolean) =>
    setFilters((prev) => ({ ...prev, favoritesOnly, page: 1 }));

  /**
   * Replace the active category filter with a new set of slugs.
   *
   * @param categoryIds - Array of category slugs to activate. Pass `[]` to
   *                      clear all category filters.
   */
  const resetCategories = (categoryIds: string[]) =>
    setFilters((prev) => ({ ...prev, categories: categoryIds, page: 1 }));

  return {
    filters,
    setPeriod,
    setDateRange,
    toggleCategory,
    setPage,
    setLimit,
    setFavoritesOnly,
    resetCategories,
  };
}
