import { useState } from 'react';
import { Box } from '@mui/material';
import { Navbar } from '../components/layout/Navbar';
import { FilterBar } from '../components/layout/FilterBar';
import { NewsList } from '../components/news/NewsList';
import { NewsModal } from '../components/news/NewsModal';
import { AuthModal } from '../components/auth/AuthModal';
import { ChangePasswordModal } from '../components/auth/ChangePasswordModal';
import { PreferencesModal } from '../components/preferences/PreferencesModal';
import { ProfileModal } from '../components/profile/ProfileModal';
import { DateRangeModal } from '../components/DateRangeModal';
import { useNewsPolling } from '../hooks/useNewsPolling';
import { useFeedFilters } from '../hooks/useFeedFilters';
import { useAuthGuard } from '../hooks/useAuthGuard';
import { NewsItem } from '../types';
import client from '../api/client';

export function HomePage() {
  const {
    filters,
    setPeriod,
    setDateRange,
    toggleCategory,
    setPage,
    setLimit,
    setFavoritesOnly,
    resetCategories,
  } = useFeedFilters();

  const { news, total, pages, loading, newArticlesCount, refreshNews } =
    useNewsPolling(filters);

  // Modal state
  const [authOpen, setAuthOpen] = useState(false);
  const [prefOpen, setPrefOpen] = useState(false);
  const [prefMode, setPrefMode] = useState<'onboarding' | 'edit'>('edit');
  const [profileOpen, setProfileOpen] = useState(false);
  const [newsModalOpen, setNewsModalOpen] = useState(false);
  const [selectedNews, setSelectedNews] = useState<NewsItem | null>(null);
  const [datePickerOpen, setDatePickerOpen] = useState(false);

  // Local favorites state
  const [favorites, setFavorites] = useState<Set<string>>(new Set());

  const { executeOrGuard } = useAuthGuard(() => setAuthOpen(true));

  const handleSelectNews = (item: NewsItem) => {
    setSelectedNews(item);
    setNewsModalOpen(true);
  };

  const handleToggleFavorite = (newsId: string) => {
    executeOrGuard(async () => {
      const isFav = favorites.has(newsId);
      try {
        if (isFav) {
          await client.delete(`/news/${newsId}/favorite`);
          setFavorites((prev) => {
            const next = new Set(prev);
            next.delete(newsId);
            return next;
          });
        } else {
          await client.post(`/news/${newsId}/favorite`);
          setFavorites((prev) => new Set([...prev, newsId]));
        }
      } catch {
        // ignore
      }
    });
  };

  const handleSignUpSuccess = () => {
    setPrefMode('onboarding');
    setPrefOpen(true);
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: 'background.default' }}>
      <Navbar
        onSignIn={() => setAuthOpen(true)}
        onProfile={() => setProfileOpen(true)}
        onPreferences={() => { setPrefMode('edit'); setPrefOpen(true); }}
      />

      <FilterBar
        filters={filters}
        onPeriodChange={setPeriod}
        onCategoryToggle={toggleCategory}
        onClearCategories={() => resetCategories([])}
        onFavoritesToggle={() => setFavoritesOnly(!filters.favoritesOnly)}
        onOpenDatePicker={() => setDatePickerOpen(true)}
        onAuthRequired={() => setAuthOpen(true)}
      />

      {/* Feed container */}
      <Box sx={{ maxWidth: 900, mx: 'auto', px: 2, py: 3 }}>
        <NewsList
          news={news}
          total={total}
          pages={pages}
          currentPage={filters.page}
          limit={filters.limit}
          loading={loading}
          newArticlesCount={newArticlesCount}
          favorites={favorites}
          onSelectNews={handleSelectNews}
          onToggleFavorite={handleToggleFavorite}
          onPageChange={setPage}
          onLimitChange={setLimit}
          onRefreshNews={async () => {
            await refreshNews();          // fetch page 1 → update display → reset counter
            setPage(1);                   // sync filter state (no-op if already on page 1)
          }}
        />
      </Box>

      {/* Modais */}
      <NewsModal
        news={selectedNews}
        open={newsModalOpen}
        onClose={() => setNewsModalOpen(false)}
        isFavorited={selectedNews ? favorites.has(selectedNews.id) : false}
        onToggleFavorite={handleToggleFavorite}
      />

      <AuthModal
        open={authOpen}
        onClose={() => setAuthOpen(false)}
        onSignUpSuccess={handleSignUpSuccess}
      />

      <PreferencesModal
        open={prefOpen}
        mode={prefMode}
        onClose={() => setPrefOpen(false)}
      />

      <ProfileModal open={profileOpen} onClose={() => setProfileOpen(false)} />

      <DateRangeModal
        open={datePickerOpen}
        onClose={() => setDatePickerOpen(false)}
        onApply={(from, to) => {
          setDateRange(from, to);
          setDatePickerOpen(false);
        }}
      />

      <ChangePasswordModal />
    </Box>
  );
}
