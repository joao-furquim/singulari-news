import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Tooltip,
  Button,
  Pagination,
} from '@mui/material';
import { Edit, Delete, FirstPage, LastPage } from '@mui/icons-material';
import { format } from 'date-fns';
import client from '../../api/client';
import { NewsItem, Category, PaginatedResponse } from '../../types';

interface NewsForm {
  title: string;
  content: string;
  category_id: string;
  published_at: string; // datetime-local input value: YYYY-MM-DDTHH:MM
}

const LIMIT_OPTIONS = [10, 20, 50] as const;
const cellSx = { color: '#c9d1d9', fontSize: 13, borderColor: '#30363d' };
const headSx = { color: '#8b949e', fontSize: 12, fontWeight: 600, borderColor: '#30363d', bgcolor: '#161b22' };

function toDatetimeLocal(iso: string): string {
  // Converts ISO string to the format required by <input type="datetime-local">
  return iso.slice(0, 16); // "YYYY-MM-DDTHH:MM"
}

const paginationSx = {
  '& .MuiPaginationItem-root': { color: '#8b949e', borderColor: '#30363d' },
  '& .Mui-selected': { background: '#1a3a5c !important', borderColor: '#2d8eff', color: '#2d8eff' },
};

const iconBtnSx = (disabled: boolean) => ({
  color: disabled ? '#484f58' : '#8b949e',
});

