import { useState, useEffect, useCallback } from 'react';
import {
  Box,
  Typography,
  Button,
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
  Pagination,
} from '@mui/material';
import { Add, Delete, FirstPage, LastPage } from '@mui/icons-material';
import { format } from 'date-fns';
import client from '../../api/client';
import { User, PaginatedResponse } from '../../types';

type Role = 'user' | 'reviewer' | 'admin';

interface InviteForm {
  name: string;
  email: string;
  password: string;
  role: Role;
}

const LIMIT_OPTIONS = [10, 20, 50] as const;
const EMPTY_INVITE: InviteForm = { name: '', email: '', password: '', role: 'user' };

const cellSx = { color: '#c9d1d9', fontSize: 13, borderColor: '#30363d' };
const headSx = { color: '#8b949e', fontSize: 12, fontWeight: 600, borderColor: '#30363d', bgcolor: '#161b22' };

const paginationSx = {
  '& .MuiPaginationItem-root': { color: '#8b949e', borderColor: '#30363d' },
  '& .Mui-selected': { background: '#1a3a5c !important', borderColor: '#2d8eff', color: '#2d8eff' },
};

const iconBtnSx = (disabled: boolean) => ({
  color: disabled ? '#484f58' : '#8b949e',
});

const ROLE_COLORS: Record<string, { bg: string; color: string; border: string }> = {
  user:     { bg: 'rgba(139,148,158,0.12)', color: '#8b949e', border: '#30363d' },
  reviewer: { bg: 'rgba(45,142,255,0.12)',  color: '#2d8eff', border: '#2d8eff' },
  admin:    { bg: 'rgba(188,120,255,0.12)', color: '#bc78ff', border: '#bc78ff' },
  root:     { bg: 'rgba(255,80,80,0.12)',   color: '#e85555', border: '#e85555' },
};

