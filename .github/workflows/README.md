# CI/CD Workflows

GitHub Actions workflows for a Python package.

## Workflows

### `pr-validation.yml` - Pull Request Validation

**Pull Requests:**

- Quality checks (lint, type-check, security, tests)
- Code formatting validation
- Comprehensive testing with coverage
- Security audits and dependency checks

### `release.yml` - Release Management

**Main Branch:**

- Automated release creation via release-please
- Full project validation and testing
- Package building and PyPI deployment
- GitHub release with distribution files

**Notes:**

- Dependency updates handled by Dependabot (see `.github/dependabot.yml`)

## Required Secrets

```bash
PYPI_API_TOKEN=your_pypi_token_here
```

## Usage

**Feature Development:**

```bash
git commit -m "feat: add new feature"
git push origin feature-branch
# Create PR on GitHub
```

**Bug Fix:**

```bash
git commit -m "fix: resolve issue"
git push origin fix-branch
# Create PR on GitHub
```

**Breaking Change:**

```bash
git commit -m "feat!: breaking change

BREAKING CHANGE: Description of breaking change"
git push origin breaking-branch
# Create PR on GitHub
```

## Monitoring

- **GitHub Actions Tab**: View workflow runs
- **Status Checks**: Required for PR merging
- **Artifacts**: Download test packages and reports

## Resources

- [GitHub Actions](https://docs.github.com/en/actions)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
