import {
  Box,
  Collapse,
  Pagination,
  Typography,
  Skeleton,
  Stack,
  Select,
  MenuItem,
  FormControl,
  IconButton,
} from '@mui/material';
import { FirstPage, LastPage, Refresh } from '@mui/icons-material';
import { NewsItem } from './NewsItem';
import { NewsItem as NewsItemType } from '../../types';

const LIMIT_OPTIONS = [10, 20, 50] as const;

interface NewsListProps {
  news: NewsItemType[];
  total: number;
  pages: number;
  currentPage: number;
  limit: number;
  loading: boolean;
  newArticlesCount: number;
  favorites: Set<string>;
  onSelectNews: (news: NewsItemType) => void;
  onToggleFavorite: (newsId: string) => void;
  onPageChange: (page: number) => void;
  onLimitChange: (limit: number) => void;
  onRefreshNews: () => void | Promise<void>;
}

export function NewsList({
  news,
  total,
  pages,
  currentPage,
  limit,
  loading,
  newArticlesCount,
  favorites,
  onSelectNews,
  onToggleFavorite,
  onPageChange,
  onLimitChange,
  onRefreshNews,
}: NewsListProps) {
  const start = total === 0 ? 0 : (currentPage - 1) * limit + 1;
  const end = Math.min(currentPage * limit, total);

  return (
    <Box>
      {/* New articles banner — always rendered so Collapse animates correctly */}
      <Collapse in={newArticlesCount > 0} unmountOnExit>
        <Box
          onClick={onRefreshNews}
          sx={{
            background: '#1a3a5c',
            border: '1px solid #2d8eff',
            borderRadius: '8px',
            padding: '10px 16px',
            marginBottom: '12px',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            userSelect: 'none',
            '&:hover': { background: '#1f4570' },
          }}
        >
          <Typography sx={{ color: '#2d8eff', fontSize: 13, fontWeight: 500 }}>
            ↑ {newArticlesCount} new article{newArticlesCount !== 1 ? 's' : ''} available — click to refresh
          </Typography>
          <Refresh sx={{ color: '#2d8eff', fontSize: 18 }} />
        </Box>
      </Collapse>

      {/* Loading skeletons */}
      {loading ? (
        <Stack spacing={1.5}>
          {Array.from({ length: limit > 10 ? 8 : 6 }).map((_, i) => (
            <Skeleton key={i} variant="rounded" height={96} />
          ))}
        </Stack>
      ) : news.length === 0 ? (
        <Box sx={{ textAlign: 'center', py: 10 }}>
          <Typography color="text.secondary">
            No articles found for the selected filters.
          </Typography>
        </Box>
      ) : (
        <>
          {/* Header row: per-page select + range info */}
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              mb: 2,
              flexWrap: 'wrap',
              gap: 1,
            }}
          >
            <FormControl size="small">
              <Select
                value={limit}
                onChange={(e) => onLimitChange(Number(e.target.value))}
                sx={{
                  fontSize: 13,
                  color: '#8b949e',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#30363d' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#8b949e' },
                  '& .MuiSvgIcon-root': { color: '#8b949e' },
                }}
              >
                {LIMIT_OPTIONS.map((n) => (
                  <MenuItem key={n} value={n} sx={{ fontSize: 13 }}>
                    {n} per page
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <Typography variant="caption" color="text.secondary" sx={{ fontSize: 13 }}>
              Showing {start}–{end} of {total} {total === 1 ? 'article' : 'articles'}
            </Typography>
          </Box>

          {/* Article list */}
          {news.map((item) => (
            <NewsItem
              key={item.id}
              news={item}
              isFavorited={favorites.has(item.id)}
              onSelect={onSelectNews}
              onToggleFavorite={onToggleFavorite}
            />
          ))}

          {/* Pagination row */}
          {pages > 1 && (
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                mt: 3,
                gap: 0.5,
              }}
            >
              <IconButton
                size="small"
                onClick={() => onPageChange(1)}
                disabled={currentPage === 1}
                sx={{ color: currentPage === 1 ? '#484f58' : '#8b949e' }}
              >
                <FirstPage fontSize="small" />
              </IconButton>

              <Pagination
                count={pages}
                page={currentPage}
                onChange={(_, page) => onPageChange(page)}
                color="primary"
                shape="rounded"
                siblingCount={1}
                boundaryCount={0}
              />

              <IconButton
                size="small"
                onClick={() => onPageChange(pages)}
                disabled={currentPage === pages}
                sx={{ color: currentPage === pages ? '#484f58' : '#8b949e' }}
              >
                <LastPage fontSize="small" />
              </IconButton>
            </Box>
          )}
        </>
      )}
    </Box>
  );
}
