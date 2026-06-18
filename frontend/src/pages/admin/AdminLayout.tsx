import { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';
import {
  Box,
  List,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Typography,
  Divider,
  Button,
} from '@mui/material';
import { Dashboard, Article, People, ArrowBack } from '@mui/icons-material';
import { useAuth } from '../../contexts/AuthContext';
import { Navbar } from '../../components/layout/Navbar';
import { ProfileModal } from '../../components/profile/ProfileModal';
import { PreferencesModal } from '../../components/preferences/PreferencesModal';

const SIDEBAR_WIDTH = 220;

interface NavItemProps {
  to: string;
  exact?: boolean;
  icon: React.ReactNode;
  label: string;
}

function NavItem({ to, exact = false, icon, label }: NavItemProps) {
  const location = useLocation();
  const active = exact ? location.pathname === to : location.pathname.startsWith(to);

  return (
    <Link to={to} style={{ textDecoration: 'none', display: 'block' }}>
      <ListItemButton
        selected={active}
        sx={{
          px: 2,
          py: 1,
          color: active ? '#2d8eff' : '#8b949e',
          '&.Mui-selected': { bgcolor: 'rgba(45,142,255,0.08)', color: '#2d8eff' },
          '&:hover': { bgcolor: 'rgba(255,255,255,0.04)' },
          '& .MuiListItemIcon-root': { color: 'inherit', minWidth: 32 },
        }}
      >
        <ListItemIcon>{icon}</ListItemIcon>
        <ListItemText primary={label} primaryTypographyProps={{ fontSize: 14 }} />
      </ListItemButton>
    </Link>
  );
}

export function AdminLayout() {
  const { user } = useAuth();
  const [profileOpen, setProfileOpen] = useState(false);
  const [prefOpen, setPrefOpen] = useState(false);

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100vh', bgcolor: '#0d1117' }}>
      {/* Top navbar — same as feed */}
      <Navbar
        onSignIn={() => {}}
        onProfile={() => setProfileOpen(true)}
        onPreferences={() => setPrefOpen(true)}
      />

      {/* Sidebar + content */}
      <Box sx={{ display: 'flex', flex: 1, overflow: 'hidden' }}>
        {/* Sidebar */}
        <Box
          sx={{
            width: SIDEBAR_WIDTH,
            flexShrink: 0,
            bgcolor: '#161b22',
            borderRight: '1px solid #30363d',
            overflowY: 'auto',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Box sx={{ px: 2, pt: 2, pb: 1 }}>
            <Button
              component={Link}
              to="/"
              startIcon={<ArrowBack sx={{ fontSize: '14px !important' }} />}
              size="small"
              sx={{
                color: '#8b949e',
                fontSize: 12,
                textTransform: 'none',
                p: 0,
                minWidth: 0,
                '&:hover': { color: '#e6edf3', bgcolor: 'transparent' },
              }}
            >
              Back to News
            </Button>
          </Box>
          <Divider sx={{ borderColor: '#30363d', mb: 1 }} />
          <Box sx={{ px: 2, py: 1 }}>
            <Typography
              variant="overline"
              sx={{ color: '#484f58', fontSize: 10, fontWeight: 700, letterSpacing: '0.1em' }}
            >
              Admin Panel
            </Typography>
          </Box>
          <List dense disablePadding>
            <NavItem to="/admin" exact icon={<Dashboard fontSize="small" />} label="Dashboard" />
            <NavItem to="/admin/news" icon={<Article fontSize="small" />} label="News Management" />
            {user?.role === 'admin' && (
              <NavItem to="/admin/users" icon={<People fontSize="small" />} label="Users" />
            )}
          </List>
        </Box>

        {/* Main content */}
        <Box sx={{ flex: 1, overflowY: 'auto', p: 3 }}>
          <Outlet />
        </Box>
      </Box>

      <ProfileModal open={profileOpen} onClose={() => setProfileOpen(false)} />
      <PreferencesModal open={prefOpen} mode="edit" onClose={() => setPrefOpen(false)} />
    </Box>
  );
}
