import { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  IconButton,
  Alert,
  Stack,
  CircularProgress,
} from '@mui/material';
import { Close } from '@mui/icons-material';
import client from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { UserAvatar } from '../common/UserAvatar';
import { User } from '../../types';

interface ProfileModalProps {
  open: boolean;
  onClose: () => void;
}

const MODAL_PAPER_SX = {
  maxWidth: 420,
  width: '100%',
  border: '1px solid #30363d',
  borderRadius: '12px',
};

export function ProfileModal({ open, onClose }: ProfileModalProps) {
  const { updateUser } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [fetching, setFetching] = useState(false);
  const [saving, setSaving] = useState(false);

  // Always fetch fresh data from the API when the modal opens
  useEffect(() => {
    if (!open) return;
    setError('');
    setFetching(true);
    client
      .get<User>('/users/me')
      .then(({ data }) => {
        setName(data.name);
        setEmail(data.email ?? '');
      })
      .catch(() => setError('Failed to load profile.'))
      .finally(() => setFetching(false));
  }, [open]);

  const handleSave = async () => {
    setSaving(true);
    setError('');
    try {
      const { data } = await client.put<User>('/users/me', { name, email });
      updateUser(data);
      onClose();
    } catch {
      setError('Failed to update profile.');
    } finally {
      setSaving(false);
    }
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth PaperProps={{ sx: MODAL_PAPER_SX }}>
      <DialogTitle>
        My profile
        <IconButton
          onClick={onClose}
          size="small"
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        {fetching ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={32} />
          </Box>
        ) : (
          <>
            {/* Dynamic initials avatar — updates automatically when name changes */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
              <UserAvatar name={name || '?'} size={72} />
            </Box>

            <Stack spacing={2}>
              <TextField
                label="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                fullWidth
                size="small"
              />
              <TextField
                label="Email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                fullWidth
                size="small"
              />
            </Stack>
          </>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button color="inherit" onClick={onClose}>Cancel</Button>
        <Button
          variant="contained"
          onClick={() => void handleSave()}
          disabled={saving || fetching || !name}
        >
          {saving ? 'Saving…' : 'Save changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
