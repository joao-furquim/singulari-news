import {
  Card,
  CardActionArea,
  CardContent,
  Box,
  Typography,
  Chip,
  IconButton,
  Avatar,
} from '@mui/material';
import {
  Computer,
  Psychology,
  BusinessCenter,
  Science,
  Lightbulb,
  Public,
  Article,
  Star,
  StarBorder,
  HealthAndSafety,
  RocketLaunch,
  EnergySavingsLeaf,
  AccountBalance,
  Sports,
  TheaterComedy,
  Work,
  Movie,
  Groups,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { NewsItem as NewsItemType } from '../../types';

interface CategoryConfig {
  icon: React.ElementType;
  bg: string;
  color: string;
}

const CATEGORY_CONFIG: Record<string, CategoryConfig> = {
  // English slugs (current classifier output)
  technology:    { icon: Computer,         bg: '#0d1f2d', color: '#185fa5' },
  ai:            { icon: Psychology,       bg: '#0f1f12', color: '#3fb950' },
  business:      { icon: BusinessCenter,   bg: '#1f1a0d', color: '#854f0b' },
  science:       { icon: Science,          bg: '#1a0f2a', color: '#534ab7' },
  innovation:    { icon: Lightbulb,        bg: '#0d1a2a', color: '#378add' },
  politics:      { icon: Public,           bg: '#2a0d1a', color: '#993556' },
  health:        { icon: HealthAndSafety,  bg: '#0d2a1a', color: '#3fb95a' },
  space:         { icon: RocketLaunch,     bg: '#0d0d2a', color: '#7070e0' },
  climate:       { icon: EnergySavingsLeaf, bg: '#1a2a0d', color: '#7ab03f' },
  finance:       { icon: AccountBalance,   bg: '#1a1f0d', color: '#d4a017' },
  sports:        { icon: Sports,           bg: '#2a0d0d', color: '#e05050' },
  culture:       { icon: TheaterComedy,    bg: '#1a0d2a', color: '#9050c0' },
  labor:         { icon: Work,             bg: '#1a1a0d', color: '#a0a030' },
  entertainment: { icon: Movie,            bg: '#2a0d1a', color: '#c04080' },
  society:       { icon: Groups,           bg: '#0d1a2a', color: '#3090b0' },
  general:       { icon: Article,          bg: '#1c2128', color: '#8b949e' },
  // Legacy Portuguese slugs (backward compat for old articles)
  tecnologia:    { icon: Computer,         bg: '#0d1f2d', color: '#185fa5' },
  ia:            { icon: Psychology,       bg: '#0f1f12', color: '#3fb950' },
  negocios:      { icon: BusinessCenter,   bg: '#1f1a0d', color: '#854f0b' },
  ciencia:       { icon: Science,          bg: '#1a0f2a', color: '#534ab7' },
  inovacao:      { icon: Lightbulb,        bg: '#0d1a2a', color: '#378add' },
  politica:      { icon: Public,           bg: '#2a0d1a', color: '#993556' },
};

const DEFAULT_CONFIG: CategoryConfig = {
  icon: Article,
  bg: '#1c2128',
  color: '#8b949e',
};

interface NewsItemProps {
  news: NewsItemType;
  isFavorited: boolean;
  onSelect: (news: NewsItemType) => void;
  onToggleFavorite: (newsId: string) => void;
}

function isRecent(publishedAt: string): boolean {
  return Date.now() - new Date(publishedAt).getTime() < 2 * 60 * 60 * 1000;
}

export function NewsItem({
  news,
  isFavorited,
  onSelect,
  onToggleFavorite,
}: NewsItemProps) {
  const cfg = CATEGORY_CONFIG[news.category?.slug ?? ''] ?? DEFAULT_CONFIG;
  const CategoryIcon = cfg.icon;
  const recent = isRecent(news.published_at);

  return (
    <Card
      elevation={0}
      sx={{
        border: '1px solid',
        borderColor: 'divider',
        borderRadius: 2,
        mb: 1.5,
        transition: 'border-color 0.15s',
        '&:hover': { borderColor: 'primary.main' },
      }}
    >
      <CardActionArea onClick={() => onSelect(news)}>
        <CardContent
          sx={{ display: 'flex', gap: 2, alignItems: 'flex-start', p: 2 }}
        >
          {/* Category thumbnail */}
          <Avatar
            sx={{
              width: 76,
              height: 58,
              bgcolor: cfg.bg,
              flexShrink: 0,
              borderRadius: '6px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
            }}
          >
            <CategoryIcon sx={{ color: cfg.color, fontSize: 26 }} />
          </Avatar>

          <Box sx={{ flex: 1, minWidth: 0 }}>
            {/* Badges */}
            <Box sx={{ display: 'flex', gap: 0.5, mb: 0.75, flexWrap: 'wrap' }}>
              {news.category && (
                <Chip
                  label={news.category.name}
                  size="small"
                  sx={{ height: 18, fontSize: 10, borderRadius: '4px' }}
                />
              )}
              {recent && (
                <Chip
                  label="new"
                  size="small"
                  color="primary"
                  sx={{ height: 18, fontSize: 10, borderRadius: '4px' }}
                />
              )}
              {news.ai_generated && (
                <Chip
                  label="✦ AI"
                  size="small"
                  sx={{
                    height: 18,
                    fontSize: 10,
                    borderRadius: '4px',
                    bgcolor: '#0a1f0f',
                    color: 'success.main',
                    border: '1px solid',
                    borderColor: 'success.main',
                  }}
                />
              )}
            </Box>

            <Typography
              variant="subtitle1"
              fontWeight={600}
              sx={{
                overflow: 'hidden',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                lineHeight: 1.35,
                mb: 0.5,
              }}
            >
              {news.title}
            </Typography>

            <Typography variant="caption" color="text.secondary">
              {news.source} ·{' '}
              {formatDistanceToNow(new Date(news.published_at), {
                addSuffix: true,
              })}
            </Typography>
          </Box>

          {/* Favorite */}
          <IconButton
            size="small"
            aria-label={isFavorited ? 'unfavorite article' : 'favorite article'}
            onClick={(e) => {
              e.stopPropagation();
              onToggleFavorite(news.id);
            }}
            sx={{ flexShrink: 0, alignSelf: 'center' }}
          >
            {isFavorited ? (
              <Star sx={{ color: 'warning.main' }} fontSize="small" />
            ) : (
              <StarBorder fontSize="small" />
            )}
          </IconButton>
        </CardContent>
      </CardActionArea>
    </Card>
  );
}
