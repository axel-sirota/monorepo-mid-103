package main

import (
	"log"

	"github.com/gin-gonic/gin"

	"github.com/example/inference-gateway/internal/client"
	"github.com/example/inference-gateway/internal/config"
	"github.com/example/inference-gateway/internal/router"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("config: %v", err)
	}

	if cfg.LogLevel != "debug" {
		gin.SetMode(gin.ReleaseMode)
	}

	upstream := client.New(cfg.ModelServingURL)

	r := router.SetupRouter(router.Deps{
		APIKey:             cfg.APIKey,
		RateLimitPerMinute: cfg.RateLimitPerMinute,
		Upstream:           upstream,
	})

	log.Printf("inference-gateway listening on :%s -> %s", cfg.Port, cfg.ModelServingURL)
	if err := r.Run(":" + cfg.Port); err != nil {
		log.Fatalf("server: %v", err)
	}
}
