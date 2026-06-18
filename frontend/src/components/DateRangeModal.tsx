import { useState } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Stack,
} from '@mui/material';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';
import { format } from 'date-fns';

interface DateRangeModalProps {
  open: boolean;
  onClose: () => void;
  onApply: (date_from: string, date_to: string) => void;
}

const toISO = (d: Date) => format(d, "yyyy-MM-dd'T'HH:mm:ss");

const MODAL_PAPER_SX = {
  maxWidth: 480,
  width: '100%',
  border: '1px solid #30363d',
  borderRadius: '12px',
};

export function DateRangeModal({ open, onClose, onApply }: DateRangeModalProps) {
  const [from, setFrom] = useState<Date | null>(null);
  const [to, setTo] = useState<Date | null>(null);

  const handleApply = () => {
    if (!from || !to) return;
    onApply(toISO(from), toISO(to));
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} fullWidth PaperProps={{ sx: MODAL_PAPER_SX }}>
      <DialogTitle>Select date range</DialogTitle>

      <DialogContent>
        <Stack spacing={2} sx={{ mt: 0.5 }}>
          <DatePicker
            label="From"
            value={from}
            onChange={(v) => setFrom(v)}
            maxDate={to ?? undefined}
            slotProps={{ textField: { size: 'small', fullWidth: true } }}
          />
          <DatePicker
            label="To"
            value={to}
            onChange={(v) => setTo(v)}
            minDate={from ?? undefined}
            slotProps={{ textField: { size: 'small', fullWidth: true } }}
          />
        </Stack>
      </DialogContent>

      <DialogActions sx={{ px: 3, py: 2 }}>
        <Button color="inherit" onClick={onClose}>Cancel</Button>
        <Button variant="contained" onClick={handleApply} disabled={!from || !to}>
          Apply
        </Button>
      </DialogActions>
    </Dialog>
  );
}
