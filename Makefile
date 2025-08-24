# =============================================================================
# Project Configuration
# =============================================================================
PROJECT_NAME := $(shell python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'].replace('-', '_'))" 2>/dev/null || echo "wyrestorm_networkhd")
PROJECT_DISPLAY_NAME := $(shell python3 -c "import tomllib; print(tomllib.load(open('pyproject.toml', 'rb'))['project']['name'])" 2>/dev/null || echo "wyrestorm-networkhd")

# Virtual environment configuration
VENV_DIR := .venv
VENV_BIN := $(VENV_DIR)/bin
PYTHON := $(VENV_BIN)/python
PIP := $(VENV_BIN)/pip

# Development tools (use venv versions in CI, system versions locally as fallback)
RUFF := $(shell if [ -x "$(VENV_BIN)/ruff" ]; then echo "$(VENV_BIN)/ruff"; else echo "ruff"; fi)
MYPY := $(shell if [ -x "$(VENV_BIN)/mypy" ]; then echo "$(VENV_BIN)/mypy"; else echo "mypy"; fi)
BANDIT := $(shell if [ -x "$(VENV_BIN)/bandit" ]; then echo "$(VENV_BIN)/bandit"; else echo "bandit"; fi)
PIP_AUDIT := $(shell if [ -x "$(VENV_BIN)/pip-audit" ]; then echo "$(VENV_BIN)/pip-audit"; else echo "pip-audit"; fi)
PYTEST := $(shell if [ -x "$(VENV_BIN)/pytest" ]; then echo "$(VENV_BIN)/pytest"; else echo "pytest"; fi)
PRE_COMMIT := $(shell if [ -x "$(VENV_BIN)/pre-commit" ]; then echo "$(VENV_BIN)/pre-commit"; else echo "pre-commit"; fi)
VULTURE := $(shell if [ -x "$(VENV_BIN)/vulture" ]; then echo "$(VENV_BIN)/vulture"; else echo "vulture"; fi)
PYUPGRADE := $(shell if [ -x "$(VENV_BIN)/pyupgrade" ]; then echo "$(VENV_BIN)/pyupgrade"; else echo "pyupgrade"; fi)
SPHINX := $(shell if [ -x "$(VENV_BIN)/sphinx-build" ]; then echo "$(VENV_BIN)/sphinx-build"; else echo "sphinx-build"; fi)

# Better Python detection
PYTHON3 := $(shell command -v python3 2> /dev/null || echo "python3")

# File exclusion patterns
EXCLUDE_FILES := _version.py

# Fallback for systems without python3
ifeq ($(PYTHON3),python3)
    PYTHON3 := python
endif

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Verbosity control
ifeq ($(VERBOSE),1)
    Q :=
    ECHO := @echo
else
    Q := @
    ECHO := @echo
endif

# Default target
.DEFAULT_GOAL := help

# Phony targets
.PHONY: help \
        install install-pkg create-venv install-deps update-deps \
        test test-cov \
        format format-code format-docs \
        lint type-check type-check-strict \
        security-check security-audit code-quality check \
        build release \
        clean clean-all clean-build clean-pyc clean-test clean-cache clean-docs \
        health-check check-project-structure check-versions show-deps \
        setup-pre-commit pre-commit validate-config ensure-venv \
        dev-workflow docker-build docker-test \
        docs docs-serve

# =============================================================================
# Help Target
# =============================================================================
help: ## Show this help message
	@echo "$(BLUE)Available commands for $(PROJECT_DISPLAY_NAME):$(NC)"
	@echo ""
	@echo "$(GREEN)🚀 Quick Start:$(NC)"
	@echo "  install          - Complete development environment setup"
	@echo "  dev-workflow     - Format → Lint → Fast Tests (daily development)"
	@echo "  health-check     - Comprehensive project validation (all tests + docs)"
	@echo ""
	@echo "$(YELLOW)📦 Development Setup:$(NC)"
	@echo "  install          - Complete development environment setup"
	@echo "  install-pkg      - Install package in development mode"
	@echo "  create-venv      - Create/ensure virtual environment"
	@echo "  install-deps     - Install development dependencies"
	@echo "  update-deps      - Update all dependencies"
	@echo "  setup-pre-commit - Install pre-commit hooks"
	@echo ""
	@echo "$(YELLOW)🧪 Testing:$(NC)"
	@echo "  test             - Run all tests"
	@echo "  test-fast        - Run only fast unit tests (daily development)"
	@echo "  test-integration - Run integration tests only"
	@echo "  test-performance - Run performance tests only"
	@echo "  test-cov         - Run all tests with coverage report"
	@echo ""
	@echo "$(YELLOW)✨ Code Formatting:$(NC)"
	@echo "  format           - Format all code and documentation"
	@echo "  format-code      - Format Python code (pyupgrade + Ruff)"
	@echo "  format-docs      - Format documentation (Prettier)"
	@echo ""
	@echo "$(YELLOW)🔍 Code Quality:$(NC)"
	@echo "  check            - Run all quality checks"
	@echo "  lint             - Run linting checks"
	@echo "  type-check       - Run type checking (non-blocking)"
	@echo "  type-check-strict - Run type checking (strict)"
	@echo "  code-quality     - Run dead code & typo checks"
	@echo "  security-check   - Run security checks"
	@echo "  security-audit   - Generate detailed security report"
	@echo ""
	@echo "$(YELLOW)📦 Build & Release:$(NC)"
	@echo "  build            - Build and validate package"
	@echo "  release          - Prepare for release"
	@echo ""
	@echo "$(YELLOW)🧹 Cleanup:$(NC)"
	@echo "  clean            - Remove all build artifacts"
	@echo "  clean-all        - Remove everything including venv"
	@echo ""
	@echo "$(YELLOW)🔧 Utilities:$(NC)"
	@echo "  health-check     - Comprehensive project validation (includes docs)"
	@echo "  show-deps        - Show installed dependencies"
	@echo "  check-versions   - Check Python and package versions"
	@echo "  pre-commit       - Setup and run pre-commit hooks"
	@echo ""
	@echo "$(YELLOW)📚 Documentation:$(NC)"
	@echo "  docs             - Build MkDocs documentation with all extensions"
	@echo "  docs-serve       - Serve documentation locally with live reload"
	@echo "  clean-docs       - Clean documentation build artifacts"
	@echo ""
	@echo "$(BLUE)🐳 Docker:$(NC)"
	@echo "  docker-build     - Build Docker image"
	@echo "  docker-test      - Run tests in Docker"

# =============================================================================
# Quick Start Targets
# =============================================================================
install: validate-config create-venv check-versions install-deps setup-pre-commit ## Complete development environment setup
	@echo ""
	@echo "$(GREEN)🎉 Setup complete! Next steps:$(NC)"
	@echo "  1. Activate: source $(VENV_DIR)/bin/activate"
	@echo "  2. Check health: make health-check"
	@echo "  3. Start coding!"

dev-workflow: format check test-fast ## Complete development workflow (format, check, fast tests only)
	@echo "$(GREEN)✓$(NC) Development workflow completed (fast tests only)"

health-check: validate-config check-versions show-deps check-project-structure format-check test-cov check security-audit build docs ## Comprehensive project validation
	@echo ""
	@echo "$(GREEN)🎉 Health check complete - all systems validated!$(NC)"

# =============================================================================
# Development Setup
# =============================================================================
install-pkg: ## Install package in development mode
	$(Q)pip install -e .

create-venv: ## Create/ensure virtual environment
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(YELLOW)📦 Creating virtual environment...$(NC)"; \
		$(PYTHON3) -m venv $(VENV_DIR); \
		echo "$(GREEN)✓$(NC) Virtual environment created"; \
	else \
		echo "$(GREEN)✓$(NC) Virtual environment already exists"; \
	fi

install-deps: create-venv ## Install development dependencies
	$(ECHO) "$(YELLOW)🔧 Installing development dependencies...$(NC)"
	$(Q)$(PIP) install --upgrade pip
	$(Q)$(PIP) install -e ".[dev]"
	@echo "$(GREEN)✓$(NC) Development dependencies installed"

update-deps: install-deps ## Update all dependencies
	@echo "$(GREEN)✓$(NC) Dependencies updated"

setup-pre-commit: install-deps ## Install pre-commit hooks
	$(ECHO) "$(YELLOW)📝 Installing pre-commit hooks...$(NC)"
	$(Q)$(VENV_BIN)/pre-commit install
	@echo "$(GREEN)✓$(NC) Pre-commit hooks installed"

# =============================================================================
# Testing
# =============================================================================
test: ## Run all tests
	$(ECHO) "$(YELLOW)Running all tests...$(NC)"
	$(Q)$(PYTEST)
	@echo "$(GREEN)✓$(NC) All tests completed"

test-fast: ## Run only fast unit tests (exclude integration and performance tests)
	$(ECHO) "$(YELLOW)Running fast unit tests only...$(NC)"
	$(Q)$(PYTEST) -m "unit" --tb=short
	@echo "$(GREEN)✓$(NC) Fast tests completed"

test-integration: ## Run integration tests only (exclude performance tests)
	$(ECHO) "$(YELLOW)Running integration tests only...$(NC)"
	$(Q)$(PYTEST) -m "integration and not performance" --tb=short
	@echo "$(GREEN)✓$(NC) Integration tests completed"

test-performance: ## Run performance tests only
	$(ECHO) "$(YELLOW)Running performance tests only...$(NC)"
	$(Q)$(PYTEST) -m "performance" --tb=short
	@echo "$(GREEN)✓$(NC) Performance tests completed"

test-cov: ## Run all tests with coverage
	$(ECHO) "$(YELLOW)Running all tests with coverage...$(NC)"
	$(Q)$(PYTEST) --cov=src/$(PROJECT_NAME) --cov-report=term-missing --cov-report=html --cov-report=xml
	@echo "$(GREEN)✓$(NC) Coverage report generated"

# =============================================================================
# Code Formatting
# =============================================================================
format: format-code format-docs ## Format all code and documentation

format-check: ## Check if code is properly formatted (without fixing)
	$(ECHO) "$(YELLOW)Checking code formatting...$(NC)"
	$(Q)$(RUFF) format --check .
	$(Q)$(RUFF) check --diff .
	@if command -v prettier >/dev/null 2>&1; then \
		prettier --check "**/*.{json,yaml,yml,md}" --ignore-path .gitignore || true; \
	fi
	@echo "$(GREEN)✓$(NC) Code formatting verified"
	@echo "$(GREEN)✅ All formatting completed$(NC)"

format-code: ## Format Python code with pyupgrade + Ruff
	$(ECHO) "$(YELLOW)Formatting Python code...$(NC)"
	@if command -v $(PYUPGRADE) >/dev/null 2>&1; then \
		find src/ tests/ -name "*.py" ! -name "$(EXCLUDE_FILES)" -exec $(PYUPGRADE) --py312-plus {} +; \
	else \
		echo "$(YELLOW)⚠ pyupgrade not found - run 'make install-deps' to install it$(NC)"; \
		exit 1; \
	fi
	$(Q)$(RUFF) format .
	$(Q)$(RUFF) check --fix .
	@echo "$(GREEN)✓$(NC) Python code formatted"

format-docs: ## Format documentation and config files with Prettier
	$(ECHO) "$(YELLOW)Formatting documentation files...$(NC)"
	@if command -v prettier >/dev/null 2>&1; then \
		prettier --write "**/*.{md,yml,yaml,json}"; \
		echo "$(GREEN)✓$(NC) Documentation formatted with prettier"; \
	else \
		echo "$(YELLOW)⚠ prettier not found - install with 'npm install -g prettier'$(NC)"; \
		echo "$(YELLOW)  Or use pre-commit: pre-commit run prettier --all-files$(NC)"; \
		exit 1; \
	fi

# =============================================================================
# Code Quality & Linting
# =============================================================================
check: lint type-check code-quality security-check ## Run all code quality checks
	@echo "$(GREEN)✅ All code quality checks completed$(NC)"

lint: ## Run linting checks
	$(ECHO) "$(YELLOW)Running linting...$(NC)"
	$(Q)$(RUFF) check .
	@echo "$(GREEN)✓$(NC) Linting completed"

type-check: ## Run type checking with MyPy (non-blocking)
	$(ECHO) "$(YELLOW)Running type checks...$(NC)"
	$(Q)$(MYPY) src/ || echo "$(YELLOW)⚠ Type checking found issues - see output above$(NC)"
	@echo "$(GREEN)✓$(NC) Type checking completed"

type-check-strict: ## Run type checking with MyPy (strict - fails on errors)
	$(ECHO) "$(YELLOW)Running strict type checks...$(NC)"
	$(Q)$(MYPY) src/
	@echo "$(GREEN)✓$(NC) Strict type checking passed"

code-quality: ## Run additional code quality checks
	$(ECHO) "$(YELLOW)Running code quality checks...$(NC)"
	@if command -v $(VULTURE) >/dev/null 2>&1; then \
		$(VULTURE) src/ --min-confidence 80 --exclude "*/$(EXCLUDE_FILES)"; \
	else \
		echo "$(YELLOW)⚠ vulture not found - install with 'pip install vulture'$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓$(NC) Code quality checks completed"

security-check: ## Run security checks
	$(ECHO) "$(YELLOW)Running security checks...$(NC)"
	$(Q)$(BANDIT) -c pyproject.toml -r src/
	@if command -v $(PIP_AUDIT) >/dev/null 2>&1; then \
		$(PIP_AUDIT) --skip-editable; \
	else \
		echo "$(YELLOW)⚠ pip-audit not found - run 'make install-deps' to install it$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓$(NC) Security checks completed"

security-audit: ## Generate detailed security report
	$(ECHO) "$(YELLOW)Generating security audit report...$(NC)"
	$(Q)$(PIP_AUDIT) --skip-editable --format json --output security-report.json
	@echo "$(GREEN)✓$(NC) Security report saved to security-report.json"

# =============================================================================
# Build & Release
# =============================================================================
build: clean-build ## Build wheel only and validate package
	$(ECHO) "$(YELLOW)Building wheel...$(NC)"
	$(Q)$(PYTHON) -m build --wheel
	$(Q)$(PYTHON) -m twine check dist/*
	@echo "$(GREEN)✅ Wheel built and validated successfully$(NC)"


# =============================================================================
# Cleanup
# =============================================================================
clean: clean-build clean-pyc clean-test clean-cache clean-docs ## Remove all build artifacts

clean-all: clean ## Remove everything including venv
	$(ECHO) "$(YELLOW)Removing virtual environment...$(NC)"
	$(Q)rm -rf $(VENV_DIR)
	@echo "$(GREEN)✓$(NC) Complete cleanup finished"

clean-build: ## Remove build artifacts
	$(ECHO) "$(YELLOW)Cleaning build artifacts...$(NC)"
	$(Q)rm -rf build/ dist/
	$(Q)find . -name '*.egg-info' -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓$(NC) Build artifacts cleaned"

clean-pyc: ## Remove Python cache files
	$(ECHO) "$(YELLOW)Cleaning Python cache files...$(NC)"
	$(Q)find . -name '*.pyc' -delete
	$(Q)find . -name '*.pyo' -delete
	$(Q)find . -name '__pycache__' -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓$(NC) Python cache cleaned"

clean-test: ## Remove test artifacts
	$(ECHO) "$(YELLOW)Cleaning test artifacts...$(NC)"
	$(Q)rm -rf .pytest_cache/ htmlcov/ coverage.xml
	$(Q)find . -name '.coverage*' -type f -delete 2>/dev/null || true
	@echo "$(GREEN)✓$(NC) Test artifacts cleaned"

clean-cache: ## Remove tool cache files
	$(ECHO) "$(YELLOW)Cleaning tool caches...$(NC)"
	$(Q)rm -rf .ruff_cache/ .mypy_cache/ .claude/
	@echo "$(GREEN)✓$(NC) Tool caches cleaned"

# =============================================================================
# Utilities
# =============================================================================
show-deps: ## Show installed dependencies
	@echo "$(YELLOW)Installed dependencies:$(NC)"
	@if [ -x "$(PIP)" ]; then \
		$(PIP) list; \
	else \
		echo "$(YELLOW)⚠ Virtual environment not found - run 'make install' first$(NC)"; \
		exit 1; \
	fi

check-versions: ## Check Python and package versions
	@echo "$(YELLOW)Version information:$(NC)"
	@$(PYTHON) -c "import sys; print('$(GREEN)Python:$(NC) ' + sys.version)"
	@$(PYTHON) -c "import $(PROJECT_NAME); print('$(GREEN)✓$(NC) Package importable')" 2>/dev/null || echo "$(RED)✗$(NC) Package not importable"

pre-commit: setup-pre-commit ## Setup, update and run pre-commit hooks
	$(ECHO) "$(YELLOW)Updating and running pre-commit...$(NC)"
	$(Q)pre-commit autoupdate
	$(Q)pre-commit run --all-files
	@echo "$(GREEN)✓$(NC) Pre-commit completed"

# =============================================================================
# Documentation
# =============================================================================
DOCS_BUILD_DIR := site
MKDOCS := $(shell if [ -x "$(VENV_BIN)/mkdocs" ]; then echo "$(VENV_BIN)/mkdocs"; else echo "mkdocs"; fi)

docs: ## Build MkDocs documentation with all optional dependencies
	$(ECHO) "$(YELLOW)Building documentation...$(NC)"
	@if ! command -v $(MKDOCS) >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠ mkdocs not found - installing docs dependencies...$(NC)"; \
		$(PIP) install -e ".[docs]"; \
	fi
	@echo "$(YELLOW)Installing all optional dependencies for complete API documentation...$(NC)"
	$(Q)$(PIP) install -e ".[docs,rs232]" --quiet
	@echo "$(YELLOW)Building MkDocs site...$(NC)"
	$(Q)$(MKDOCS) build --clean
	@echo "$(GREEN)✓$(NC) Documentation built in $(DOCS_BUILD_DIR)/"
	@echo "$(YELLOW)Open:$(NC) file://$(PWD)/$(DOCS_BUILD_DIR)/index.html"

docs-serve: ## Serve documentation locally with live reload
	$(ECHO) "$(YELLOW)Starting MkDocs development server...$(NC)"
	@if ! command -v $(MKDOCS) >/dev/null 2>&1; then \
		echo "$(YELLOW)⚠ mkdocs not found - installing docs dependencies...$(NC)"; \
		$(PIP) install -e ".[docs]"; \
	fi
	$(Q)$(PIP) install -e ".[docs,rs232]" --quiet
	$(Q)$(MKDOCS) serve

clean-docs: ## Clean documentation build artifacts
	$(ECHO) "$(YELLOW)Cleaning documentation build...$(NC)"
	$(Q)rm -rf $(DOCS_BUILD_DIR)/
	@echo "$(GREEN)✓$(NC) Documentation build cleaned"

# =============================================================================
# Docker
# =============================================================================
docker-build: ## Build Docker image
	$(ECHO) "$(YELLOW)Building Docker image...$(NC)"
	$(Q)docker build -t $(PROJECT_DISPLAY_NAME) .
	@echo "$(GREEN)✓$(NC) Docker image built"

docker-test: ## Run tests in Docker
	$(ECHO) "$(YELLOW)Running tests in Docker...$(NC)"
	$(Q)docker run --rm $(PROJECT_DISPLAY_NAME) $(PYTHON) -m pytest
	@echo "$(GREEN)✓$(NC) Docker tests completed"

# =============================================================================
# Internal/Support Targets
# =============================================================================
validate-config: ## Validate project configuration
	@echo "$(YELLOW)Validating project configuration...$(NC)"
	@$(PYTHON3) -c "import tomllib; print('✓ pyproject.toml is valid')" 2>/dev/null || (echo "$(RED)✗ pyproject.toml is invalid$(NC)" && exit 1)
	@if [ ! -f "pyproject.toml" ]; then \
		echo "$(RED)✗ pyproject.toml not found$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✓$(NC) Configuration validated"

ensure-venv: ## Ensure virtual environment exists
	@if [ ! -d "$(VENV_DIR)" ]; then \
		echo "$(RED)Virtual environment not found. Run 'make install' first.$(NC)"; \
		exit 1; \
	fi

check-project-structure: ## Validate project structure and required files
	@echo "$(YELLOW)Project Structure Validation:$(NC)"
	@FAILED=0; \
	if [ -d "src/$(PROJECT_NAME)" ]; then echo "$(GREEN)✓$(NC) Source directory exists"; else echo "$(RED)✗$(NC) Source directory missing"; FAILED=1; fi; \
	if [ -d "tests" ]; then echo "$(GREEN)✓$(NC) Tests directory exists"; else echo "$(RED)✗$(NC) Tests directory missing"; FAILED=1; fi; \
	if [ -f "README.md" ]; then echo "$(GREEN)✓$(NC) README.md exists"; else echo "$(RED)✗$(NC) README.md missing"; FAILED=1; fi; \
	if [ -f "SECURITY.md" ]; then echo "$(GREEN)✓$(NC) Security policy exists"; else echo "$(RED)✗$(NC) Security policy missing"; FAILED=1; fi; \
	if [ -f ".github/workflows/pr-validation.yml" ] && [ -f ".github/workflows/release.yml" ]; then echo "$(GREEN)✓$(NC) CI/CD workflows exist"; else echo "$(RED)✗$(NC) CI/CD workflows missing"; FAILED=1; fi; \
	if [ $$FAILED -eq 1 ]; then echo "$(RED)✗$(NC) Project structure validation failed"; exit 1; else echo "$(GREEN)✓$(NC) Project structure validation passed"; fi
