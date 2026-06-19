import { describe, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

vi.mock('@mui/material', () => ({
  Box: ({ children }: any) => <div>{children}</div>,
  Typography: ({ children }: any) => <span>{children}</span>,
  Chip: ({ label, onClick }: any) => <button onClick={onClick}>{label}</button>,
  IconButton: ({ children, onClick, 'aria-label': ariaLabel }: any) => <button onClick={onClick} aria-label={ariaLabel}>{children}</button>,
  Card: ({ children, sx, ...rest }: any) => <div {...rest}>{children}</div>,
  CardActionArea: ({ children, onClick }: any) => <div onClick={onClick}>{children}</div>,
  CardContent: ({ children }: any) => <div>{children}</div>,
  Avatar: ({ children }: any) => <div>{children}</div>,
}));

vi.mock('@mui/icons-material', () => ({
  default: () => null,
  Computer: () => null,
  Psychology: () => null,
  BusinessCenter: () => null,
  Science: () => null,
  Lightbulb: () => null,
  Public: () => null,
  Article: () => null,
  Star: () => null,
  StarBorder: () => null,
  HealthAndSafety: () => null,
  RocketLaunch: () => null,
  EnergySavingsLeaf: () => null,
  AccountBalance: () => null,
  Sports: () => null,
  TheaterComedy: () => null,
  Work: () => null,
  Movie: () => null,
  Groups: () => null,
}));
import userEvent from '@testing-library/user-event';
import { NewsItem } from '../news/NewsItem';
import type { NewsItem as NewsItemType } from '../../types';

function makeNews(overrides: Partial<NewsItemType> = {}): NewsItemType {
  const now = new Date().toISOString();
  return {
    id: 'news-1',
    category_id: 'cat-1',
    title: 'Test Article Title',
    source: 'Test Source',
    summary: 'A short summary.',
    content: 'Full article content.',
    published_at: now,
    created_at: now,
    ai_generated: false,
    category: { id: 'cat-1', name: 'Technology', slug: 'technology', icon: '💻', description: null },
    ...overrides,
  };
}

const defaultProps = {
  isFavorited: false,
  onSelect: vi.fn(),
  onToggleFavorite: vi.fn(),
};

describe('NewsItem', () => {
  it('renders title and source correctly', () => {
    render(<NewsItem news={makeNews()} {...defaultProps} />);
    expect(screen.getByText('Test Article Title')).toBeInTheDocument();
    expect(screen.getByText(/Test Source/)).toBeInTheDocument();
  });

  it('shows AI badge when ai_generated is true', () => {
    render(<NewsItem news={makeNews({ ai_generated: true })} {...defaultProps} />);
    expect(screen.getByText('✦ AI')).toBeInTheDocument();
  });

  it('hides AI badge when ai_generated is false', () => {
    render(<NewsItem news={makeNews({ ai_generated: false })} {...defaultProps} />);
    expect(screen.queryByText('✦ AI')).not.toBeInTheDocument();
  });

  it('shows "new" badge for articles published less than 2 hours ago', () => {
    const recentDate = new Date(Date.now() - 30 * 60 * 1000).toISOString(); // 30 min ago
    render(<NewsItem news={makeNews({ published_at: recentDate })} {...defaultProps} />);
    expect(screen.getByText('new')).toBeInTheDocument();
  });

  it('does not show "new" badge for articles older than 2 hours', () => {
    const oldDate = new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(); // 3 hours ago
    render(<NewsItem news={makeNews({ published_at: oldDate })} {...defaultProps} />);
    expect(screen.queryByText('new')).not.toBeInTheDocument();
  });

  it('calls onToggleFavorite when star icon is clicked', async () => {
    const onToggleFavorite = vi.fn();
    const user = userEvent.setup();
    render(
      <NewsItem
        news={makeNews()}
        isFavorited={false}
        onSelect={vi.fn()}
        onToggleFavorite={onToggleFavorite}
      />,
    );
    const favoriteBtn = screen.getByRole('button', { name: /favorite/i });
    await user.click(favoriteBtn);
    expect(onToggleFavorite).toHaveBeenCalledWith('news-1');
  });

  it('calls onSelect when the card area is clicked', async () => {
    const onSelect = vi.fn();
    const user = userEvent.setup();
    render(
      <NewsItem
        news={makeNews()}
        isFavorited={false}
        onSelect={onSelect}
        onToggleFavorite={vi.fn()}
      />,
    );
    await user.click(screen.getByText('Test Article Title'));
    expect(onSelect).toHaveBeenCalledOnce();
  });
});
