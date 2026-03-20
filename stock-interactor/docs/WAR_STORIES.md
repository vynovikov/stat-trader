# Engineering War Stories

Personal collection of complex problems solved and lessons learned.

---

## 2025-12-22: The Sneaky Graceful Shutdown Bug ⭐⭐⭐⭐⭐

**Symptom:** App hangs on Ctrl+C after 30+ minutes, but works fine if stopped early.

**Root Cause:** WebSocket reconnection (`InitStream.ReadMessage`) had no timeout. During reconnect, if shutdown signal arrived, the read operation blocked forever.

**Key Challenge:** Race condition - only appeared when reconnect timing coincided with shutdown.

**What I Learned:**
- Always set deadlines on ALL network I/O (even "quick" operations)
- `select` is a snapshot, not a guard - context can cancel between check and execution
- `SetReadDeadline(t time.Time)` is absolute time, not duration - must refresh before each read
- Channel sends during shutdown must be non-blocking
- Timing-dependent bugs are hardest to catch - need stress testing

**Skills Demonstrated:**
- Goroutine dump analysis
- Systematic debugging methodology
- Go concurrency deep understanding (context, channels, select)
- Network programming (WebSocket, timeouts, deadlines)
- Architectural thinking (consistency, configuration)
- Root cause analysis (not just symptom fixing)

**Technical Details:**
- Used pprof goroutine dumps to identify blocking goroutine
- Traced call stack: Worker → reconnect → InitStream → ReadMessage
- Found log from 2 minutes earlier: Binance abnormal closure (1006)
- Timeline reconstruction showed race between reconnect and shutdown
- Solution: Added configurable INIT_TIMEOUT with proper deadline management

**Complexity:** 5/5 (race condition + multiple layers + timing-dependent)

**For Interviews:**
> "I debugged a production race condition in a Go trading bot where graceful shutdown would hang, but only after 30+ minutes of runtime. Using goroutine dumps and systematic analysis, I traced it to a missing timeout in the WebSocket reconnection flow. The bug only appeared when shutdown coincided with reconnection - a timing-dependent issue that required understanding Go's concurrency primitives, network I/O semantics, and proper use of context cancellation."

**GitHub:** [Link to commit / PR]

**Full Documentation:** [docs/debugging/graceful-shutdown-race-condition.md](./debugging/graceful-shutdown-race-condition.md)

---

## Template for Future Stories

```markdown
## YYYY-MM-DD: [Bug Title] ⭐⭐⭐⭐⭐

**Symptom:**
**Root Cause:**
**Key Challenge:**
**What I Learned:**
**Skills Demonstrated:**
**Complexity:** X/5
**For Interviews:**
**Full Documentation:** [link]
```

---

**Legend:**
- ⭐⭐⭐⭐⭐ Extremely complex (race conditions, multiple systems, non-obvious)
- ⭐⭐⭐⭐ Complex (requires deep understanding)
- ⭐⭐⭐ Moderate (systematic approach needed)
- ⭐⭐ Simple (straightforward debugging)
- ⭐ Trivial (typo, config error)

