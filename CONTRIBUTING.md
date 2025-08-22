# Contributing to WyreStorm NetworkHD

Thank you for your interest in contributing! This guide will help you get started.

## 🚀 Quick Start

1. **Fork the repository**
1. **Create a feature branch**: `git checkout -b feature/amazing-feature`
1. **Make your changes**
1. **Run tests**: `make test`
1. **Commit with conventional commits**: `git commit -m "feat: add amazing feature"`
1. **Push to your fork**: `git push origin feature/amazing-feature`
1. **Create a Pull Request**

## 📋 Development Setup

### Prerequisites

- Python 3.12+ (see pyproject.toml for exact requirements)
- Git

### Local Development Environment

```bash
# Clone your fork
git clone https://github.com/Matt-Hadley/wyrestorm-networkhd-py.git
cd wyrestorm-networkhd

# Complete development setup (creates venv, installs deps, sets up pre-commit)
make install

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

## 🧪 Testing

```bash
# Run all tests
make test

# Run tests with coverage report
make test-cov

# Check all available commands
make help
```

## 📝 Code Style

- **Line Length**: 120 characters maximum
- **Formatter**: Ruff (configured in pyproject.toml)
- **Linter**: Ruff + MyPy
- **Pre-commit**: Hooks run automatically on commit

## 🔧 Development Workflow

### Daily Development Commands

```bash
# Complete setup (run once)
make install

# Daily development workflow: format → lint → test
make dev-workflow

# Individual commands
make format        # Format code and docs
make lint         # Run linting checks
make test         # Run tests
make build        # Build package

# Quality checks before committing
make check

# Full project validation before release
make health-check
```

### Branch Naming

- `feature/description`: New features
- `fix/description`: Bug fixes
- `docs/description`: Documentation updates
- `refactor/description`: Code refactoring

### Commit Messages

Use [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new video wall scene management
fix: resolve SSH connection timeout issue
docs: update API documentation examples
refactor: simplify matrix switching logic
test: add unit tests for device control
chore: update dependencies
```

### Pull Request Process

1. **Create PR** with descriptive title and description
1. **Link issues** using keywords (fixes #123, relates to #456)
1. **Address feedback** and update PR
1. **Merge** after approval and CI passing

## 🐛 Bug Reports

### Before Reporting

- Check existing issues
- Try latest version
- Reproduce in minimal environment

### Bug Report Template

```markdown
## Bug Description

Brief description of the issue

## Steps to Reproduce

1. Step 1
2. Step 2
3. Step 3

## Expected Behavior

What should happen

## Actual Behavior

What actually happens

## Environment

- OS: [e.g., Ubuntu 22.04]
- Python: [e.g., 3.12.1] (see pyproject.toml for requirements)
- Package Version: [e.g., 1.2.3]
```

## 💡 Feature Requests

### Before Requesting

- Check if feature already exists
- Consider if it fits project scope
- Think about implementation complexity

### Feature Request Template

```markdown
## Feature Description

Brief description of the requested feature

## Use Case

Why this feature is needed

## Proposed Implementation

How you think it should work
```

## 🔒 Security

**DO NOT** create public issues for security vulnerabilities. Instead:

1. Email: [81762940+Matt-Hadley@users.noreply.github.com]
1. Use subject: `[SECURITY] WyreStorm NetworkHD - [Brief Description]`
1. Include detailed reproduction steps

## 📚 Documentation

- Use clear, concise language
- Include code examples
- Keep examples up-to-date
- Use consistent formatting

## 🚀 Release Process

- Uses [Semantic Versioning](https://semver.org/)
- Automatic versioning via conventional commits
- Release notes generated from conventional commits
- PyPI publication automated via CI/CD

## 🤝 Community Guidelines

- Be respectful and inclusive
- Focus on technical merit
- Welcome newcomers
- Constructive feedback only

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Need help?** Open an issue or start a discussion. We're here to help!
