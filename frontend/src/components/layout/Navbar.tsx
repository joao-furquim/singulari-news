import React, { useState } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Menu,
  MenuItem,
  IconButton,
  Divider,
  ListItemIcon,
  ListItemText,
  Box,
} from '@mui/material';
import { Person, Settings, Logout, AdminPanelSettings } from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { UserAvatar } from '../common/UserAvatar';

interface NavbarProps {
  onSignIn: () => void;
  onProfile: () => void;
  onPreferences: () => void;
}

export function Navbar({ onSignIn, onProfile, onPreferences }: NavbarProps) {
  const { user, isAuthenticated, logout } = useAuth();
  const navigate = useNavigate();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const open = Boolean(anchorEl);
  const handleOpen = (e: React.MouseEvent<HTMLElement>) =>
    setAnchorEl(e.currentTarget);
  const handleClose = () => setAnchorEl(null);

  const handleProfile = () => { handleClose(); onProfile(); };
  const handlePreferences = () => { handleClose(); onPreferences(); };
  const handleAdmin = () => { handleClose(); navigate('/admin'); };
  const handleSignOut = () => { handleClose(); logout(); navigate('/'); };

  const firstName = user?.name?.split(' ')[0];
  const isAdminOrReviewer =
    user?.role === 'admin' || user?.role === 'reviewer' || user?.role === 'root';

  return (
    <AppBar
      position="sticky"
      elevation={0}
      sx={{
        bgcolor: 'background.paper',
        borderBottom: '1px solid',
        borderColor: 'divider',
      }}
    >
      <Toolbar>
        {/* Logo */}
        <Typography
          variant="h6"
          sx={{ flexGrow: 1, fontWeight: 700, letterSpacing: '-0.5px' }}
        >
          <Box component="span" sx={{ color: 'text.primary' }}>
            Singulari
          </Box>
          <Box component="span" sx={{ color: 'primary.main' }}>
            {' '}News
          </Box>
        </Typography>

        {isAuthenticated ? (
          <>
            <Typography
              variant="body2"
              color="text.secondary"
              sx={{ mr: 1.5, display: { xs: 'none', sm: 'block' } }}
            >
              Hello, {firstName}
            </Typography>

            <IconButton onClick={handleOpen} size="small" sx={{ p: 0.5 }}>
              <UserAvatar name={user?.name ?? '?'} size={30} />
            </IconButton>

            <Menu
              anchorEl={anchorEl}
              open={open}
              onClose={handleClose}
              PaperProps={{ sx: { mt: 1, minWidth: 180 } }}
              transformOrigin={{ horizontal: 'right', vertical: 'top' }}
              anchorOrigin={{ horizontal: 'right', vertical: 'bottom' }}
            >
              <MenuItem onClick={handleProfile}>
                <ListItemIcon><Person fontSize="small" /></ListItemIcon>
                <ListItemText>My Profile</ListItemText>
              </MenuItem>
              <MenuItem onClick={handlePreferences}>
                <ListItemIcon><Settings fontSize="small" /></ListItemIcon>
                <ListItemText>Preferences</ListItemText>
              </MenuItem>
              {isAdminOrReviewer && (
                <MenuItem onClick={handleAdmin}>
                  <ListItemIcon><AdminPanelSettings fontSize="small" /></ListItemIcon>
                  <ListItemText>Admin Panel</ListItemText>
                </MenuItem>
              )}
              <Divider />
              <MenuItem onClick={handleSignOut}>
                <ListItemIcon><Logout fontSize="small" /></ListItemIcon>
                <ListItemText>Sign out</ListItemText>
              </MenuItem>
            </Menu>
          </>
        ) : (
          <Button variant="contained" size="small" onClick={onSignIn}>
            Sign in
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}
