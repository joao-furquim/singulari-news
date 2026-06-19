import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { startOfDay, startOfWeek, startOfMonth } from 'date-fns';

// Stable reference — a new [] on every call would make the useEffect
// dependency change every render, causing an infinite loop.
const STABLE_PREFERENCES: string[] = [];

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: false, preferences: STABLE_PREFERENCES }),
}));

import { useFeedFilters } from '../useFeedFilters';

const FIXED_NOW = new Date('2026-06-18T14:00:00.000Z');

describe('useFeedFilters', () => {
  beforeEach(() => {
    vi.useFakeTimers({ toFake: ['Date'] });
    vi.setSystemTime(FIXED_NOW);
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('initializes with default period today', () => {
    const { result } = renderHook(() => useFeedFilters());
    expect(result.current.filters.period).toBe('today');
    expect(result.current.filters.categories).toEqual([]);
    expect(result.current.filters.favoritesOnly).toBe(false);
    expect(result.current.filters.page).toBe(1);
  });

  it('sets date_from to start of today on init', () => {
    const { result } = renderHook(() => useFeedFilters());
    const expected = startOfDay(FIXED_NOW).toISOString();
    expect(result.current.filters.date_from).toBe(expected);
  });

  it('toggles category — adds when not selected', () => {
    const { result } = renderHook(() => useFeedFilters());
    act(() => result.current.toggleCategory('technology'));
    expect(result.current.filters.categories).toContain('technology');
  });

  it('toggles category — removes when already selected', () => {
    const { result } = renderHook(() => useFeedFilters());
    act(() => result.current.toggleCategory('technology'));
    act(() => result.current.toggleCategory('technology'));
    expect(result.current.filters.categories).not.toContain('technology');
  });

  it('accumulates multiple category selections', () => {
    const { result } = renderHook(() => useFeedFilters());
    act(() => result.current.toggleCategory('technology'));
    act(() => result.current.toggleCategory('ai'));
    expect(result.current.filters.categories).toEqual(['technology', 'ai']);
  });

  it('clears all categories with resetCategories([])', () => {
    const { result } = renderHook(() => useFeedFilters());
    act(() => result.current.toggleCategory('technology'));
    act(() => result.current.toggleCategory('ai'));
    act(() => result.current.resetCategories([]));
    expect(result.current.filters.categories).toEqual([]);
  });

  it('resets to page 1 when period changes', () => {
    const { result } = renderHook(() => useFeedFilters());
    act(() => result.current.setPage(3));
    expect(result.current.filters.page).toBe(3);
    act(() => result.current.setPeriod('week'));
    expect(result.current.filters.page).toBe(1);
  });

  it('resets to page 1 when category is toggled', () => {
    const { result } = renderHook(() => useFeedFilters());
    act(() => result.current.setPage(5));
    act(() => result.current.toggleCategory('ai'));
    expect(result.current.filters.page).toBe(1);
  });

  it('sets correct date_from for week period', () => {
    const { result } = renderHook(() => useFeedFilters());
    act(() => result.current.setPeriod('week'));
    const expected = startOfWeek(FIXED_NOW, { weekStartsOn: 1 }).toISOString();
    expect(result.current.filters.date_from).toBe(expected);
    expect(result.current.filters.period).toBe('week');
  });

  it('sets correct date_from for month period', () => {
    const { result } = renderHook(() => useFeedFilters());
    act(() => result.current.setPeriod('month'));
    const expected = startOfMonth(FIXED_NOW).toISOString();
    expect(result.current.filters.date_from).toBe(expected);
  });

  it('stores custom date range without changing period to non-custom', () => {
    const { result } = renderHook(() => useFeedFilters());
    const from = '2026-06-01T00:00:00.000Z';
    const to = '2026-06-15T23:59:59.000Z';
    act(() => result.current.setDateRange(from, to));
    expect(result.current.filters.period).toBe('custom');
    expect(result.current.filters.date_from).toBe(from);
    expect(result.current.filters.date_to).toBe(to);
  });
});
