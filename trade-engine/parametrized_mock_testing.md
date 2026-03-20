# Parametrized Mock Testing

## 🎯 Goal

Создать компактный **gomock-style** паттерн для Python-тестов:

- ожидание = поведение = количество вызовов описываются **в одном месте**
- ожидания лежат **прямо в таблице кейсов**, тело теста остаётся чистым
- подход отлично дружит с `pytest.mark.parametrize` и table-driven стилем

---

## 🛠 Stack

- [pytest](https://docs.pytest.org/) — параметризация и ассерты
- [flexmock](https://github.com/bobf/flexmock) — строгие, декларативные моки

Установка:

```bash
pip install pytest flexmock
```

## 🧩 Core Idea

Каждый сценарий описывается как dict с полями:

- inputs — входные данные
- repo_setup — список функций lambda repo: ... с декларативными ожиданиями
- expect — ожидаемый результат/состояние

Тест выполняет четыре шага:

1) создать мок
2) применить repo_setup
3) запустить SUT
4) проверить expect

### 📝 Minimal Template
```python
from typing import Any, Callable, Dict, List
import pytest
from flexmock import flexmock

RepoSetupFn = Callable[[Any], None]

cases: List[Dict[str, Any]] = [
    {
        "name": "happy path",
        "inputs": {...},
        "repo_setup": [
            lambda repo: repo.should_receive("save")
                              .with_args(id=123, data=dict)  # isinstance check
                              .and_return(None)
                              .once(),
            lambda repo: repo.should_receive("get_by_id")
                              .with_args(123)
                              .and_return({"id": 123, "ok": True})
                              .once(),
        ],
        "expect": {"result": {"ok": True}},
    },
]

@pytest.mark.parametrize("case", cases, ids=[c["name"] for c in cases])
def test_subject(case):
    repo = flexmock()
    for setup in case["repo_setup"]:
        setup(repo)

    svc = YourService(repository=repo)

    result = svc.handle(case["inputs"])
    assert result == case["expect"]["result"]
```

### 🎛 Argument Matching

- По значению
```python
repo.should_receive("neighbors").with_args(id=10, limit=5)
```

- По типу (Segment ⇒ isinstance(arg, Segment))
```python
repo.should_receive("upsert").with_args(id=10, segment=Segment)
```

- По предикату
```python
repo.should_receive("save").with_args(obj=lambda x: x.version > 0)
```
💡 Если аргументы не совпадут — тест немедленно упадёт с понятным diff.

### 🔄 Call Counts

- *.once()* — ровно 1 вызов
- *.twice()* — ровно 2 вызова
- *.times(n)* — ровно *n* вызовов

### ↩️ Returning or Raising

- Возврат значения:
```python
repo.should_receive("neighbors") \
    .with_args(id=10, limit=5) \
    .and_return([NearestNeighbor(id=7)]) \
    .once()
```

- Исключение:
```python
repo.should_receive("neighbors") \
    .with_args(id=10, limit=5) \
    .and_raise(RuntimeError("backend down")) \
    .once()
```

### 📐 Case Shape

Рекомендуется держать каждый сценарий самодостаточным:
```python
{
  "name": "transitions to off_market",
  "inputs": {...},
  "repo_setup": [
    lambda repo: repo.should_receive("upsert")
                      .with_args(id=10, segment=Segment)
                      .and_return(None).twice(),
    lambda repo: repo.should_receive("neighbors")
                      .with_args(id=10, limit=5)
                      .and_return([NearestNeighbor(id=7)]).once(),
  ],
  "expect": {"state_id": "off_market"},
}
```

### 🍬 Optional Sugar

Можно определить маленькие хелперы, чтобы кейсы выглядели ещё компактнее:
```python
def expect_return(method, returns, times=1, **kwargs):
    return lambda repo: repo.should_receive(method) \
                             .with_args(**kwargs) \
                             .and_return(returns) \
                             .times(times)

def expect_raise(method, exc, times=1, **kwargs):
    return lambda repo: repo.should_receive(method) \
                             .with_args(**kwargs) \
                             .and_raise(exc) \
                             .times(times)
```

И тогда:
```python
"repo_setup": [
  expect_return("upsert", returns=None, times=2, id=10, segment=Segment),
  expect_return("neighbors", returns=[NearestNeighbor(id=7)], id=10, limit=5),
]
```

### ⚖️ Style Guidelines

- держите логику вне теста — тело теста должно быть читаемо: build → setup → run → assert
- используйте матчинг по типу для сложных объектов (Segment), чтобы избежать хрупких сравнений
- один вызов = одно ожидание; разные варианты аргументов — разные lambda repo: ...
- мокайте только внешние зависимости (репозитории, клиенты)
- не прячьте «молчаливые» вызовы: если метод опционален — отражайте это в кейсе

### 🚨 Troubleshooting

- Unexpected call → значит, вызов не покрыт with_args
- Wrong number of calls → проверь .once()/.twice()/.times(n)
- Flaky asserts (time, UUID) → матчите по типу или предикату, а не по точному значению

### ✅ Example: FSM Engine

```python
import pytest
from flexmock import flexmock
from datetime import datetime

from domain.models.candle import Candle
from domain.models.nearest_neighbor import NearestNeighbor
from domain.models.segment import Segment
from services.trade_engine import TradeEngineReversalV2

cases = [
    {
        "name": "Not_ready -> off_market",
        "initial_candles": [Candle(100.5,100.4,100.45,100.48,1000), ...],
        "candle": Candle(100.7,100.6,100.58,100.55,1000),
        "avg_candle_len": 1.5,
        "repo_setup": [
            lambda r: r.should_receive("upsert")
                       .with_args(id=10, segment=Segment)
                       .and_return(None).twice(),
            lambda r: r.should_receive("neighbors")
                       .with_args(id=10, limit=5)
                       .and_return([NearestNeighbor(id=7)]).once(),
        ],
        "expect": {"state_id": "off_market"},
    },
]

@pytest.mark.parametrize("case", cases, ids=[c["name"] for c in cases])
def test_fsm(case):
    repo = flexmock()
    for f in case["repo_setup"]:
        f(repo)

    fsm = TradeEngineReversalV2(repository=repo, avg_candle_len=case["avg_candle_len"],
                         last_id=10, expire_in=365, neighbor_limit=5)

    for c in case["initial_candles"]:
        fsm.handle_first(c)
    fsm.handle_first(case["candle"])

    assert fsm.current_state.id == case["expect"]["state_id"]
```

