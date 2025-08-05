import React, { useState, useEffect } from 'react';
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  IconButton,
  Badge,
  Menu,
  MenuItem,
  Box,
  Avatar,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  AccountCircle,
  Dashboard,
  Email,
  Event,
  Settings,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import authService from '../services/authService';
import alertService from '../services/alertService';
import { User } from '../types';

const Navbar: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [notificationCount, setNotificationCount] = useState(0);
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    // Load user data
    authService.getCurrentUser().then(setUser).catch(console.error);
    
    // Load notification count
    alertService.getUnreadAlerts()
      .then(alerts => setNotificationCount(alerts.length))
      .catch(console.error);
  }, []);

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    authService.logout();
    handleClose();
  };

  const navigationItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <Dashboard /> },
    { path: '/emails', label: 'Emails', icon: <Email /> },
    { path: '/calendar', label: 'Calendar', icon: <Event /> },
    { path: '/alerts', label: 'Alerts', icon: <NotificationsIcon /> },
    { path: '/settings', label: 'Settings', icon: <Settings /> },
  ];

  return (
    <AppBar position="static" elevation={1}>
      <Toolbar>
        <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
          Secretary AI
        </Typography>

        <Box sx={{ display: 'flex', gap: 1, mr: 2 }}>
          {navigationItems.map((item) => (
            <Button
              key={item.path}
              color={location.pathname === item.path ? 'secondary' : 'inherit'}
              startIcon={item.icon}
              onClick={() => navigate(item.path)}
              sx={{ 
                textTransform: 'none',
                borderRadius: 2,
                backgroundColor: location.pathname === item.path ? 'rgba(255,255,255,0.1)' : 'transparent'
              }}
            >
              {item.label}
            </Button>
          ))}
        </Box>

        <IconButton
          color="inherit"
          onClick={() => navigate('/alerts')}
          sx={{ mr: 1 }}
        >
          <Badge badgeContent={notificationCount} color="error">
            <NotificationsIcon />
          </Badge>
        </IconButton>

        <IconButton
          size="large"
          aria-label="account of current user"
          aria-controls="menu-appbar"
          aria-haspopup="true"
          onClick={handleMenu}
          color="inherit"
        >
          <Avatar sx={{ width: 32, height: 32, bgcolor: 'secondary.main' }}>
            {user?.full_name?.charAt(0) || 'U'}
          </Avatar>
        </IconButton>

        <Menu
          id="menu-appbar"
          anchorEl={anchorEl}
          anchorOrigin={{
            vertical: 'bottom',
            horizontal: 'right',
          }}
          keepMounted
          transformOrigin={{
            vertical: 'top',
            horizontal: 'right',
          }}
          open={Boolean(anchorEl)}
          onClose={handleClose}
        >
          <MenuItem onClick={() => { navigate('/settings'); handleClose(); }}>
            Profile Settings
          </MenuItem>
          <MenuItem onClick={handleLogout}>Logout</MenuItem>
        </Menu>
      </Toolbar>
    </AppBar>
  );
};

export default Navbar;