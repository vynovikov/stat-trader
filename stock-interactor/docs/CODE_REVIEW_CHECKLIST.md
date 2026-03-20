# Code Review Checklist

Checklist derived from production bugs and best practices.

---

## 🌐 Network Operations

### Timeouts & Deadlines
- [ ] All `Read()` operations have timeouts/deadlines?
- [ ] All `Write()` operations have timeouts/deadlines?
- [ ] All `Dial()` operations use `DialContext` with timeout?
- [ ] Timeouts are configurable via environment variables?
- [ ] Default timeout values are reasonable (5-30s)?

### WebSocket Specific
- [ ] Subscription confirmation read has timeout?
- [ ] Ping/pong handlers have timeouts?
- [ ] Reconnection logic has timeout protection?
- [ ] Close handshake has timeout?

**Reference:** [graceful-shutdown-race-condition.md](./debugging/graceful-shutdown-race-condition.md)

---

## 🔄 Graceful Shutdown

### Context Handling
- [ ] All goroutines respect context cancellation?
- [ ] Long-running operations check `ctx.Done()` periodically?
- [ ] Context passed to all network operations?
- [ ] `select` statements include `<-ctx.Done()` case?

### Channel Operations
- [ ] Channel sends are non-blocking during shutdown?
  ```go
  // Good
  select {
  case ch <- data:
  case <-ctx.Done():
      return
  }

  // Bad
  ch <- data  // can block forever during shutdown
  ```

- [ ] Channel receives have timeout or context check?
- [ ] Buffered channels have appropriate buffer size?

### Cleanup
- [ ] Deferred cleanup handlers (`defer`) present?
- [ ] Resources (connections, files) closed properly?
- [ ] WaitGroups used correctly (`Add` before goroutine spawn)?

---

## 🔀 Concurrency

### Race Conditions
- [ ] Shared state protected by mutex or channels?
- [ ] No assumptions about goroutine execution order?
- [ ] Atomic operations used for counters/flags?
- [ ] Code passes `go run -race`?

### Select Statements
- [ ] Understand that `select` is a snapshot, not a guard?
- [ ] No blocking operations in `default` case without context check?
- [ ] Random selection behavior acceptable when multiple cases ready?

### Context Best Practices
- [ ] Context created at request/operation boundary?
- [ ] Context passed as first parameter?
- [ ] `context.WithTimeout` used instead of manual deadline?
- [ ] Context cancellation cleanup handled (`defer cancel()`)?

---

## 🐛 Error Handling

### Logging
- [ ] Errors logged with sufficient context?
- [ ] Structured logging used (not just `fmt.Printf`)?
- [ ] Log levels appropriate (ERROR vs WARN vs INFO)?
- [ ] Sensitive data not logged?

### Recovery
- [ ] Retry logic has exponential backoff?
- [ ] Maximum retry attempts configured?
- [ ] Circuit breaker pattern considered for external deps?
- [ ] Panic recovery in goroutines (`defer recover()`)?

### Propagation
- [ ] Errors wrapped with context (`fmt.Errorf` with `%w`)?
- [ ] Sentinel errors used for expected cases?
- [ ] Error handling doesn't block shutdown?

---

## 📊 Observability

### Metrics
- [ ] Key operations instrumented?
- [ ] Error rates tracked?
- [ ] Latency percentiles measured?
- [ ] Resource usage (goroutines, memory) monitored?

### Debugging
- [ ] pprof endpoints enabled?
- [ ] Goroutine dumps on hang condition?
- [ ] Trace IDs propagated through call chain?
- [ ] Debug logging available (behind flag)?

---

## 🏗️ Architecture

### Configuration
- [ ] All timeouts/limits configurable?
- [ ] Sensible defaults provided?
- [ ] Configuration validation on startup?
- [ ] Environment variables documented?

### Consistency
- [ ] Similar operations have similar timeouts?
- [ ] Error handling patterns consistent across codebase?
- [ ] Logging format consistent?
- [ ] Naming conventions followed?

### Testing
- [ ] Unit tests for happy path?
- [ ] Tests for error conditions?
- [ ] Tests for timeout scenarios?
- [ ] Tests for graceful shutdown?
- [ ] Integration tests for critical paths?

---

## 🎯 Specific Patterns to Watch For

### Anti-Pattern: Blocking Channel Send
```go
// ❌ Bad - can block forever during shutdown
chanErr <- err

// ✅ Good - non-blocking
select {
case chanErr <- err:
case <-ctx.Done():
}
```

### Anti-Pattern: No Timeout on Network I/O
```go
// ❌ Bad - can block forever
conn.ReadMessage()

// ✅ Good - has timeout
conn.SetReadDeadline(time.Now().Add(timeout))
conn.ReadMessage()
```

### Anti-Pattern: Select Without Context
```go
// ❌ Bad - misses shutdown signal
select {
case data := <-dataCh:
    process(data)
default:
    // do something
}

// ✅ Good - includes shutdown path
select {
case data := <-dataCh:
    process(data)
case <-ctx.Done():
    return ctx.Err()
default:
    // do something
}
```

### Anti-Pattern: Hardcoded Timeouts
```go
// ❌ Bad - hardcoded
time.Sleep(5 * time.Second)

// ✅ Good - configurable
time.Sleep(cfg.RetryDelay)
```

---

## 📝 Review Process

1. **Automated Checks**
   - [ ] `go vet` passes
   - [ ] `golangci-lint` passes
   - [ ] Tests pass
   - [ ] Race detector passes (`go test -race`)

2. **Manual Review**
   - [ ] All checklist items above verified
   - [ ] Code follows project conventions
   - [ ] Changes documented (comments, docs)
   - [ ] Breaking changes communicated

3. **Testing Recommendations**
   - [ ] Test with short runtime (< 5 min)
   - [ ] Test with long runtime (> 30 min)
   - [ ] Test graceful shutdown at various points
   - [ ] Test error injection (network issues, timeouts)

---

## 🎓 Additional Resources

- [Effective Go](https://go.dev/doc/effective_go)
- [Go Code Review Comments](https://github.com/golang/go/wiki/CodeReviewComments)
- [Uber Go Style Guide](https://github.com/uber-go/guide/blob/master/style.md)
- Project-specific war stories: [WAR_STORIES.md](./WAR_STORIES.md)

---

**Remember:** This checklist exists because each item was learned through a real bug in production. Don't skip items!

**Last Updated:** 2025-12-22

