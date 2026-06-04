package middleware

import (
	"net/http"
	"sync"

	"github.com/gin-gonic/gin"
	"golang.org/x/time/rate"
)

// KeyLimiter holds per-API-key token-bucket limiters.
type KeyLimiter struct {
	mu       sync.Mutex
	limiters map[string]*rate.Limiter
	rps      rate.Limit
	burst    int
}

// NewKeyLimiter constructs a limiter where each key gets `perMinute` tokens per minute,
// with a burst capacity of max(perMinute/6, 1) (so 60/min -> burst 10).
func NewKeyLimiter(perMinute int) *KeyLimiter {
	if perMinute <= 0 {
		perMinute = 60
	}
	burst := perMinute / 6
	if burst < 1 {
		burst = 1
	}
	return &KeyLimiter{
		limiters: make(map[string]*rate.Limiter),
		rps:      rate.Limit(float64(perMinute) / 60.0),
		burst:    burst,
	}
}

func (k *KeyLimiter) getLimiter(key string) *rate.Limiter {
	k.mu.Lock()
	defer k.mu.Unlock()
	if l, ok := k.limiters[key]; ok {
		return l
	}
	l := rate.NewLimiter(k.rps, k.burst)
	k.limiters[key] = l
	return l
}

// Middleware returns a gin.HandlerFunc that rate-limits per API key
// (taken from the "api_key" context value set by APIKeyAuth).
func (k *KeyLimiter) Middleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		v, ok := c.Get("api_key")
		if !ok {
			// No key on context means auth wasn't applied; fall through.
			c.Next()
			return
		}
		key, _ := v.(string)
		if !k.getLimiter(key).Allow() {
			c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{"error": "rate_limit_exceeded"})
			return
		}
		c.Next()
	}
}
