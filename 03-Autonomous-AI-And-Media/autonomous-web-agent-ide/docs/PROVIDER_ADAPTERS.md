# LLM Provider Adapters

The Autonomous Web-Agent IDE is completely decoupled from any single AI backend via the `LLMProvider` abstract interface.

---

## 1. Provider Interface

```python
class LLMProvider(ABC):
    @abstractmethod
    async def connect(self) -> bool: ...

    @abstractmethod
    async def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str: ...

    @abstractmethod
    async def health_check(self) -> Dict[str, Any]: ...

    @abstractmethod
    async def close(self): ...
```

---

## 2. Supported Adapters

### `DeepSeekWebProvider` (`deepseek_web`)
- Automates DeepSeek's Web Chat (`https://chat.deepseek.com`).
- Uses a persistent Chromium user data profile (`browser-profile/`) to keep user session cookies.
- Detects CAPTCHAs, rate limiting, and stop-generating buttons.
- Multi-selector fallback scraper.

### `GenericWebProvider` (`generic_web`)
- Connects to standard web chat interfaces using semantic and content-editable selectors.

### `MockLocalProvider` (`mock_provider`)
- Provides deterministic, offline responses for unit testing, test pipelines, and instant local execution.
- Generates valid task plans, full-stack Express + SQLite + React code, and handles error recovery.
