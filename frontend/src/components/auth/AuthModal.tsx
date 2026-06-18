import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  Tabs,
  Tab,
  Box,
  TextField,
  Button,
  Typography,
  Alert,
  IconButton,
} from '@mui/material';
import { Close, ArrowBack } from '@mui/icons-material';
import client from '../../api/client';
import { useAuth } from '../../contexts/AuthContext';
import { LoginResponse } from '../../types';

interface AuthModalProps {
  open: boolean;
  initialTab?: number;
  onClose: () => void;
  onSignUpSuccess: () => void;
}

type AuthView = 'main' | 'forgot';

const MODAL_PAPER_SX = {
  maxWidth: 480,
  width: '100%',
  border: '1px solid #30363d',
  borderRadius: '12px',
};

async function fetchPreferencesAfterLogin(token: string): Promise<string[]> {
  localStorage.setItem('token', token);
  try {
    const { data } = await client.get<string[]>('/users/me/preferences');
    return data;
  } catch {
    return [];
  }
}

export function AuthModal({
  open,
  initialTab = 0,
  onClose,
  onSignUpSuccess,
}: AuthModalProps) {
  const { login, pendingAction, setPendingAction } = useAuth();

  const [view, setView] = useState<AuthView>('main');
  const [tab, setTab] = useState(initialTab);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [successMsg, setSuccessMsg] = useState('');

  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');

  const [regName, setRegName] = useState('');
  const [regEmail, setRegEmail] = useState('');
  const [regPassword, setRegPassword] = useState('');

  const [forgotEmail, setForgotEmail] = useState('');

  useEffect(() => {
    if (open) {
      setView('main');
      setTab(initialTab);
      setError('');
      setSuccessMsg('');
      setLoginEmail('');
      setLoginPassword('');
      setRegName('');
      setRegEmail('');
      setRegPassword('');
      setForgotEmail('');
    }
  }, [open, initialTab]);

  const resetMessages = () => { setError(''); setSuccessMsg(''); };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();
    setLoading(true);
    try {
      const { data } = await client.post<LoginResponse>('/login', {
        email: loginEmail,
        password: loginPassword,
      });
      const prefs = await fetchPreferencesAfterLogin(data.access_token);
      login(data.access_token, data.user, prefs);
      if (pendingAction) { pendingAction(); setPendingAction(null); }
      onClose();
    } catch {
      localStorage.removeItem('token');
      setError('Invalid email or password.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();
    setLoading(true);
    try {
      await client.post('/users', {
        name: regName,
        email: regEmail,
        password: regPassword,
      });
      const { data } = await client.post<LoginResponse>('/login', {
        email: regEmail,
        password: regPassword,
      });
      const prefs = await fetchPreferencesAfterLogin(data.access_token);
      login(data.access_token, data.user, prefs);
      onClose();
      onSignUpSuccess();
    } catch {
      localStorage.removeItem('token');
      setError('Registration failed. Email may already be in use.');
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    resetMessages();
    setLoading(true);
    try {
      await client.post('/auth/forgot-password', { email: forgotEmail });
      setSuccessMsg('If this email is registered, a reset link has been sent.');
    } catch {
      setError('Something went wrong. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const goToForgot = () => { resetMessages(); setView('forgot'); };
  const goToMain = () => { resetMessages(); setView('main'); };

  return (
    <Dialog open={open} onClose={onClose} fullWidth PaperProps={{ sx: MODAL_PAPER_SX }}>
      <DialogTitle sx={{ pb: 0 }}>
        {view === 'forgot' ? 'Reset password' : 'Welcome to Singulari'}
        <IconButton
          onClick={onClose}
          size="small"
          sx={{ position: 'absolute', right: 8, top: 8 }}
        >
          <Close />
        </IconButton>
      </DialogTitle>

      <DialogContent sx={{ pt: 1 }}>
        {/* ─── Main view (Sign in / Create account) ─── */}
        {view === 'main' && (
          <>
            <Tabs
              value={tab}
              onChange={(_, v: number) => {
              setTab(v);
              resetMessages();
              setLoginEmail('');
              setLoginPassword('');
              setRegName('');
              setRegEmail('');
              setRegPassword('');
            }}
              sx={{ mb: 2 }}
            >
              <Tab label="Sign in" />
              <Tab label="Create account" />
            </Tabs>

            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

            {/* Sign in form */}
            {tab === 0 && (
              <Box component="form" onSubmit={(e) => void handleLogin(e)} noValidate>
                <TextField
                  label="Email"
                  type="email"
                  value={loginEmail}
                  onChange={(e) => setLoginEmail(e.target.value)}
                  fullWidth required size="small" autoComplete="email"
                  sx={{ mb: 2 }}
                />
                <TextField
                  label="Password"
                  type="password"
                  value={loginPassword}
                  onChange={(e) => setLoginPassword(e.target.value)}
                  fullWidth required size="small" autoComplete="current-password"
                  sx={{ mb: 2 }}
                />
                <Button type="submit" variant="contained" fullWidth disabled={loading}>
                  {loading ? 'Signing in…' : 'Sign in'}
                </Button>
                <Typography
                  variant="body2"
                  onClick={goToForgot}
                  sx={{
                    mt: 1.5,
                    textAlign: 'right',
                    color: 'primary.main',
                    cursor: 'pointer',
                    fontSize: 13,
                    '&:hover': { textDecoration: 'underline' },
                  }}
                >
                  Forgot your password?
                </Typography>
              </Box>
            )}

            {/* Create account form */}
            {tab === 1 && (
              <Box component="form" onSubmit={(e) => void handleRegister(e)} noValidate>
                <TextField
                  label="Full name"
                  value={regName}
                  onChange={(e) => setRegName(e.target.value)}
                  fullWidth required size="small"
                  sx={{ mb: 2 }}
                />
                <TextField
                  label="Email"
                  type="email"
                  value={regEmail}
                  onChange={(e) => setRegEmail(e.target.value)}
                  fullWidth required size="small" autoComplete="email"
                  sx={{ mb: 2 }}
                />
                <TextField
                  label="Password"
                  type="password"
                  value={regPassword}
                  onChange={(e) => setRegPassword(e.target.value)}
                  fullWidth required size="small" autoComplete="new-password"
                  sx={{ mb: 2 }}
                />
                <Button type="submit" variant="contained" fullWidth disabled={loading}>
                  {loading ? 'Creating account…' : 'Create account'}
                </Button>
              </Box>
            )}
          </>
        )}

        {/* ─── Forgot password view ─── */}
        {view === 'forgot' && (
          <Box component="form" onSubmit={(e) => void handleForgotPassword(e)} noValidate>
            {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
            {successMsg && <Alert severity="success" sx={{ mb: 2 }}>{successMsg}</Alert>}

            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Enter your email and we'll send you a reset link.
            </Typography>
            <TextField
              label="Email"
              type="email"
              value={forgotEmail}
              onChange={(e) => setForgotEmail(e.target.value)}
              fullWidth required size="small"
              sx={{ mb: 2 }}
            />
            <Button type="submit" variant="contained" fullWidth disabled={loading}>
              {loading ? 'Sending…' : 'Send reset link'}
            </Button>
            <Button
              startIcon={<ArrowBack />}
              color="inherit"
              onClick={goToMain}
              sx={{ mt: 1.5, fontSize: 13 }}
            >
              Back to sign in
            </Button>
          </Box>
        )}
      </DialogContent>
    </Dialog>
  );
}
