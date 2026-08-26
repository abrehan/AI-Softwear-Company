import React, { useEffect, useState } from "react";
import {
  Card,
  CardContent,
  FormControlLabel,
  Switch,
  Typography,
} from "@mui/material";

const SETTINGS_KEY = "ai_software_company_settings";

const Settings: React.FC = () => {
  const [compactMode, setCompactMode] = useState(false);
  const [notifications, setNotifications] = useState(true);

  useEffect(() => {
    const saved = localStorage.getItem(SETTINGS_KEY);

    if (!saved) {
      return;
    }

    try {
      const parsed = JSON.parse(saved);
      setCompactMode(Boolean(parsed.compactMode));
      setNotifications(parsed.notifications !== false);
    } catch {
      // Ignore malformed local settings.
    }
  }, []);

  useEffect(() => {
    localStorage.setItem(
      SETTINGS_KEY,
      JSON.stringify({
        compactMode,
        notifications,
      })
    );
  }, [compactMode, notifications]);

  return (
    <>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      <Typography color="text.secondary" sx={{ mb: 3 }}>
        Manage your Virtual Office preferences.
      </Typography>

      <Card>
        <CardContent>
          <FormControlLabel
            control={
              <Switch
                checked={notifications}
                onChange={(e) => setNotifications(e.target.checked)}
              />
            }
            label="Enable notifications"
          />

          <br />

          <FormControlLabel
            control={
              <Switch
                checked={compactMode}
                onChange={(e) => setCompactMode(e.target.checked)}
              />
            }
            label="Compact dashboard mode"
          />
        </CardContent>
      </Card>
    </>
  );
};

export default Settings;