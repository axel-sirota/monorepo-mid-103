package main

import (
	"context"
	"errors"
	"log"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/golang-migrate/migrate/v4"
	migratepg "github.com/golang-migrate/migrate/v4/database/postgres"
	_ "github.com/golang-migrate/migrate/v4/source/file"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"

	"github.com/example/notification-service/internal/config"
	"github.com/example/notification-service/internal/repository"
	"github.com/example/notification-service/internal/router"
	"github.com/example/notification-service/internal/service"
)

func main() {
	cfg, err := config.Load()
	if err != nil {
		log.Fatalf("config error: %v", err)
	}

	db, err := sqlx.Connect("postgres", cfg.DatabaseURL)
	if err != nil {
		log.Fatalf("db connect: %v", err)
	}
	defer db.Close()

	if err := migrateUp(); err != nil {
		log.Fatalf("migrations: %v", err)
	}

	sender := service.NewSMTPSender(cfg.SMTPHost, cfg.SMTPPort)
	repo := repository.NewNotificationLogRepository(db)
	notifier := service.NewNotifier(sender, repo, cfg.FromEmail)

	r := router.SetupRouter(router.Deps{Notifier: notifier})

	srv := &http.Server{
		Addr:              ":" + cfg.Port,
		Handler:           r,
		ReadHeaderTimeout: 5 * time.Second,
	}

	go func() {
		log.Printf("notification-service listening on :%s", cfg.Port)
		if err := srv.ListenAndServe(); err != nil && !errors.Is(err, http.ErrServerClosed) {
			log.Fatalf("listen: %v", err)
		}
	}()

	stop := make(chan os.Signal, 1)
	signal.Notify(stop, os.Interrupt, syscall.SIGTERM)
	<-stop
	log.Println("shutting down")

	ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
	defer cancel()
	if err := srv.Shutdown(ctx); err != nil {
		log.Printf("shutdown error: %v", err)
	}
}

// migrateUp uses the file source against the local migrations dir and the DATABASE_URL env.
func migrateUp() error {
	dbURL := os.Getenv("DATABASE_URL")
	if dbURL == "" {
		return errors.New("DATABASE_URL not set")
	}
	migrationsPath := os.Getenv("MIGRATIONS_PATH")
	if migrationsPath == "" {
		migrationsPath = "file:///app/migrations"
		if _, err := os.Stat("./migrations"); err == nil {
			migrationsPath = "file://./migrations"
		}
	}

	// Open a fresh *sql.DB for the migrator (it manages its own conn).
	conn, err := sqlx.Connect("postgres", dbURL)
	if err != nil {
		return err
	}
	defer conn.Close()

	driver, err := migratepg.WithInstance(conn.DB, &migratepg.Config{})
	if err != nil {
		return err
	}
	m, err := migrate.NewWithDatabaseInstance(migrationsPath, "postgres", driver)
	if err != nil {
		return err
	}
	if err := m.Up(); err != nil && !errors.Is(err, migrate.ErrNoChange) {
		return err
	}
	return nil
}
