import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Button,
  Typography,
  Alert,
  Box,
} from '@mui/material';
import { LockReset } from '@mui/icons-material';
import client from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';

export function ChangePasswordModal() {
  const { user, updateUser } = useAuth();
  const [password, setPassword] = useState('');
  const [confirm, setConfirm] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const isOpen = user?.must_change_password === true;

  useEffect(() => {
    if (!isOpen) return;
    setPassword('');
    setConfirm('');
    setError('');
  }, [isOpen]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    if (password.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (password !== confirm) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    try {
      await client.put('/users/me/password', { password });
      updateUser({ ...user!, must_change_password: false });
    } catch {
      setError('Failed to change password. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog
      open={isOpen}
      disableEscapeKeyDown
      onClose={() => { /* non-dismissable */ }}
      maxWidth="xs"
      fullWidth
      PaperProps={{
        sx: { border: '1px solid #30363d', borderRadius: '12px' },
      }}
    >
      <DialogTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
        <LockReset color="warning" />
        Change your password
      </DialogTitle>

      <DialogContent>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 2.5 }}>
          For security, you must set a new password before continuing.
          This temporary password cannot be used again.
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <Box
          component="form"
          id="change-pw-form"
          onSubmit={(e) => void handleSubmit(e)}
          noValidate
        >
          <TextField
            label="New password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            fullWidth
            required
            size="small"
            autoComplete="new-password"
            sx={{ mb: 2 }}
          />
          <TextField
            label="Confirm password"
            type="password"
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            fullWidth
            required
            size="small"
            autoComplete="new-password"
          />
        </Box>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button
          type="submit"
          form="change-pw-form"
          variant="contained"
          fullWidth
          disabled={loading || !password || !confirm}
        >
          {loading ? 'Saving…' : 'Save new password'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
