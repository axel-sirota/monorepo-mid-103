package config

import (
	"errors"
	"os"
	"strconv"
)

// Config holds runtime configuration loaded from environment variables.
type Config struct {
	Port               string
	ModelServingURL    string
	APIKey             string
	RateLimitPerMinute int
	LogLevel           string
}

// Load reads configuration from environment variables.
func Load() (*Config, error) {
	cfg := &Config{
		Port:               getenv("PORT", "9000"),
		ModelServingURL:    os.Getenv("MODEL_SERVING_URL"),
		APIKey:             os.Getenv("API_KEY"),
		RateLimitPerMinute: 60,
		LogLevel:           getenv("LOG_LEVEL", "info"),
	}

	if cfg.ModelServingURL == "" {
		return nil, errors.New("MODEL_SERVING_URL is required")
	}
	if cfg.APIKey == "" {
		return nil, errors.New("API_KEY is required")
	}

	if v := os.Getenv("RATE_LIMIT_PER_MINUTE"); v != "" {
		parsed, err := strconv.Atoi(v)
		if err != nil || parsed <= 0 {
			return nil, errors.New("RATE_LIMIT_PER_MINUTE must be a positive integer")
		}
		cfg.RateLimitPerMinute = parsed
	}

	return cfg, nil
}

func getenv(k, fallback string) string {
	if v := os.Getenv(k); v != "" {
		return v
	}
	return fallback
}
