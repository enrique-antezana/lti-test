# GitIgnore Configuration for PyLTI1p3

This document explains the `.gitignore` configuration for the PyLTI1p3 project and its examples.

## 🗂️ File Structure

```
PyLTI1p3-2.0.0/
├── .gitignore                    # Main project .gitignore
├── examples/
│   ├── fastapi_example/
│   │   └── .gitignore           # FastAPI-specific ignores
│   ├── django_example/
│   │   └── .gitignore           # Django-specific ignores
│   └── flask_example/
│       └── .gitignore           # Flask-specific ignores
└── pylti1p3/                    # Core library (no .gitignore needed)
```

## 🔐 Security-Critical Files

### **RSA Keys (NEVER COMMIT!)**

These files contain sensitive cryptographic keys and are **automatically ignored**:

```bash
# Private keys
private.key
public.key
*.pem
*.key

# Example locations
examples/*/private.key
examples/*/public.key
```

### **Environment Variables**

```bash
.env
.env.local
.env.production
.env.development
```

### **Configuration Files with Secrets**

```bash
lti_config.json
config.json
secrets.json
```

## 📁 What's Ignored

### **Python Files**

- `__pycache__/` - Compiled Python files
- `*.pyc`, `*.pyo` - Bytecode files
- `*.egg-info/` - Package metadata
- `dist/`, `build/` - Distribution files

### **Virtual Environments**

- `venv/`, `env/`, `ENV/` - Virtual environment directories
- `.venv/` - Modern virtual environment

### **IDE Files**

- `.vscode/` - Visual Studio Code settings
- `.idea/` - PyCharm/IntelliJ settings
- `*.swp`, `*.swo` - Vim swap files

### **OS Files**

- `.DS_Store` - macOS Finder metadata
- `Thumbs.db` - Windows thumbnail cache
- `*~` - Linux backup files

### **Development Files**

- `*.log` - Log files
- `tmp/`, `temp/` - Temporary directories
- `*.bak`, `*.backup` - Backup files

### **Deployment Files**

- `.vercel/` - Vercel deployment cache
- `Dockerfile.dev` - Development Docker files

## 🚨 Security Checklist

Before committing, ensure these files are **NOT** in your repository:

- [ ] No RSA private keys (`private.key`, `*.pem`)
- [ ] No environment files with secrets (`.env*`)
- [ ] No hardcoded credentials in config files
- [ ] No database files with sensitive data
- [ ] No log files with sensitive information

## 🔍 Verify GitIgnore is Working

### **Check what's being tracked:**

```bash
git status
```

### **Check if sensitive files are ignored:**

```bash
# This should return nothing if properly ignored
git check-ignore private.key
git check-ignore .env
```

### **See all ignored files:**

```bash
git status --ignored
```

## 🛠️ Adding New Ignore Patterns

### **For the main project:**

Edit `.gitignore` in the root directory.

### **For specific examples:**

Edit the `.gitignore` in the example directory (e.g., `examples/fastapi_example/.gitignore`).

### **Common patterns to add:**

```bash
# Custom configuration
my_config.json
local_settings.py

# Test files
test_*.py
*_test.py

# Temporary files
*.tmp
*.temp
```

## 🚀 Deployment Considerations

### **Vercel Deployment:**

- `.vercel/` directory is ignored (contains deployment cache)
- Environment variables should be set in Vercel dashboard, not committed

### **Docker Deployment:**

- `Dockerfile.dev` is ignored (development-specific)
- Production `Dockerfile` should be committed

### **CI/CD:**

- Log files are ignored to prevent sensitive data in CI logs
- Temporary build files are ignored

## 📋 Best Practices

1. **Always review** what you're committing with `git status`
2. **Never commit** RSA keys or secrets
3. **Use environment variables** for sensitive configuration
4. **Test your .gitignore** with `git check-ignore`
5. **Keep .gitignore files** in sync across examples

## 🔧 Troubleshooting

### **If you accidentally committed sensitive files:**

1. **Remove from tracking:**

   ```bash
   git rm --cached private.key
   git rm --cached .env
   ```

2. **Add to .gitignore:**

   ```bash
   echo "private.key" >> .gitignore
   echo ".env" >> .gitignore
   ```

3. **Commit the changes:**

   ```bash
   git add .gitignore
   git commit -m "Add sensitive files to .gitignore"
   ```

4. **Force push if needed** (if the sensitive files were already pushed):
   ```bash
   git push --force-with-lease
   ```

### **If .gitignore isn't working:**

1. **Check file location** - .gitignore must be in the repository root or the directory you want to ignore
2. **Check syntax** - No spaces around the `*` in patterns
3. **Clear git cache:**
   ```bash
   git rm -r --cached .
   git add .
   git commit -m "Re-apply .gitignore"
   ```

## 📚 Additional Resources

- [Git Documentation - gitignore](https://git-scm.com/docs/gitignore)
- [GitHub .gitignore templates](https://github.com/github/gitignore)
- [Python .gitignore best practices](https://github.com/github/gitignore/blob/main/Python.gitignore)

Remember: **Security first!** When in doubt, add it to .gitignore rather than risk committing sensitive data.
