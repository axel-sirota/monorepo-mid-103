package config

import (
	"fmt"
	"os"
)

// Config holds all runtime configuration loaded from env.
type Config struct {
	DatabaseURL string
	SMTPHost    string
	SMTPPort    string
	FromEmail   string
	LogLevel    string
	Port        string
}

// Load reads env vars and returns Config or an error if required vars are missing.
func Load() (*Config, error) {
	cfg := &Config{
		DatabaseURL: os.Getenv("DATABASE_URL"),
		SMTPHost:    os.Getenv("SMTP_HOST"),
		SMTPPort:    os.Getenv("SMTP_PORT"),
		FromEmail:   os.Getenv("FROM_EMAIL"),
		LogLevel:    getOrDefault("LOG_LEVEL", "info"),
		Port:        getOrDefault("PORT", "8002"),
	}

	var missing []string
	if cfg.DatabaseURL == "" {
		missing = append(missing, "DATABASE_URL")
	}
	if cfg.SMTPHost == "" {
		missing = append(missing, "SMTP_HOST")
	}
	if cfg.SMTPPort == "" {
		missing = append(missing, "SMTP_PORT")
	}
	if cfg.FromEmail == "" {
		missing = append(missing, "FROM_EMAIL")
	}
	if len(missing) > 0 {
		return nil, fmt.Errorf("missing required env vars: %v", missing)
	}
	return cfg, nil
}

func getOrDefault(key, def string) string {
	if v := os.Getenv(key); v != "" {
		return v
	}
	return def
}
