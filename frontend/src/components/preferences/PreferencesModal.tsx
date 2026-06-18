import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  List,
  ListItem,
  ListItemButton,
  ListItemText,
  Checkbox,
  Chip,
  Box,
  Button,
  Typography,
  CircularProgress,
  Stack,
  InputAdornment,
} from '@mui/material';
import { Search } from '@mui/icons-material';
import client from '../../api/client';
import { Category } from '../../types';
import { useAuth } from '../../contexts/AuthContext';

interface PreferencesModalProps {
  open: boolean;
  mode: 'onboarding' | 'edit';
  onClose: () => void;
}

const MODAL_PAPER_SX = {
  maxWidth: 480,
  width: '100%',
  border: '1px solid #30363d',
  borderRadius: '12px',
};

export function PreferencesModal({ open, mode, onClose }: PreferencesModalProps) {
  const { updatePreferences } = useAuth();
  const [categories, setCategories] = useState<Category[]>([]);
  const [selected, setSelected] = useState<string[]>([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (!open) return;
    setSearch('');
    setLoading(true);
    // Always fetch fresh data from API — never use stale context cache
    Promise.all([
      client.get<Category[]>('/preferences'),
      client.get<string[]>('/users/me/preferences').catch(() => ({ data: [] as string[] })),
    ])
      .then(([catsRes, prefsRes]) => {
        setCategories(catsRes.data);
        setSelected(prefsRes.data);
      })
      .catch(() => undefined)
      .finally(() => setLoading(false));
  }, [open]);

  const filtered = categories.filter((cat) =>
    cat.name.toLowerCase().includes(search.toLowerCase()),
  );

  const toggle = (id: string) =>
    setSelected((prev) =>
      prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id],
    );

  const handleSave = async () => {
    setSaving(true);
    try {
      const payload = { category_ids: selected };
      console.log('[preferences] PUT /users/me/preferences', payload);
      await client.put('/users/me/preferences', payload);
      updatePreferences(selected);
      onClose();
    } finally {
      setSaving(false);
    }
  };

  const title =
    mode === 'onboarding'
      ? 'What topics do you want to follow?'
      : 'Edit preferences';

  return (
    <Dialog open={open} onClose={onClose} fullWidth PaperProps={{ sx: MODAL_PAPER_SX }}>
      <DialogTitle>
        {title}
        <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5, fontWeight: 400 }}>
          Select the categories you're interested in.
        </Typography>
      </DialogTitle>

      <DialogContent sx={{ pb: 0 }}>
        <TextField
          placeholder="Search categories…"
          value={search}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setSearch(e.target.value)}
          fullWidth size="small" sx={{ mb: 1.5 }}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <Search fontSize="small" />
              </InputAdornment>
            ),
          }}
        />

        {selected.length > 0 && (
          <Stack direction="row" sx={{ mb: 1.5, flexWrap: 'wrap', gap: 0.5 }}>
            {selected.map((id) => {
              const cat = categories.find((c) => c.id === id);
              return cat ? (
                <Chip
                  key={id}
                  label={cat.name}
                  size="small"
                  color="primary"
                  onDelete={() => toggle(id)}
                />
              ) : null;
            })}
          </Stack>
        )}

        {loading ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
            <CircularProgress size={32} />
          </Box>
        ) : (
          <List dense disablePadding sx={{ maxHeight: 300, overflow: 'auto' }}>
            {filtered.map((cat) => (
              <ListItem key={cat.id} disablePadding>
                <ListItemButton onClick={() => toggle(cat.id)} sx={{ borderRadius: 1 }}>
                  <Checkbox
                    checked={selected.includes(cat.id)}
                    size="small"
                    edge="start"
                    disableRipple
                    tabIndex={-1}
                  />
                  <ListItemText primary={cat.name} secondary={cat.description} />
                </ListItemButton>
              </ListItem>
            ))}
          </List>
        )}
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        {mode === 'onboarding' && (
          <Button color="inherit" onClick={onClose}>
            Skip for now
          </Button>
        )}
        <Box sx={{ flex: 1 }} />
        {mode === 'edit' && (
          <Button color="inherit" onClick={onClose}>
            Cancel
          </Button>
        )}
        <Button
          variant="contained"
          onClick={() => void handleSave()}
          disabled={saving || selected.length === 0}
        >
          {saving ? 'Saving…' : 'Save preferences'}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
