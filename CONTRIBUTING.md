# Contributing to deepstock-bot

Thank you for your interest in contributing! 🎉

## How to Contribute

### Reporting Bugs

- Use [GitHub Issues](https://github.com/bernhardbrugger/deepstock-bot/issues)
- Include steps to reproduce, expected vs actual behavior
- Include Python version and OS

### Suggesting Features

- Open an issue with the `enhancement` label
- Describe the use case and expected behavior

### Pull Requests

1. **Fork** the repo and create your branch from `main`
2. **Install** dev dependencies: `make install`
3. **Write tests** for any new functionality
4. **Lint** your code: `make lint`
5. **Test** your changes: `make test`
6. **Commit** with clear, descriptive messages
7. **Push** and open a PR

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use type hints for all function signatures
- Write docstrings (Google style)
- Keep functions focused and small

### Commit Messages

```
feat: add Discord alert channel
fix: handle empty API response in FMP client
docs: update configuration guide
refactor: simplify trade scoring logic
```

## Development Setup

```bash
git clone https://github.com/bernhardbrugger/deepstock-bot.git
cd deepstock-bot
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

## Code of Conduct

Be kind, be respectful. We're all here to build something cool. 🤖📊

## Questions?

Open an issue or reach out — happy to help!