export function NewsManagement() {
  const [news, setNews] = useState<NewsItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);

  const [editOpen, setEditOpen] = useState(false);
  const [editTarget, setEditTarget] = useState<NewsItem | null>(null);
  const [form, setForm] = useState<NewsForm>({ title: '', content: '', category_id: '', published_at: '' });
  const [saving, setSaving] = useState(false);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<NewsItem | null>(null);
  const [deleting, setDeleting] = useState(false);

  const fetchNews = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await client.get<PaginatedResponse<NewsItem>>('/news', {
        params: { page, limit },
      });
      setNews(data.items);
      setTotal(data.total);
      setPages(Math.max(1, data.pages));
    } catch {
      // ignore
    } finally {
      setLoading(false);
    }
  }, [page, limit]);

  useEffect(() => { void fetchNews(); }, [fetchNews]);

  useEffect(() => {
    client.get<Category[]>('/preferences')
      .then(({ data }) => setCategories(data))
      .catch(() => undefined);
  }, []);

  const openEdit = (item: NewsItem) => {
    setEditTarget(item);
    setForm({
      title: item.title,
      content: item.content,
      category_id: item.category?.id ?? '',
      published_at: toDatetimeLocal(item.published_at),
    });
    setEditOpen(true);
  };

  const handleSave = async () => {
    if (!editTarget) return;
    setSaving(true);
    try {
      await client.put(`/news/${editTarget.id}`, {
        title: form.title,
        content: form.content,
        published_at: form.published_at ? new Date(form.published_at).toISOString() : undefined,
      });
      setEditOpen(false);
      void fetchNews();
    } catch {
      // ignore
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await client.delete(`/news/${deleteTarget.id}`);
      setDeleteOpen(false);
      void fetchNews();
    } catch {
      // ignore
    } finally {
      setDeleting(false);
    }
  };

  const handleLimitChange = (newLimit: number) => {
    setLimit(newLimit);
    setPage(1);
  };

  const start = total === 0 ? 0 : (page - 1) * limit + 1;
  const end = Math.min(page * limit, total);

  return (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 3 }}>
        News Management
      </Typography>

      <Box sx={{ border: '1px solid #30363d', borderRadius: 2, overflow: 'hidden' }}>
        <TableContainer component={Paper} sx={{ bgcolor: '#161b22' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={headSx}>Title</TableCell>
                <TableCell sx={headSx}>Category</TableCell>
                <TableCell sx={headSx}>Source</TableCell>
                <TableCell sx={headSx}>Published at</TableCell>
                <TableCell sx={headSx}>AI</TableCell>
                <TableCell sx={{ ...headSx, width: 90 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={6} sx={{ textAlign: 'center', py: 4, borderColor: '#30363d' }}>
                    <CircularProgress size={24} />
                  </TableCell>
                </TableRow>
              ) : news.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={6} sx={{ textAlign: 'center', py: 4, color: '#8b949e', borderColor: '#30363d' }}>
                    No articles yet. The agent will populate this list.
                  </TableCell>
                </TableRow>
              ) : news.map((item) => (
                <TableRow key={item.id} sx={{ '&:hover': { bgcolor: 'rgba(255,255,255,0.02)' } }}>
                  <TableCell sx={cellSx}>
                    <Tooltip title={item.title}>
                      <span>{item.title.length > 50 ? `${item.title.slice(0, 50)}…` : item.title}</span>
                    </Tooltip>
                  </TableCell>
                  <TableCell sx={cellSx}>{item.category?.name ?? '—'}</TableCell>
                  <TableCell sx={cellSx}>{item.source || '—'}</TableCell>
                  <TableCell sx={cellSx}>
                    {format(new Date(item.published_at), 'MMM d, yyyy')}
                  </TableCell>
                  <TableCell sx={cellSx}>
                    <Chip
                      label={item.ai_generated ? 'AI' : 'Manual'}
                      size="small"
                      sx={{
                        fontSize: 11, height: 20,
                        bgcolor: item.ai_generated ? 'rgba(63,185,80,0.12)' : 'rgba(139,148,158,0.12)',
                        color: item.ai_generated ? '#3fb950' : '#8b949e',
                        border: '1px solid',
                        borderColor: item.ai_generated ? '#3fb950' : '#30363d',
                      }}
                    />
                  </TableCell>
                  <TableCell sx={{ borderColor: '#30363d' }}>
                    <IconButton size="small" onClick={() => openEdit(item)} sx={{ color: '#8b949e' }}>
                      <Edit fontSize="small" />
                    </IconButton>
                    <IconButton size="small" onClick={() => { setDeleteTarget(item); setDeleteOpen(true); }} sx={{ color: '#e85555' }}>
                      <Delete fontSize="small" />
                    </IconButton>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>

        {/* Standardized pagination footer */}
        <Box sx={{
          bgcolor: '#161b22',
          borderTop: '1px solid #30363d',
          px: '20px',
          py: '12px',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <FormControl size="small">
              <Select
                value={limit}
                onChange={(e) => handleLimitChange(Number(e.target.value))}
                sx={{
                  fontSize: 12, color: '#8b949e',
                  '& .MuiOutlinedInput-notchedOutline': { borderColor: '#30363d' },
                  '&:hover .MuiOutlinedInput-notchedOutline': { borderColor: '#8b949e' },
                  '& .MuiSvgIcon-root': { color: '#8b949e' },
                }}
              >
                {LIMIT_OPTIONS.map((n) => (
                  <MenuItem key={n} value={n} sx={{ fontSize: 12 }}>{n} per page</MenuItem>
                ))}
              </Select>
            </FormControl>
            <Typography sx={{ color: '#8b949e', fontSize: 12 }}>
              Showing {start}–{end} of {total} items
            </Typography>
          </Box>

          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <IconButton size="small" onClick={() => setPage(1)} disabled={page === 1} sx={iconBtnSx(page === 1)}>
              <FirstPage fontSize="small" />
            </IconButton>
            <Pagination
              count={pages}
              page={page}
              onChange={(_, p) => setPage(p)}
              size="small"
              sx={paginationSx}
            />
            <IconButton size="small" onClick={() => setPage(pages)} disabled={page === pages} sx={iconBtnSx(page === pages)}>
              <LastPage fontSize="small" />
            </IconButton>
          </Box>
        </Box>
      </Box>

      {/* Edit modal */}
      <Dialog
        open={editOpen}
        onClose={() => setEditOpen(false)}
        maxWidth="sm"
        fullWidth
        PaperProps={{ sx: { bgcolor: '#161b22', border: '1px solid #30363d', borderRadius: 2 } }}
      >
        <DialogTitle>Edit Article</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '16px !important' }}>
          <TextField
            label="Title"
            value={form.title}
            onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))}
            fullWidth size="small"
          />
          <TextField
            label="Content"
            value={form.content}
            onChange={(e) => setForm((f) => ({ ...f, content: e.target.value }))}
            fullWidth multiline minRows={4} size="small"
          />
          <FormControl fullWidth size="small">
            <InputLabel>Category</InputLabel>
            <Select
              label="Category"
              value={form.category_id}
              onChange={(e) => setForm((f) => ({ ...f, category_id: e.target.value }))}
            >
              {categories.map((cat) => (
                <MenuItem key={cat.id} value={cat.id}>{cat.name}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="Published at"
            type="datetime-local"
            value={form.published_at}
            onChange={(e) => setForm((f) => ({ ...f, published_at: e.target.value }))}
            size="small"
            fullWidth
            InputLabelProps={{ shrink: true }}
            sx={{ '& input': { colorScheme: 'dark' } }}
          />
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button color="inherit" onClick={() => setEditOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => void handleSave()} disabled={saving || !form.title}>
            {saving ? 'Saving…' : 'Save'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete confirmation */}
      <Dialog
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        PaperProps={{ sx: { bgcolor: '#161b22', border: '1px solid #30363d', borderRadius: 2 } }}
      >
        <DialogTitle>Delete article?</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Are you sure you want to delete this article? This action cannot be undone.
          </Typography>
          {deleteTarget && (
            <Typography variant="body2" sx={{ mt: 1, color: '#c9d1d9', fontStyle: 'italic' }}>
              "{deleteTarget.title.length > 60 ? `${deleteTarget.title.slice(0, 60)}…` : deleteTarget.title}"
            </Typography>
          )}
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button color="inherit" onClick={() => setDeleteOpen(false)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={() => void handleDelete()} disabled={deleting}>
            {deleting ? 'Deleting…' : 'Confirm'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
