# CI/CD Setup Documentation

This document describes the comprehensive CI/CD pipeline setup for Carolina's Diary project.

## Overview

The CI/CD pipeline consists of 6 main workflows:

1. **Frontend CI** - Testing, linting, and building the React frontend
2. **Backend CI** - Testing, linting, and security scanning for FastAPI backend
3. **Deploy** - Automated deployment to staging and production
4. **PR Validation** - Comprehensive pull request validation and analysis
5. **Security** - Advanced security scanning and vulnerability detection
6. **Dependency Updates** - Automated dependency management and updates

## Workflows Details

### 1. Frontend CI (`frontend-ci.yml`)

**Triggers:**
- Push to `master`/`develop` branches
- Pull requests to `master`/`develop`
- Changes in `frontend/` directory

**Jobs:**
- **Test**: Runs on Node.js 18.x and 20.x
  - Install dependencies
  - Lint code
  - Type checking with TypeScript
  - Run tests with coverage
  - Build application
  - Upload artifacts
- **Lighthouse**: Performance and accessibility testing (PR only)
- **Security**: npm audit and secret scanning

### 2. Backend CI (`backend-ci.yml`)

**Triggers:**
- Push to `master`/`develop` branches
- Pull requests to `master`/`develop`
- Changes in `backend/` directory

**Jobs:**
- **Test**: Runs on Python 3.9, 3.10, 3.11
  - Install dependencies
  - Lint with flake8
  - Format check with black
  - Type check with mypy
  - Run tests with pytest
  - Coverage reporting
- **Security**: Safety check, Bandit scan, Semgrep analysis
- **Docker**: Build and test Docker images

### 3. Deploy (`deploy.yml`)

**Triggers:**
- Push to `master` branch
- Manual workflow dispatch

**Jobs:**
- **Build and Push**: Creates Docker images for both frontend and backend
- **Deploy Staging**: Deploys to staging environment
- **Deploy Production**: Deploys to production with GitHub releases

### 4. PR Validation (`pr-validation.yml`)

**Triggers:**
- Pull request events (opened, synchronize, reopened)

**Jobs:**
- **Validate PR**:
  - Semantic PR title validation
  - Branch naming convention checks
  - Commit message validation
  - Large file detection
  - Sensitive file scanning
  - Auto-generated PR summaries
- **Size Analysis**: Bundle size analysis and comparison
- **Accessibility**: Automated accessibility testing

### 5. Security (`security.yml`)

**Triggers:**
- Scheduled (every Monday at 6 AM UTC)
- Push to main branches
- Pull requests
- Manual trigger

**Jobs:**
- **CodeQL**: Static analysis for JavaScript and Python
- **Dependency Review**: License and vulnerability checks (PR only)
- **NPM Audit**: Frontend security scanning
- **Python Security**: Safety and Bandit scanning
- **Docker Security**: Trivy container scanning
- **Secrets Scan**: TruffleHog secret detection
- **License Compliance**: License compatibility verification

### 6. Dependency Updates (`dependency-updates.yml`)

**Triggers:**
- Scheduled (every Monday at 8 AM UTC)
- Manual trigger

**Jobs:**
- **Update Dependencies**: Automated dependency updates with PR creation
- **Update GitHub Actions**: Renovate bot for action updates
- **Security Advisories**: Automated security issue creation

## Required Secrets and Variables

### Secrets (Repository Settings → Secrets and variables → Actions)

```
GITHUB_TOKEN                 # Automatically provided
FIREBASE_API_KEY            # Firebase configuration
```

### Variables

```
REACT_APP_API_URL           # API endpoint URL
FIREBASE_AUTH_DOMAIN        # Firebase auth domain
FIREBASE_PROJECT_ID         # Firebase project ID
```

## Environment Setup

### GitHub Repository Settings

1. **Enable GitHub Actions**:
   - Go to Settings → Actions → General
   - Allow all actions and reusable workflows

2. **Branch Protection Rules**:
   ```
   Branch: master
   ✅ Require status checks to pass before merging
   ✅ Require branches to be up to date before merging
   ✅ Require pull request reviews before merging
   ✅ Dismiss stale PR approvals when new commits are pushed
   ✅ Require review from code owners
   ✅ Include administrators
   ```

3. **Required Status Checks**:
   - Frontend CI / test
   - Backend CI / test
   - PR Validation / validate-pr
   - Security / codeql

### Local Development Setup

1. **Pre-commit Hooks** (recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

2. **Branch Naming Convention**:
   ```
   feature/description    # New features
   fix/description       # Bug fixes
   hotfix/description    # Critical fixes
   release/version       # Release branches
   chore/description     # Maintenance tasks
   docs/description      # Documentation
   refactor/description  # Code refactoring
   test/description      # Test improvements
   ```

3. **Commit Message Format**:
   ```
   type(scope): description

   Examples:
   feat(auth): add Google OAuth integration
   fix(api): resolve database connection timeout
   docs(readme): update installation instructions
   ```

## Monitoring and Alerts

### CodeQL Security Alerts
- Automatic security alerts for code vulnerabilities
- Results appear in Security → Code scanning alerts

### Dependabot Alerts
- Automatic vulnerability alerts for dependencies
- Results appear in Security → Dependabot alerts

### Workflow Notifications
- Failed workflows send notifications to repository admins
- Security issues automatically create GitHub issues

## Performance Budgets

### Frontend Performance Targets
- **Interactive**: < 3 seconds
- **First Meaningful Paint**: < 1 second
- **JavaScript Bundle**: < 125 KB
- **Total Bundle**: < 300 KB

### Accessibility Requirements
- **Minimum Score**: 90/100
- **Automated axe-core testing** on every PR

## Troubleshooting

### Common Issues

1. **Workflow Permissions**:
   ```yaml
   permissions:
     contents: read
     security-events: write
     actions: read
   ```

2. **Dependency Cache Issues**:
   ```bash
   # Clear npm cache
   npm cache clean --force

   # Clear pip cache
   pip cache purge
   ```

3. **Docker Build Failures**:
   - Check Dockerfile syntax
   - Verify base image availability
   - Review build context size

### Debug Commands

```bash
# Test workflows locally (using act)
act -j test

# Validate workflow syntax
actionlint .github/workflows/*.yml

# Test Docker builds locally
docker build -f backend/Dockerfile backend/
docker build -f frontend/Dockerfile frontend/
```

## Deployment Environments

### Staging
- **Trigger**: Push to `develop` branch
- **Environment**: staging
- **URL**: https://staging.carolinas-diary.com

### Production
- **Trigger**: Push to `master` branch
- **Environment**: production
- **URL**: https://carolinas-diary.com
- **Features**:
  - Automatic GitHub releases
  - Production environment protection rules
  - Manual approval required

## Security Features

- **CodeQL static analysis** for security vulnerabilities
- **Dependency scanning** with automated PRs for updates
- **Container vulnerability scanning** with Trivy
- **Secret detection** with TruffleHog
- **License compliance** verification
- **Security advisory monitoring** with automatic issue creation

## Contributing

When contributing to this project:

1. **Follow branch naming conventions**
2. **Write semantic commit messages**
3. **Ensure all CI checks pass**
4. **Add tests for new features**
5. **Update documentation as needed**

All pull requests must pass the complete CI/CD pipeline before merging.

---

For questions or issues with the CI/CD pipeline, please create an issue with the `ci/cd` label.
