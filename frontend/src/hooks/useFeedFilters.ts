import { useState, useEffect } from 'react';
import { startOfDay, startOfWeek, startOfMonth } from 'date-fns';
import { useAuth } from '../contexts/AuthContext';

export type Period = 'today' | 'week' | 'month' | 'custom';

export interface FeedFilters {
  period: Period;
  date_from: string;
  date_to: string;
  categories: string[];
  favoritesOnly: boolean;
  page: number;
  limit: number;
}

const toISO = (d: Date) => d.toISOString();

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

export function useFeedFilters() {
  const { isAuthenticated } = useAuth();

  const getInitial = (): FeedFilters => ({
    period: 'today',
    ...getDateRange('today'),
    categories: [],
    favoritesOnly: false,
    page: 1,
    limit: DEFAULT_LIMIT,
  });

  const [filters, setFilters] = useState<FeedFilters>(getInitial);

  // Reset all filters on logout
  useEffect(() => {
    if (!isAuthenticated) {
      setFilters(getInitial());
    }
  }, [isAuthenticated]); // eslint-disable-line react-hooks/exhaustive-deps

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

  const setDateRange = (date_from: string, date_to: string) => {
    setFilters((prev) => ({
      ...prev,
      period: 'custom',
      date_from,
      date_to,
      page: 1,
    }));
  };

  const toggleCategory = (categoryId: string) => {
    setFilters((prev) => ({
      ...prev,
      page: 1,
      categories: prev.categories.includes(categoryId)
        ? prev.categories.filter((id) => id !== categoryId)
        : [...prev.categories, categoryId],
    }));
  };

  const setPage = (page: number) =>
    setFilters((prev) => ({ ...prev, page }));

  const setLimit = (limit: number) =>
    setFilters((prev) => ({ ...prev, limit, page: 1 }));

  const setFavoritesOnly = (favoritesOnly: boolean) =>
    setFilters((prev) => ({ ...prev, favoritesOnly, page: 1 }));

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
