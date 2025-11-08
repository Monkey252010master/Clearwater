import { useEffect, useState } from 'react';
import {
  Container,
  Paper,
  Typography,
  Grid as MuiGrid,
  Box,
  CircularProgress,
  Card,
  CardContent,
} from '@mui/material';
import { Theme } from '@mui/material/styles';
import { SxProps } from '@mui/system';

const Grid = MuiGrid as any; // Quick fix for TypeScript issues
import axios from 'axios';

interface ServerInfo {
  players: {
    username: string;
    // Add other player properties as needed
  }[];
}

const Home = () => {
  const [serverInfo, setServerInfo] = useState<ServerInfo | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchServerInfo = async () => {
      try {
        const response = await axios.get(`${import.meta.env.VITE_API_URL}/api/server-info`);
        setServerInfo(response.data);
        setError(null);
      } catch (err) {
        setError('Failed to fetch server information');
      } finally {
        setLoading(false);
      }
    };

    fetchServerInfo();
    // Refresh every 30 seconds
    const interval = setInterval(fetchServerInfo, 30000);
    return () => clearInterval(interval);
  }, []);

  const ServerStatus = () => (
    <Card sx={{ mb: 4, background: 'rgba(33, 150, 243, 0.1)' }}>
      <CardContent>
        <Grid container spacing={3} alignItems="center">
          <Grid item xs={12} md={4}>
            <Box textAlign="center">
              <Typography variant="h6" color="primary" gutterBottom>
                Players Online
              </Typography>
              <Typography variant="h2">
                {loading ? (
                  <CircularProgress />
                ) : error ? (
                  'N/A'
                ) : (
                  serverInfo?.players.length || 0
                )}
              </Typography>
            </Box>
          </Grid>
          <Grid item xs={12} md={8}>
            <Typography variant="h6" color="primary" gutterBottom>
              Active Players
            </Typography>
            {loading ? (
              <CircularProgress />
            ) : error ? (
              <Typography color="error">{error}</Typography>
            ) : (
              <Box sx={{ maxHeight: 200, overflow: 'auto' }}>
                {serverInfo?.players.map((player, index) => (
                  <Typography key={index} variant="body1">
                    {player.username}
                  </Typography>
                ))}
              </Box>
            )}
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );

  return (
    <Container maxWidth="lg" sx={{ mt: 4 }}>
      <Box textAlign="center" mb={4}>
        <Typography variant="h2" component="h1" gutterBottom>
          Welcome to Our ERLC Server
        </Typography>
        <Typography variant="h5" color="textSecondary" gutterBottom>
          Live Server Status
        </Typography>
      </Box>

      <ServerStatus />

      <Grid container spacing={4}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Join Our Team
            </Typography>
            <Typography variant="body1" paragraph>
              We're looking for dedicated staff members to help maintain order and
              ensure a great experience for all players. Apply today to become part
              of our team!
            </Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h5" gutterBottom>
              Server Rules
            </Typography>
            <Typography variant="body1" paragraph>
              • Respect all players and staff
              • No exploiting or hacking
              • Follow ERLC guidelines
              • Listen to staff instructions
              • Report issues to staff
            </Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};

export default Home;