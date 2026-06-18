import { useState, useEffect } from 'react';
import { Box, Card, CardContent, Typography, CircularProgress, Grid } from '@mui/material';
import { Article, People, FolderOpen, Today } from '@mui/icons-material';
import { startOfDay } from 'date-fns';
import client from '../../api/client';
import { PaginatedResponse, NewsItem, User, Category } from '../../types';
import { useAuth } from '../../contexts/AuthContext';

interface MetricCardProps {
  title: string;
  value: number | null;
  icon: React.ReactNode;
}

function MetricCard({ title, value, icon }: MetricCardProps) {
  return (
    <Card sx={{ bgcolor: '#161b22', border: '1px solid #30363d', borderRadius: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 1, fontSize: 13 }}>
              {title}
            </Typography>
            {value === null ? (
              <CircularProgress size={20} />
            ) : (
              <Typography variant="h4" sx={{ fontWeight: 700 }}>
                {value.toLocaleString()}
              </Typography>
            )}
          </Box>
          <Box sx={{ color: '#2d8eff', mt: 0.5 }}>{icon}</Box>
        </Box>
      </CardContent>
    </Card>
  );
}

export function AdminDashboard() {
  console.log('AdminDashboard mounted');
  const { user } = useAuth();
  const [totalNews, setTotalNews] = useState<number | null>(null);
  const [totalUsers, setTotalUsers] = useState<number | null>(null);
  const [totalCategories, setTotalCategories] = useState<number | null>(null);
  const [newsToday, setNewsToday] = useState<number | null>(null);

  useEffect(() => {
    client
      .get<PaginatedResponse<NewsItem>>('/news', { params: { limit: 1, page: 1 } })
      .then(({ data }) => setTotalNews(data.total))
      .catch(() => setTotalNews(0));

    const todayStart = startOfDay(new Date()).toISOString();
    client
      .get<PaginatedResponse<NewsItem>>('/news', {
        params: { limit: 1, page: 1, date_from: todayStart, date_to: new Date().toISOString() },
      })
      .then(({ data }) => setNewsToday(data.total))
      .catch(() => setNewsToday(0));

    client
      .get<Category[]>('/preferences')
      .then(({ data }) => setTotalCategories(data.length))
      .catch(() => setTotalCategories(0));

    // GET /users now returns PaginatedResponse — use data.total
    if (user?.role === 'admin' || user?.role === 'root') {
      client
        .get<PaginatedResponse<User>>('/users', { params: { limit: 1, page: 1 } })
        .then(({ data }) => setTotalUsers(data.total))
        .catch(() => setTotalUsers(0));
    }
  }, [user?.role]);

  return (
    <Box>
      <Typography variant="h5" sx={{ fontWeight: 700, mb: 3 }}>
        Dashboard
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Total articles" value={totalNews} icon={<Article />} />
        </Grid>
        {(user?.role === 'admin' || user?.role === 'root') && (
          <Grid item xs={12} sm={6} md={3}>
            <MetricCard title="Total users" value={totalUsers} icon={<People />} />
          </Grid>
        )}
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="Categories" value={totalCategories} icon={<FolderOpen />} />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard title="News today" value={newsToday} icon={<Today />} />
        </Grid>
      </Grid>
    </Box>
  );
}
