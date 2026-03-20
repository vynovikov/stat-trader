package ticker

import (
	"context"
	"encoding/csv"
	"fmt"
	"io"
	"log/slog"
	"os"
	"strconv"
	"strings"
	"time"

	emperror "emperror.dev/errors"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

type historyTicker struct {
	symbol string
	reader *csv.Reader
	domain domain
	logger *slog.Logger
}

func NewHistoryTicker(
	path string,
	domain domain,
	logger *slog.Logger,
) (
	historyTicker,
	chan entities.Candle,
	chan error,
	error,
) {
	chanErr := make(chan error, 10)
	symbol := strings.TrimSuffix(path, "_")

	file, err := os.Open(path)
	if err != nil {
		chanErr <- err
		return historyTicker{}, nil, chanErr, emperror.Wrap(err, "ticker.NewHistoryTicker")
	}

	reader := csv.NewReader(file)
	reader.ReuseRecord = true

	return historyTicker{
		symbol: symbol,
		reader: reader,
		domain: domain,
		logger: logger,
	}, make(chan entities.Candle, 1), chanErr, nil
}

func (h historyTicker) Run(
	ctx context.Context,
	cancel context.CancelFunc,
	chanData chan entities.Candle,
	chanErr chan error,
) {
	defer func() {
		close(chanData)
		close(chanErr)
		cancel()
	}()

	header, err := h.reader.Read()
	if err != nil {
		chanErr <- emperror.Wrap(err, "historyTicker.Run")
	}
	if len(header) < 7 {
		chanErr <- emperror.Wrap(fmt.Errorf("expected 7 columns, got %d", len(header)), "historyTicker.Run")
		//fmt.Errorf("expected 7 columns: got %v", header)
	}

	for {
		record, err := h.reader.Read()

		if err == io.EOF {
			h.logger.Info("History ticker finished reading file")
			return

		}
		if err != nil {
			chanErr <- emperror.Wrap(err, "historyTicker.Run")
			continue
		}

		// Парсим столбцы
		// open_time, open, high, low, close, volume, close_time

		open, err := strconv.ParseFloat(record[1], 64)
		if err != nil {
			chanErr <- fmt.Errorf("parse open: %w", err)
			continue
		}

		high, err := strconv.ParseFloat(record[2], 64)
		if err != nil {
			chanErr <- emperror.Wrap(err, "historyTicker.Run")
			continue
		}

		low, err := strconv.ParseFloat(record[3], 64)
		if err != nil {
			chanErr <- emperror.Wrap(err, "historyTicker.Run")
			continue
		}

		closeV, err := strconv.ParseFloat(record[4], 64)
		if err != nil {
			chanErr <- emperror.Wrap(err, "historyTicker.Run")
			continue
		}

		volume, err := strconv.ParseFloat(record[5], 64)
		if err != nil {
			chanErr <- emperror.Wrap(err, "historyTicker.Run")
			continue
		}

		closeTime, err := time.Parse(time.RFC3339, record[6])
		if err != nil {
			chanErr <- emperror.Wrap(err, "historyTicker.Run")
			continue
		}

		candle := entities.Candle{
			Symbol:    h.symbol,
			CloseTime: closeTime,
			Open:      open,
			High:      high,
			Low:       low,
			Close:     closeV,
			Volume:    volume,
		}

		select {
		case <-ctx.Done():
			return
		case chanData <- candle:
			spread := 0.0
			balance := 1000.0

			h.domain.Decide(ctx, h.symbol, candle, spread, balance)
		}
	}
}
