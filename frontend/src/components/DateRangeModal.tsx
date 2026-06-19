import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stack,
  TextField,
} from '@mui/material';

interface DateRangeModalProps {
  open: boolean;
  onClose: () => void;
  onApply: (date_from: string, date_to: string) => void;
}

const inputSx = {
  '& .MuiOutlinedInput-root': {
    bgcolor: '#161b22',
    '& fieldset': { borderColor: '#30363d' },
    '&:hover fieldset': { borderColor: '#2d8eff' },
    '&.Mui-focused fieldset': { borderColor: '#2d8eff' },
  },
  '& input': { colorScheme: 'dark' },
};

const MODAL_PAPER_SX = {
  maxWidth: 380,
  width: '100%',
  border: '1px solid #30363d',
  borderRadius: '12px',
};

export function DateRangeModal({ open, onClose, onApply }: DateRangeModalProps) {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');

  const handleApply = () => {
    if (!from || !to) return;
    onApply(
      new Date(`${from}T00:00:00`).toISOString(),
      new Date(`${to}T23:59:59`).toISOString(),
    );
    onClose();
  };

  const handleClose = () => {
    setFrom('');
    setTo('');
    onClose();
  };

  return (
    <Dialog open={open} onClose={handleClose} fullWidth PaperProps={{ sx: MODAL_PAPER_SX }}>
      <DialogTitle>Select date range</DialogTitle>

      <DialogContent>
        <Stack spacing={2} sx={{ mt: 0.5 }}>
          <TextField
            label="From"
            type="date"
            value={from}
            onChange={(e) => setFrom(e.target.value)}
            inputProps={{ max: to || undefined }}
            size="small"
            fullWidth
            InputLabelProps={{ shrink: true }}
            sx={inputSx}
          />
          <TextField
            label="To"
            type="date"
            value={to}
            onChange={(e) => setTo(e.target.value)}
            inputProps={{ min: from || undefined }}
            size="small"
            fullWidth
            InputLabelProps={{ shrink: true }}
            sx={inputSx}
          />
        </Stack>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button color="inherit" onClick={handleClose}>Cancel</Button>
        <Button variant="contained" onClick={handleApply} disabled={!from || !to}>
          Apply
        </Button>
      </DialogActions>
    </Dialog>
  );
}
