# Documentation

## 📁 Structure

### Debugging
War stories and complex bug investigations.

- [Graceful Shutdown Race Condition](./debugging/graceful-shutdown-race-condition.md) - A critical P0 bug where the application hung on shutdown after extended runtime. Deep dive into Go concurrency, WebSocket timeouts, and race conditions.

---

## 🎯 Quick Links

### For New Team Members
Start with the debugging case studies to understand:
- How we approach complex problems
- Architectural decisions and their reasoning
- Common pitfalls and how to avoid them

### For Code Reviews
Each case study includes:
- Prevention checklists
- Best practices
- Architectural patterns

---

## 📝 Contributing

When documenting a significant bug fix or architectural decision:

1. Create a new markdown file in the appropriate subdirectory
2. Follow the template (see existing case studies)
3. Include: problem, analysis, solution, and lessons learned
4. Add entry to this README

---

**Last Updated:** 2025-12-22

