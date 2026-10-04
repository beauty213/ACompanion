# 🐙 Git Workflow & Cheatsheet for ACompanion

This guide provides the official Git workflow, best practices, and cheat sheet for contributing to **Anchor / ACompanion** (`https://github.com/beauty213/ACompanion.git`).

---

## 📌 Repository Information

- **Remote URL**: `https://github.com/beauty213/ACompanion.git`
- **Default Branch**: `main`
- **Recommended Git Version**: 2.30+

---

## 🚀 Quick Setup

### 1. Clone the Repository
```bash
git clone https://github.com/beauty213/ACompanion.git
cd ACompanion
```

### 2. Verify Remotes
```bash
git remote -v
# Output should show:
# origin  https://github.com/beauty213/ACompanion.git (fetch)
# origin  https://github.com/beauty213/ACompanion.git (push)
```

### 3. Check Current Branch and Status
```bash
git status
git branch -a
```

---

## 🌿 Branching Strategy

| Branch Prefix | Purpose | Example |
|---|---|---|
| `main` | Production / Stable release branch | `main` |
| `feature/` | New features or UI components | `feature/meme-explorer-filters` |
| `fix/` | Bug fixes and patches | `fix/sqlite-cascade-delete` |
| `docs/` | Documentation improvements | `docs/update-readme` |
| `test/` | Adding or updating tests | `test/incident-analysis-suite` |

### Creating and Switching Branches
```bash
# Pull latest main before branching
git checkout main
git pull origin main

# Create and switch to a new branch
git checkout -b feature/your-feature-name

# Or using modern git switch
git switch -c feature/your-feature-name
```

---

## ✍️ Everyday Git Workflow

### 1. Check Changes
```bash
# View modified, added, or deleted files
git status

# Inspect exact code diffs (unstaged changes)
git diff

# Inspect staged diffs
git diff --staged
```

### 2. Stage Changes
```bash
# Stage specific files
git add backend/services/online_meme_service.py frontend/src/components/JournalExpressView.tsx

# Stage all tracked & untracked changes
git add .
```

### 3. Commit with Conventional Commits
Use clean, descriptive commit messages:
```bash
git commit -m "feat: add category filter to online meme explorer"
```

#### Commit Message Format
- `feat: <description>` — New user-facing feature
- `fix: <description>` — Bug fix
- `docs: <description>` — Documentation only changes
- `refactor: <description>` — Code change that neither fixes a bug nor adds a feature
- `test: <description>` — Adding missing tests or correcting existing tests
- `chore: <description>` — Tooling, dependencies, or config changes

### 4. Keep Your Branch Updated (Rebase)
```bash
# Fetch latest updates from remote
git fetch origin

# Rebase your local branch onto the latest main
git pull --rebase origin main
```

### 5. Push to GitHub
```bash
# First time pushing the new branch (sets upstream)
git push -u origin feature/your-feature-name

# Subsequent pushes
git push
```

---

## 🛠️ Helpful Git Recipes

### Stashing Work in Progress (WIP)
When you need to switch tasks without committing unfinished work:
```bash
# Save your working changes
git stash save "WIP: working on pastel palette adjustment"

# List saved stashes
git stash list

# Re-apply the latest stash
git stash pop
```

### Viewing Clean History
```bash
# Pretty one-line history with graph
git log --oneline --graph --decorate -n 10
```

### Undoing Mistakes Safely

| Scenario | Command | Notes |
|---|---|---|
| Unstage a file | `git restore --staged <file>` | Keeps changes in working directory |
| Discard changes in a file | `git restore <file>` | Reverts file to last committed state |
| Amend the last commit | `git commit --amend -m "new message"` | Only if commit hasn't been pushed |
| Undo last commit (keep changes) | `git reset --soft HEAD~1` | Preserves changes as staged |
| Revert a pushed commit | `git revert <commit-hash>` | Creates a safe compensating commit |

---

## 🔀 Merging & Pull Requests

1. **Push your branch** to `origin`:
   ```bash
   git push -u origin feature/your-feature-name
   ```
2. **Open a Pull Request** on GitHub:
   - Navigate to `https://github.com/beauty213/ACompanion/pulls`
   - Click **New pull request**
   - Choose base: `main` <- compare: `feature/your-feature-name`
   - Provide a clear summary and list of changes
3. **Verify Automated Tests**:
   Ensure all tests pass before merging:
   ```bash
   source .venv/bin/activate && PYTHONPATH=. pytest
   ```

---

## 🛡️ Git Hygiene & Privacy Rules for Anchor

- **NEVER** commit personal SQLite databases (`*.db`, `anchor.db`, `data/`).
- **NEVER** commit private virtual environment directories (`.venv/`, `venv/`).
- **NEVER** commit API secrets or personal access tokens.
- Keep `.gitignore` updated at all times.
