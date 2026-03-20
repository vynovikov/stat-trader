package logger

import (
	"context"
	"fmt"
	"io"
	"log/slog"
	"strings"
)

type PrettyHandler struct {
	base slog.Handler
	out  io.Writer
}

func NewPrettyHandler(w io.Writer, opts *slog.HandlerOptions) slog.Handler {
	return &PrettyHandler{
		base: slog.NewTextHandler(w, opts),
		out:  w,
	}
}

func (h *PrettyHandler) Enabled(ctx context.Context, level slog.Level) bool {
	return h.base.Enabled(ctx, level)
}

func (h *PrettyHandler) Handle(ctx context.Context, r slog.Record) error {
	var b strings.Builder

	// Префикс: уровень + сообщение
	fmt.Fprintf(&b, "%s: %s\n", r.Level.String(), r.Message)

	// Аргументы
	r.Attrs(func(a slog.Attr) bool {
		if a.Key == "stack" {
			fmt.Fprintf(&b, "\nSTACK TRACE:\n%s\n", a.Value.String())
		} else {
			fmt.Fprintf(&b, "%s: %s\n", a.Key, a.Value.String())
		}
		return true
	})

	_, err := fmt.Fprint(h.out, b.String())
	return err
}

func (h *PrettyHandler) WithAttrs(attrs []slog.Attr) slog.Handler {
	return &PrettyHandler{
		base: h.base.WithAttrs(attrs),
		out:  h.out,
	}
}

func (h *PrettyHandler) WithGroup(name string) slog.Handler {
	return &PrettyHandler{
		base: h.base.WithGroup(name),
		out:  h.out,
	}
}