export function UserManagement() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [limit, setLimit] = useState(10);
  const [total, setTotal] = useState(0);
  const [pages, setPages] = useState(1);

  const [inviteOpen, setInviteOpen] = useState(false);
  const [inviteForm, setInviteForm] = useState<InviteForm>(EMPTY_INVITE);
  const [inviting, setInviting] = useState(false);

  const [deleteOpen, setDeleteOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<User | null>(null);
  const [deleting, setDeleting] = useState(false);

  const [roleChanging, setRoleChanging] = useState<string | null>(null);

  const fetchUsers = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await client.get<PaginatedResponse<User>>('/users', {
        params: { page, limit },
      });
      setUsers(data.items);
      setTotal(data.total);
      setPages(Math.max(1, data.pages));
    } catch {
      setUsers([]);
    } finally {
      setLoading(false);
    }
  }, [page, limit]);

  useEffect(() => { void fetchUsers(); }, [fetchUsers]);

  const handleRoleChange = async (userId: string, role: Role) => {
    setRoleChanging(userId);
    try {
      await client.put(`/users/${userId}/role`, { role });
      setUsers((prev) => prev.map((u) => (u.id === userId ? { ...u, role } : u)));
    } catch {
      // ignore
    } finally {
      setRoleChanging(null);
    }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    try {
      await client.delete(`/users/${deleteTarget.id}`);
      setDeleteOpen(false);
      void fetchUsers();
    } catch {
      // ignore
    } finally {
      setDeleting(false);
    }
  };

  const handleInvite = async () => {
    setInviting(true);
    try {
      await client.post('/users/invite', inviteForm);
      setInviteOpen(false);
      setInviteForm(EMPTY_INVITE);
      void fetchUsers();
    } catch {
      // ignore
    } finally {
      setInviting(false);
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
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, flex: 1 }}>
          Users
        </Typography>
        <Button
          variant="contained"
          startIcon={<Add />}
          size="small"
          onClick={() => { setInviteForm(EMPTY_INVITE); setInviteOpen(true); }}
        >
          Invite User
        </Button>
      </Box>

      <Box sx={{ border: '1px solid #30363d', borderRadius: 2, overflow: 'hidden' }}>
        <TableContainer component={Paper} sx={{ bgcolor: '#161b22' }}>
          <Table size="small">
            <TableHead>
              <TableRow>
                <TableCell sx={headSx}>Name</TableCell>
                <TableCell sx={headSx}>Email</TableCell>
                <TableCell sx={headSx}>Role</TableCell>
                <TableCell sx={headSx}>Created at</TableCell>
                <TableCell sx={{ ...headSx, width: 220 }}>Actions</TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={5} sx={{ textAlign: 'center', py: 4, borderColor: '#30363d' }}>
                    <CircularProgress size={24} />
                  </TableCell>
                </TableRow>
              ) : users.map((user) => {
                const rc = ROLE_COLORS[user.role] ?? ROLE_COLORS.user;
                const isRoot = user.role === 'root';
                return (
                  <TableRow key={user.id} sx={{ '&:hover': { bgcolor: 'rgba(255,255,255,0.02)' } }}>
                    <TableCell sx={cellSx}>{user.name}</TableCell>
                    <TableCell sx={cellSx}>{user.email}</TableCell>
                    <TableCell sx={cellSx}>
                      <Chip
                        label={user.role}
                        size="small"
                        sx={{
                          fontSize: 11, height: 20,
                          bgcolor: rc.bg, color: rc.color,
                          border: `1px solid ${rc.border}`,
                          textTransform: 'capitalize',
                        }}
                      />
                    </TableCell>
                    <TableCell sx={cellSx}>
                      {format(new Date(user.created_at), 'MMM d, yyyy')}
                    </TableCell>
                    <TableCell sx={{ borderColor: '#30363d' }}>
                      {!isRoot && (
                        <FormControl size="small" sx={{ minWidth: 120, mr: 1 }}>
                          <Select
                            value={user.role}
                            onChange={(e) => void handleRoleChange(user.id, e.target.value as Role)}
                            disabled={roleChanging === user.id}
                            sx={{ fontSize: 12, height: 28 }}
                          >
                            <MenuItem value="user" sx={{ fontSize: 12 }}>User</MenuItem>
                            <MenuItem value="reviewer" sx={{ fontSize: 12 }}>Reviewer</MenuItem>
                            <MenuItem value="admin" sx={{ fontSize: 12 }}>Admin</MenuItem>
                          </Select>
                        </FormControl>
                      )}
                      {!isRoot && (
                        <IconButton
                          size="small"
                          onClick={() => { setDeleteTarget(user); setDeleteOpen(true); }}
                          sx={{ color: '#e85555' }}
                        >
                          <Delete fontSize="small" />
                        </IconButton>
                      )}
                    </TableCell>
                  </TableRow>
                );
              })}
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

      {/* Invite User modal */}
      <Dialog
        open={inviteOpen}
        onClose={() => setInviteOpen(false)}
        maxWidth="xs"
        fullWidth
        PaperProps={{ sx: { bgcolor: '#161b22', border: '1px solid #30363d', borderRadius: 2 } }}
      >
        <DialogTitle>Invite User</DialogTitle>
        <DialogContent sx={{ display: 'flex', flexDirection: 'column', gap: 2, pt: '16px !important' }}>
          <TextField label="Name" value={inviteForm.name}
            onChange={(e) => setInviteForm((f) => ({ ...f, name: e.target.value }))}
            fullWidth size="small" />
          <TextField label="Email" type="email" value={inviteForm.email}
            onChange={(e) => setInviteForm((f) => ({ ...f, email: e.target.value }))}
            fullWidth size="small" />
          <TextField label="Password" type="password" value={inviteForm.password}
            onChange={(e) => setInviteForm((f) => ({ ...f, password: e.target.value }))}
            fullWidth size="small" />
          <FormControl fullWidth size="small">
            <InputLabel>Role</InputLabel>
            <Select label="Role" value={inviteForm.role}
              onChange={(e) => setInviteForm((f) => ({ ...f, role: e.target.value as Role }))}>
              <MenuItem value="user">User</MenuItem>
              <MenuItem value="reviewer">Reviewer</MenuItem>
              <MenuItem value="admin">Admin</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions sx={{ px: 3, py: 2 }}>
          <Button color="inherit" onClick={() => setInviteOpen(false)}>Cancel</Button>
          <Button variant="contained" onClick={() => void handleInvite()}
            disabled={inviting || !inviteForm.name || !inviteForm.email || !inviteForm.password}>
            {inviting ? 'Inviting…' : 'Invite'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Delete confirmation */}
      <Dialog
        open={deleteOpen}
        onClose={() => setDeleteOpen(false)}
        PaperProps={{ sx: { bgcolor: '#161b22', border: '1px solid #30363d', borderRadius: 2 } }}
      >
        <DialogTitle>Delete user?</DialogTitle>
        <DialogContent>
          <Typography variant="body2" color="text.secondary">
            Are you sure you want to delete this user? This action cannot be undone.
          </Typography>
          {deleteTarget && (
            <Typography variant="body2" sx={{ mt: 1, color: '#c9d1d9' }}>
              {deleteTarget.name} ({deleteTarget.email})
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
