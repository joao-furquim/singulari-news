import React, { useState, useEffect, useRef } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Box,
  Avatar,
  IconButton,
  Alert,
  Stack,
  CircularProgress,
} from '@mui/material';
import { CameraAlt, Close } from '@mui/icons-material';
import client from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { User } from '../../types';

interface ProfileModalProps {
  open: boolean;
  onClose: () => void;
}

const MODAL_PAPER_SX = {
  maxWidth: 480,
  width: '100%',
  border: '1px solid #30363d',
  borderRadius: '12px',
};

export function ProfileModal({ open, onClose }: ProfileModalProps) {
  const { updateUser } = useAuth();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [error, setError] = useState('');
  const [fetching, setFetching] = useState(false);
  const [saving, setSaving] = useState(false);
  const [uploading, setUploading] = useState(false);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // Always fetch fresh user data from the API when modal opens
  useEffect(() => {
    if (!open) return;
    setError('');
    setFetching(true);
    client.get<User>('/users/me')
      .then(({ data }) => {
        setName(data.name);
        setEmail(data.email ?? '');
        setAvatarUrl(data.avatar_url);
      })
      .catch(() => setError('Failed to load profile.'))
      .finally(() => setFetching(false));
  }, [open]);

  const initials = name
    .split(' ')
    .map((w) => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2) || '?';

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);
    setUploading(true);
    setError('');
    try {
      const { data } = await client.post<User>('/users/me/avatar', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setAvatarUrl(data.avatar_url);
      updateUser(data);
    } catch {
      setError('Failed to upload avatar.');
    } finally {
      setUploading(false);
    }
  };

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
            {/* Avatar with camera overlay */}
            <Box sx={{ display: 'flex', justifyContent: 'center', mb: 3 }}>
              <Box sx={{ position: 'relative' }}>
                <Avatar
                  src={avatarUrl ?? undefined}
                  sx={{
                    width: 96,
                    height: 96,
                    fontSize: 32,
                    fontWeight: 700,
                    background: 'linear-gradient(135deg, #1a4a8a 0%, #2d8eff 100%)',
                  }}
                >
                  {!avatarUrl && initials}
                </Avatar>
                <IconButton
                  size="small"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={uploading}
                  sx={{
                    position: 'absolute',
                    bottom: 0,
                    right: 0,
                    bgcolor: 'background.paper',
                    border: '2px solid',
                    borderColor: 'divider',
                    '&:hover': { bgcolor: 'background.default' },
                  }}
                >
                  {uploading ? (
                    <CircularProgress size={14} />
                  ) : (
                    <CameraAlt sx={{ fontSize: 16 }} />
                  )}
                </IconButton>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  hidden
                  onChange={(e) => void handleFileChange(e)}
                />
              </Box>
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
          disabled={saving || fetching}
        >
          {saving ? 'Saving…' : 'Save changes'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
