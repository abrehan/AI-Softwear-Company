import React from "react";
import {
  Card,
  CardContent,
  Chip,
  Grid,
  Typography,
} from "@mui/material";
import { useAuth } from "../context/AuthContext";

const Profile: React.FC = () => {
  const { user } = useAuth();

  if (!user) {
    return null;
  }

  return (
    <Grid container spacing={3}>
      <Grid size={{ xs: 12 }}>
        <Typography variant="h4">Profile</Typography>
        <Typography color="text.secondary">
          Your authenticated account information.
        </Typography>
      </Grid>

      <Grid size={{ xs: 12, md: 6 }}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Account
            </Typography>

            <Typography><strong>Username:</strong> {user.username}</Typography>
            <Typography><strong>Email:</strong> {user.email}</Typography>
            <Typography><strong>User ID:</strong> {user.id}</Typography>
            <Typography sx={{ mt: 1 }}>
              <strong>Status:</strong>{" "}
              <Chip
                size="small"
                label={user.disabled ? "Disabled" : "Active"}
                color={user.disabled ? "default" : "success"}
              />
            </Typography>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};

export default Profile;