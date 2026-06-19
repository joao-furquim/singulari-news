import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { FilterBar } from '../layout/FilterBar';
import type { FeedFilters } from '../../hooks/useFeedFilters';

// Mutable flag — controls authenticated state per test
let mockIsAuthenticated = true;

vi.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: mockIsAuthenticated }),
}));

const defaultFilters: FeedFilters = {
  period: 'today',
  date_from: '2026-06-18T00:00:00.000Z',
  date_to: '2026-06-18T14:00:00.000Z',
  categories: [],
  favoritesOnly: false,
  page: 1,
  limit: 10,
};

function renderFilterBar(overrides = {}) {
  const props = {
    filters: defaultFilters,
    onPeriodChange: vi.fn(),
    onCategoryToggle: vi.fn(),
    onClearCategories: vi.fn(),
    onFavoritesToggle: vi.fn(),
    onOpenDatePicker: vi.fn(),
    onAuthRequired: vi.fn(),
    ...overrides,
  };
  render(<FilterBar {...props} />);
  return props;
}

describe('FilterBar', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    mockIsAuthenticated = true;
  });

  it('renders all 4 period chips', () => {
    renderFilterBar();
    expect(screen.getByText('Today')).toBeInTheDocument();
    expect(screen.getByText('This Week')).toBeInTheDocument();
    expect(screen.getByText('This Month')).toBeInTheDocument();
    expect(screen.getByText('Custom Range')).toBeInTheDocument();
  });

  it('renders the 8 fixed category chips', () => {
    renderFilterBar();
    ['Technology', 'AI', 'Business', 'Science', 'Health', 'Politics', 'Sports', 'General'].forEach(
      (cat) => expect(screen.getByText(cat)).toBeInTheDocument(),
    );
  });

  it('renders All chip and Favorites chip', () => {
    renderFilterBar();
    expect(screen.getByText('All')).toBeInTheDocument();
    expect(screen.getByText('Favorites')).toBeInTheDocument();
  });

  it('calls onCategoryToggle with the slug when a category chip is clicked', async () => {
    const onCategoryToggle = vi.fn();
    const user = userEvent.setup();
    renderFilterBar({ onCategoryToggle });
    await user.click(screen.getByText('Technology'));
    expect(onCategoryToggle).toHaveBeenCalledWith('technology');
  });

  it('calls onClearCategories when All chip is clicked', async () => {
    const onClearCategories = vi.fn();
    const user = userEvent.setup();
    renderFilterBar({ onClearCategories });
    await user.click(screen.getByText('All'));
    expect(onClearCategories).toHaveBeenCalledOnce();
  });

  it('calls onPeriodChange with correct period when period chip is clicked', async () => {
    const onPeriodChange = vi.fn();
    const user = userEvent.setup();
    renderFilterBar({ onPeriodChange });
    await user.click(screen.getByText('This Week'));
    expect(onPeriodChange).toHaveBeenCalledWith('week');
  });

  it('calls onOpenDatePicker when Custom Range chip is clicked', async () => {
    const onOpenDatePicker = vi.fn();
    const user = userEvent.setup();
    renderFilterBar({ onOpenDatePicker });
    await user.click(screen.getByText('Custom Range'));
    expect(onOpenDatePicker).toHaveBeenCalledOnce();
  });

  it('calls onFavoritesToggle when Favorites chip is clicked and user is authenticated', async () => {
    mockIsAuthenticated = true;
    const onFavoritesToggle = vi.fn();
    const user = userEvent.setup();
    renderFilterBar({ onFavoritesToggle });
    await user.click(screen.getByText('Favorites'));
    expect(onFavoritesToggle).toHaveBeenCalledOnce();
  });

  it('calls onAuthRequired instead of onFavoritesToggle when user is not authenticated', async () => {
    mockIsAuthenticated = false;
    const onFavoritesToggle = vi.fn();
    const onAuthRequired = vi.fn();
    const user = userEvent.setup();
    renderFilterBar({ onFavoritesToggle, onAuthRequired });
    await user.click(screen.getByText('Favorites'));
    expect(onFavoritesToggle).not.toHaveBeenCalled();
    expect(onAuthRequired).toHaveBeenCalledOnce();
  });
});
