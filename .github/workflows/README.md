# CI/CD Workflows

GitHub Actions workflows for a Python package.

## Workflows

### `pr-validation.yml` - Pull Request Validation

**Pull Requests:**

- Complete health check (`make health-check`) including:
  - Configuration validation
  - Version compatibility checks
  - Code formatting and quality checks
  - Security audits and dependency checks
  - Comprehensive testing with coverage
  - Package building
- Coverage reporting with PR comments
- Artifact uploads (test packages, reports)

### `release.yml` - Release Management

**Main Branch:**

- Automated release creation via [release-please](https://github.com/googleapis/release-please-action)
- Complete health check validation
- Coverage badge updates
- Package building and PyPI deployment via trusted publisher
- GitHub release with distribution files (.whl)

**_How Release-Please Works:_**

1. **Analyzes commits** since last release using conventional commit format
2. **Creates release PR on a new branch** with updated changelog and version bump
3. **Merging the PR back into main** triggers the actual release workflow:
   - Runs full validation suite
   - Updates coverage badge with released code coverage
   - Builds and publishes package to PyPI
   - Creates GitHub release with assets

**Notes:**

- Dependency updates handled by Dependabot (see `.github/dependabot.yml`)

## Required Secrets

```bash
# Coverage badge (for gist updates)
GIST_SECRET=your_github_personal_access_token_with_gist_scope
GIST_ID=your_coverage_badge_gist_id

# Release-please (if using custom token)
MY_RELEASE_PLEASE_TOKEN=your_github_token_with_repo_scope
```

**Note:** PyPI authentication uses trusted publisher (no API token needed).

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
- [Release-Please Action](https://github.com/googleapis/release-please-action)
- [Conventional Commits](https://www.conventionalcommits.org/)
- [Semantic Versioning](https://semver.org/)
- [PyPI Trusted Publishers](https://docs.pypi.org/trusted-publishers/)
