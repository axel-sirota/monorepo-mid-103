package service

import (
	"fmt"
	"net/smtp"
	"strings"
)

// Sender is the abstraction over SMTP so tests can mock it.
type Sender interface {
	Send(from, to, subject, body string) error
}

// SMTPSender sends via net/smtp without auth (matches Mailhog dev env).
type SMTPSender struct {
	Host string
	Port string
}

// NewSMTPSender constructs a stdlib SMTP sender.
func NewSMTPSender(host, port string) *SMTPSender {
	return &SMTPSender{Host: host, Port: port}
}

// Send formats a plain-text message and dispatches it via the configured SMTP server.
func (s *SMTPSender) Send(from, to, subject, body string) error {
	addr := fmt.Sprintf("%s:%s", s.Host, s.Port)
	msg := buildMessage(from, to, subject, body)
	return smtp.SendMail(addr, nil, from, []string{to}, []byte(msg))
}

func buildMessage(from, to, subject, body string) string {
	var b strings.Builder
	b.WriteString("From: ")
	b.WriteString(from)
	b.WriteString("\r\n")
	b.WriteString("To: ")
	b.WriteString(to)
	b.WriteString("\r\n")
	b.WriteString("Subject: ")
	b.WriteString(subject)
	b.WriteString("\r\n")
	b.WriteString("Content-Type: text/plain; charset=\"utf-8\"\r\n")
	b.WriteString("\r\n")
	b.WriteString(body)
	return b.String()
}
