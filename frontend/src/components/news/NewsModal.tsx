import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Typography,
  Box,
  IconButton,
  Button,
  Divider,
} from '@mui/material';
import { Close, Star, StarBorder, CalendarToday, Language } from '@mui/icons-material';
import { format } from 'date-fns';
import { NewsItem } from '../../types';

interface NewsModalProps {
  news: NewsItem | null;
  open: boolean;
  onClose: () => void;
  isFavorited: boolean;
  onToggleFavorite: (newsId: string) => void;
}

export function NewsModal({
  news,
  open,
  onClose,
  isFavorited,
  onToggleFavorite,
}: NewsModalProps) {
  if (!news) return null;

  return (
    <Dialog
      open={open}
      onClose={onClose}
      maxWidth={false}
      scroll="paper"
      PaperProps={{
        sx: {
          width: '100%',
          maxWidth: 520,
          maxHeight: '80vh',
          border: '1px solid #30363d',
          borderRadius: '12px',
          bgcolor: '#161b22',
        },
      }}
    >
      {/* Header */}
      <DialogTitle sx={{ pr: 7, pb: 1.5 }}>
        {news.category && (
          <Typography
            variant="overline"
            sx={{
              display: 'block',
              color: '#2d8eff',
              fontSize: 10,
              fontWeight: 700,
              letterSpacing: '0.08em',
              mb: 0.75,
            }}
          >
            {news.category.name}
          </Typography>
        )}

        <Typography
          variant="h6"
          component="div"
          sx={{ fontSize: 16, fontWeight: 700, lineHeight: 1.35, mb: 1 }}
        >
          {news.title}
        </Typography>

        <Box sx={{ display: 'flex', gap: 2, flexWrap: 'wrap' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
            <CalendarToday sx={{ fontSize: 12, color: '#484f58' }} />
            <Typography variant="caption" color="text.secondary" sx={{ fontSize: 11 }}>
              {format(new Date(news.published_at), 'MMM d, yyyy · HH:mm')}
            </Typography>
          </Box>
          {news.source && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5 }}>
              <Language sx={{ fontSize: 12, color: '#484f58' }} />
              <Typography variant="caption" color="text.secondary" sx={{ fontSize: 11 }}>
                {news.source}
              </Typography>
            </Box>
          )}
        </Box>

        <IconButton
          onClick={onClose}
          size="small"
          sx={{ position: 'absolute', right: 8, top: 8, color: '#8b949e' }}
        >
          <Close fontSize="small" />
        </IconButton>
      </DialogTitle>

      {/* Body */}
      <DialogContent sx={{ pt: 1.5, pb: 0 }}>
        {/* AI Summary */}
        {news.summary && (
          <>
            {news.ai_generated ? (
              <>
                <Typography
                  variant="overline"
                  sx={{
                    display: 'block',
                    color: '#3fb950',
                    fontSize: 10,
                    fontWeight: 700,
                    letterSpacing: '0.08em',
                    mb: 0.75,
                  }}
                >
                  ✦ AI Summary
                </Typography>
                <Box
                  sx={{
                    bgcolor: '#0f1f12',
                    borderLeft: '2px solid #3fb950',
                    borderRadius: '0 6px 6px 0',
                    p: '10px 12px',
                    mb: 2,
                  }}
                >
                  <Typography sx={{ color: '#8b949e', fontSize: 12, lineHeight: 1.6 }}>
                    {news.summary}
                  </Typography>
                </Box>
              </>
            ) : (
              <>
                <Typography
                  variant="overline"
                  sx={{
                    display: 'block',
                    color: '#484f58',
                    fontSize: 10,
                    fontWeight: 700,
                    letterSpacing: '0.08em',
                    mb: 0.75,
                  }}
                >
                  Summary
                </Typography>
                <Typography sx={{ color: '#8b949e', fontSize: 12, lineHeight: 1.6, mb: 2 }}>
                  {news.summary}
                </Typography>
              </>
            )}
          </>
        )}

        <Divider sx={{ borderColor: '#30363d', mb: 2 }} />

        <Typography
          variant="overline"
          sx={{
            display: 'block',
            color: '#484f58',
            fontSize: 10,
            fontWeight: 700,
            letterSpacing: '0.08em',
            mb: 0.75,
          }}
        >
          Full content
        </Typography>

        <Box sx={{ maxHeight: 300, overflowY: 'auto', pb: 2 }}>
          <Typography
            sx={{ color: '#c9d1d9', fontSize: 12, lineHeight: 1.7, whiteSpace: 'pre-wrap' }}
          >
            {news.content}
          </Typography>
        </Box>
      </DialogContent>

      {/* Footer */}
      <DialogActions sx={{ px: 3, py: 2, justifyContent: 'space-between' }}>
        <Button
          variant="outlined"
          onClick={onClose}
          sx={{
            borderColor: '#30363d',
            color: '#8b949e',
            '&:hover': { borderColor: '#8b949e', bgcolor: 'rgba(139,148,158,0.06)' },
          }}
        >
          Close
        </Button>
        <Button
          variant={isFavorited ? 'contained' : 'outlined'}
          startIcon={isFavorited ? <Star /> : <StarBorder />}
          onClick={() => onToggleFavorite(news.id)}
          sx={
            isFavorited
              ? {
                  bgcolor: '#2a2010',
                  borderColor: '#e6c85a',
                  color: '#e6c85a',
                  '&:hover': { bgcolor: '#3a3010', borderColor: '#e6c85a' },
                }
              : {
                  borderColor: '#5a4a1a',
                  color: '#e6c85a',
                  '&:hover': { borderColor: '#e6c85a', bgcolor: 'rgba(230,200,90,0.06)' },
                }
          }
        >
          {isFavorited ? 'Favorited' : 'Favorite'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
