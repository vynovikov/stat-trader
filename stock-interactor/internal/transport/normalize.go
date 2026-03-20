package transport

import (
	"time"

	"github.com/vector-trader/stock-interactor/internal/entities"
)

func Normalize(
	historyEntity entities.History,
	limit int,
) (
	[]entities.History,
	error,
) {
	if len(historyEntity.Symbol) == 0 {
		return nil, nil
	}
	var next time.Time
	start, end := time.Unix(0, historyEntity.FromTimestamp*int64(time.Millisecond)),
		time.Unix(0, historyEntity.ToTimestamp*int64(time.Millisecond))

	interval, err := time.ParseDuration(historyEntity.Interval)
	if err != nil {
		return nil, err
	}

	chunkDuration := interval * time.Duration(limit)

	normalizedHistoryEntities := make([]entities.History, 0)

	for start.Before(end) {
		next = start.Add(chunkDuration)
		if next.After(end) {
			next = end
		}
		normalizedHistoryEntities = append(normalizedHistoryEntities, entities.History{
			Symbol:        historyEntity.Symbol,
			Interval:      historyEntity.Interval,
			FromTimestamp: start.UnixMilli(),
			ToTimestamp:   next.UnixMilli(),
		})

		start = next
	}

	return normalizedHistoryEntities, nil
}
