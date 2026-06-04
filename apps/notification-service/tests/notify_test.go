package tests

import (
	"context"
	"encoding/json"
	"errors"
	"fmt"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/jmoiron/sqlx"
	_ "github.com/lib/pq"
	"github.com/stretchr/testify/suite"
	"github.com/testcontainers/testcontainers-go"
	tcpostgres "github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"

	"github.com/example/notification-service/internal/repository"
	"github.com/example/notification-service/internal/router"
	"github.com/example/notification-service/internal/service"
)

// mockSender implements service.Sender. Returns the configured error (nil = success).
type mockSender struct {
	err  error
	last struct{ from, to, subject, body string }
}

func (m *mockSender) Send(from, to, subject, body string) error {
	m.last.from = from
	m.last.to = to
	m.last.subject = subject
	m.last.body = body
	return m.err
}

type NotifyTestSuite struct {
	suite.Suite
	pgContainer *tcpostgres.PostgresContainer
	db          *sqlx.DB
}

func (s *NotifyTestSuite) SetupSuite() {
	ctx := context.Background()

	c, err := tcpostgres.Run(ctx,
		"postgres:16-alpine",
		tcpostgres.WithDatabase("notifications_db"),
		tcpostgres.WithUsername("monorepo"),
		tcpostgres.WithPassword("monorepo"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(60*time.Second),
		),
	)
	if err != nil {
		s.T().Skipf("skipping: cannot start postgres testcontainer (likely no Docker): %v", err)
		return
	}
	s.pgContainer = c

	dsn, err := c.ConnectionString(ctx, "sslmode=disable")
	s.Require().NoError(err)

	db, err := sqlx.Connect("postgres", dsn)
	s.Require().NoError(err)
	s.db = db

	// Apply migration inline (instead of dragging in the migrate CLI for tests).
	schema := `
	CREATE TABLE notification_log (
		id         BIGSERIAL PRIMARY KEY,
		to_email   VARCHAR(320) NOT NULL,
		subject    VARCHAR(200) NOT NULL,
		body       TEXT NOT NULL,
		kind       VARCHAR(50) NOT NULL,
		user_id    BIGINT NULL,
		metadata   JSONB NULL,
		status     VARCHAR(20) NOT NULL,
		error      TEXT NULL,
		created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
	);`
	_, err = s.db.Exec(schema)
	s.Require().NoError(err)
}

func (s *NotifyTestSuite) TearDownSuite() {
	if s.db != nil {
		_ = s.db.Close()
	}
	if s.pgContainer != nil {
		_ = s.pgContainer.Terminate(context.Background())
	}
}

func (s *NotifyTestSuite) SetupTest() {
	if s.db != nil {
		_, _ = s.db.Exec("TRUNCATE notification_log RESTART IDENTITY")
	}
}

func (s *NotifyTestSuite) newRouter(sender service.Sender) *gin.Engine {
	gin.SetMode(gin.TestMode)
	repo := repository.NewNotificationLogRepository(s.db)
	notifier := service.NewNotifier(sender, repo, "noreply@example.com")
	return router.SetupRouter(router.Deps{Notifier: notifier})
}

func (s *NotifyTestSuite) doPost(r *gin.Engine, payload string) *httptest.ResponseRecorder {
	req := httptest.NewRequest(http.MethodPost, "/notify", strings.NewReader(payload))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	r.ServeHTTP(w, req)
	return w
}

func (s *NotifyTestSuite) TestHappyPath() {
	sender := &mockSender{err: nil}
	r := s.newRouter(sender)

	payload := `{
		"to_email": "ada@example.com",
		"subject": "Hi",
		"body": "Hello there",
		"kind": "welcome",
		"user_id": 42,
		"metadata": {"src": "test"}
	}`

	w := s.doPost(r, payload)
	s.Require().Equal(http.StatusAccepted, w.Code, "body=%s", w.Body.String())

	var resp map[string]any
	s.Require().NoError(json.Unmarshal(w.Body.Bytes(), &resp))
	s.NotZero(resp["id"])

	var status string
	err := s.db.Get(&status, "SELECT status FROM notification_log WHERE to_email=$1", "ada@example.com")
	s.Require().NoError(err)
	s.Equal("sent", status)
	s.Equal("ada@example.com", sender.last.to)
}

func (s *NotifyTestSuite) TestSMTPFailure() {
	sender := &mockSender{err: errors.New("connection refused")}
	r := s.newRouter(sender)

	payload := `{
		"to_email": "bob@example.com",
		"subject": "Hi",
		"body": "Body",
		"kind": "weekly_digest"
	}`

	w := s.doPost(r, payload)
	s.Require().Equal(http.StatusBadGateway, w.Code, "body=%s", w.Body.String())

	var row struct {
		Status string
		Error  string
	}
	err := s.db.QueryRow("SELECT status, error FROM notification_log WHERE to_email=$1", "bob@example.com").
		Scan(&row.Status, &row.Error)
	s.Require().NoError(err)
	s.Equal("failed", row.Status)
	s.Contains(row.Error, "connection refused")
}

func (s *NotifyTestSuite) TestValidation_MissingToEmail() {
	sender := &mockSender{}
	r := s.newRouter(sender)

	payload := `{"subject":"x","body":"y","kind":"welcome"}`
	w := s.doPost(r, payload)
	s.Equal(http.StatusBadRequest, w.Code)
}

func (s *NotifyTestSuite) TestValidation_InvalidKind() {
	sender := &mockSender{}
	r := s.newRouter(sender)

	payload := fmt.Sprintf(`{"to_email":"a@b.com","subject":"x","body":"y","kind":"%s"}`, "not_a_real_kind")
	w := s.doPost(r, payload)
	s.Equal(http.StatusBadRequest, w.Code)
}

func TestNotifyTestSuite(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping testcontainers-backed suite in short mode")
	}
	suite.Run(t, new(NotifyTestSuite))
}
