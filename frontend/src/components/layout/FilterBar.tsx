import { Box, Chip, Divider } from '@mui/material';
import {
  CalendarMonth,
  Star,
  StarBorder,
  Computer,
  Psychology,
  BusinessCenter,
  Science,
  HealthAndSafety,
  Public,
  Sports,
  Article,
} from '@mui/icons-material';
import { SxProps, Theme } from '@mui/material/styles';
import { Period, FeedFilters } from '../../hooks/useFeedFilters';
import { useAuth } from '../../contexts/AuthContext';

interface FilterBarProps {
  filters: FeedFilters;
  onPeriodChange: (period: Period) => void;
  onCategoryToggle: (slug: string) => void;
  onClearCategories: () => void;
  onFavoritesToggle: () => void;
  onOpenDatePicker: () => void;
  onAuthRequired: () => void;
}

interface FixedCategory {
  slug: string;
  label: string;
  Icon: React.ElementType;
}

const FIXED_CATEGORIES: FixedCategory[] = [
  { slug: 'technology', label: 'Technology', Icon: Computer },
  { slug: 'ai',         label: 'AI',         Icon: Psychology },
  { slug: 'business',   label: 'Business',   Icon: BusinessCenter },
  { slug: 'science',    label: 'Science',    Icon: Science },
  { slug: 'health',     label: 'Health',     Icon: HealthAndSafety },
  { slug: 'politics',   label: 'Politics',   Icon: Public },
  { slug: 'sports',     label: 'Sports',     Icon: Sports },
  { slug: 'general',    label: 'General',    Icon: Article },
];

const PERIOD_LABELS: Record<Period, string> = {
  today: 'Today',
  week: 'This Week',
  month: 'This Month',
  custom: 'Custom Range',
};
const PERIODS: Period[] = ['today', 'week', 'month', 'custom'];

const chipSx = (active: boolean): SxProps<Theme> => ({
  height: 28,
  borderRadius: '20px',
  border: '1px solid',
  borderColor: active ? '#2d8eff' : '#30363d',
  bgcolor: active ? '#1a3a5c' : 'transparent',
  color: active ? '#2d8eff' : '#8b949e',
  fontSize: 13,
  fontWeight: active ? 600 : 400,
  cursor: 'pointer',
  flexShrink: 0,
  '& .MuiChip-label': { px: 1.5 },
  '& .MuiChip-icon': {
    color: 'inherit !important',
    fontSize: '14px !important',
    ml: '6px',
  },
  '&:hover': {
    borderColor: '#2d8eff',
    color: '#2d8eff',
    bgcolor: active ? '#1a3a5c' : 'rgba(45,142,255,0.06)',
  },
  '&.MuiButtonBase-root:hover': {
    bgcolor: active ? '#1a3a5c' : 'rgba(45,142,255,0.06)',
  },
});

const favChipSx = (active: boolean): SxProps<Theme> => ({
  height: 28,
  borderRadius: '20px',
  border: '1px solid',
  borderColor: active ? '#e6c85a' : '#5a4a1a',
  bgcolor: active ? '#2a2010' : 'transparent',
  color: '#e6c85a',
  fontSize: 13,
  fontWeight: active ? 600 : 400,
  cursor: 'pointer',
  flexShrink: 0,
  '& .MuiChip-label': { px: 1.5 },
  '& .MuiChip-icon': { color: '#e6c85a !important', fontSize: '14px !important', ml: '6px' },
  '&:hover': {
    borderColor: '#e6c85a',
    bgcolor: active ? '#3a3010' : 'rgba(230,200,90,0.06)',
  },
  '&.MuiButtonBase-root:hover': {
    bgcolor: active ? '#3a3010' : 'rgba(230,200,90,0.06)',
  },
});

export function FilterBar({
  filters,
  onPeriodChange,
  onCategoryToggle,
  onClearCategories,
  onFavoritesToggle,
  onOpenDatePicker,
  onAuthRequired,
}: FilterBarProps) {
  const { isAuthenticated } = useAuth();

  const handleFavoritesClick = () => {
    if (isAuthenticated) {
      onFavoritesToggle();
    } else {
      onAuthRequired();
    }
  };

  const isAllActive = filters.categories.length === 0 && !filters.favoritesOnly;

  return (
    <Box
      sx={{
        px: 2,
        py: 1.5,
        borderBottom: '1px solid',
        borderColor: 'divider',
        bgcolor: 'background.paper',
        display: 'flex',
        alignItems: 'center',
        gap: 0.75,
        overflow: 'hidden',
      }}
    >
      {/* Period chips — fixed, never scroll */}
      <Box sx={{ display: 'flex', gap: 0.75, flexShrink: 0 }}>
        {PERIODS.map((period) => (
          <Chip
            key={period}
            label={PERIOD_LABELS[period]}
            icon={period === 'custom' ? <CalendarMonth /> : undefined}
            onClick={() =>
              period === 'custom' ? onOpenDatePicker() : onPeriodChange(period)
            }
            sx={chipSx(filters.period === period && !filters.favoritesOnly)}
          />
        ))}
      </Box>

      <Divider
        orientation="vertical"
        flexItem
        sx={{ borderColor: '#30363d', flexShrink: 0, mx: 0.25 }}
      />

      {/* Category chips — horizontally scrollable, never wrap */}
      <Box
        sx={{
          display: 'flex',
          gap: 1,
          flex: 1,
          overflowX: 'auto',
          flexWrap: 'nowrap',
          alignItems: 'center',
          pb: 0.5,
          mb: -0.5,
          '&::-webkit-scrollbar': { height: 4 },
          '&::-webkit-scrollbar-track': { bgcolor: 'transparent' },
          '&::-webkit-scrollbar-thumb': {
            background: '#30363d',
            borderRadius: 2,
            '&:hover': { background: '#484f58' },
          },
        }}
      >
        {/* "All" clears selection */}
        <Chip
          label="All"
          onClick={onClearCategories}
          sx={chipSx(isAllActive)}
        />

        {FIXED_CATEGORIES.map(({ slug, label, Icon }) => {
          const active = filters.categories.includes(slug) && !filters.favoritesOnly;
          return (
            <Chip
              key={slug}
              label={label}
              icon={<Icon />}
              onClick={() => onCategoryToggle(slug)}
              sx={chipSx(active)}
            />
          );
        })}
      </Box>

      {/* Favorites chip — fixed right */}
      <Chip
        label="Favorites"
        icon={filters.favoritesOnly ? <Star /> : <StarBorder />}
        onClick={handleFavoritesClick}
        sx={favChipSx(filters.favoritesOnly)}
      />
    </Box>
  );
}
