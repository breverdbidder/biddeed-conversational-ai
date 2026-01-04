# BidDeed.AI Quality Infrastructure

**Deployed:** January 3, 2026  
**Purpose:** Enterprise-grade code quality for foreclosure analysis platform

---

## 🚀 Quick Start

```bash
# 1. Install pre-commit
pip install pre-commit

# 2. Install hooks
pre-commit install

# 3. Run on all files (first time)
pre-commit run --all-files

# 4. Commit as usual - hooks run automatically
git commit -m "feat: Add lien detection logic"
```

---

## 📦 Installed Tools

### Ruff (Linter + Formatter)
- **Replaces:** flake8, black, isort, pyupgrade
- **Speed:** 10-100x faster than alternatives
- **Config:** `ruff.toml`

```bash
# Run manually
ruff check .              # Lint
ruff check --fix .        # Lint + auto-fix
ruff format .             # Format
```

### MyPy (Static Type Checker)
- **Purpose:** Catch type errors before runtime
- **Config:** `mypy.ini`

```bash
# Run manually
mypy src/
```

### Bandit (Security Scanner)
- **Purpose:** Detect security vulnerabilities
- **Config:** `pyproject.toml`

```bash
# Run manually
bandit -r src/
```

### Detect-Secrets
- **Purpose:** Prevent API keys/passwords in commits
- **Config:** `.secrets.baseline`

```bash
# Scan for secrets
detect-secrets scan
```

---

## 🔧 Configuration Files

| File | Purpose |
|------|---------|
| `ruff.toml` | Linting + formatting rules |
| `mypy.ini` | Type checking configuration |
| `pyproject.toml` | Bandit security config |
| `.pre-commit-config.yaml` | Git hook definitions |
| `.yamllint.yml` | YAML file linting |
| `.secrets.baseline` | Known secrets allowlist |

---

## ✅ Pre-commit Hooks

Hooks run automatically on `git commit`:

1. **Ruff** - Lint and format Python code
2. **MyPy** - Check type annotations
3. **Detect-Secrets** - Scan for API keys
4. **Trailing Whitespace** - Remove extra spaces
5. **End-of-File Fixer** - Ensure newline at EOF
6. **YAML Check** - Validate YAML syntax
7. **JSON Check** - Validate JSON syntax
8. **Large Files** - Block files >1MB
9. **Merge Conflicts** - Detect conflict markers
10. **Bandit** - Security vulnerability scan

---

## 🚨 Bypass Hooks (Emergency Only)

```bash
# Skip hooks for urgent hotfix
git commit --no-verify -m "hotfix: Critical production issue"
```

⚠️ **Use sparingly** - bypassed commits will fail CI/CD

---

## 📊 GitHub Actions

### Quality Check Workflow
- **Triggers:** PRs to main/develop, pushes to main
- **Runs:** Ruff + MyPy
- **Fails:** Only on linting errors (type errors are warnings)

See: `.github/workflows/quality_check.yml`

---

## 🎯 Code Quality Standards

### Required (Blocking)
- ✅ Ruff linting passes
- ✅ Ruff formatting applied
- ✅ No secrets detected
- ✅ YAML/JSON valid

### Recommended (Non-blocking)
- ⚠️ MyPy type checks (improve over time)
- ⚠️ Test coverage >70%

---

## 🔍 Ignoring Rules

### File-level ignore
```python
# ruff: noqa: E501
# Ignore line-too-long for this entire file
```

### Line-level ignore
```python
result = some_long_function()  # noqa: PLR0913
```

### Type ignore
```python
data: Any = external_api()  # type: ignore[misc]
```

---

## 📈 Expected Results

### After Initial Run
```bash
$ ruff check --fix .
Found 347 errors → Fixed 324 automatically
Remaining: 23 manual fixes needed
```

### After Pre-commit Install
```bash
$ git commit -m "Add feature"

ruff............................Passed ✅
mypy............................Passed ✅
detect-secrets..................Passed ✅
trailing-whitespace.............Passed ✅
end-of-file-fixer...............Passed ✅

[main 1a2b3c4] Add feature
 5 files changed, 120 insertions(+)
```

---

## 🐛 Troubleshooting

### "MyPy errors on third-party libraries"
**Solution:** Already configured in `mypy.ini`
```ini
[mypy-langchain.*]
ignore_missing_imports = True
```

### "Ruff complaining about line length"
**Solution:** Already set to 100 chars in `ruff.toml`
```toml
line-length = 100
```

### "Detect-secrets flagging false positives"
**Solution:** Add to `.secrets.baseline`
```bash
detect-secrets scan --update .secrets.baseline
```

---

## 🎓 Learning Resources

- **Ruff:** https://docs.astral.sh/ruff/
- **MyPy:** https://mypy.readthedocs.io/
- **Pre-commit:** https://pre-commit.com/

---

## 📝 Maintenance

### Update pre-commit hooks (weekly)
```bash
pre-commit autoupdate
```

### Update ruff (as needed)
```bash
pip install --upgrade ruff
pre-commit run --all-files
```

---

**Questions?** Check deployment logs or PROJECT_STATE.json
