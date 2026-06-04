// Template: copy into apps/notification-service/internal/handler/{{NAME}}_test.go
// Replace {{NAME}}, {{METHOD}} (e.g. GET/POST), {{ENDPOINT}}, {{EXPECTED_STATUS}} (e.g. http.StatusOK).
// Assertion bodies should reflect the shape in contracts/schemas/*.json — not just "endpoint exists".

package handler

import (
	"bytes"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func Test_{{METHOD}}_{{NAME}}_Returns_{{EXPECTED_STATUS}}(t *testing.T) {
	gin.SetMode(gin.TestMode)
	router := gin.New()
	// Wire the route under test ONLY — keep the test focused:
	router.{{METHOD}}("{{ENDPOINT}}", New{{NAME}}Handler(/* mocked deps */).Handle)

	body := []byte(`{"field_from_contract":"value"}`) // match contracts/schemas/*.json
	req, _ := http.NewRequest(http.Method{{METHOD}}, "{{ENDPOINT}}", bytes.NewBuffer(body))
	req.Header.Set("Content-Type", "application/json")
	w := httptest.NewRecorder()
	router.ServeHTTP(w, req)

	assert.Equal(t, {{EXPECTED_STATUS}}, w.Code)
	assert.Contains(t, w.Body.String(), "field_from_contract")
}
