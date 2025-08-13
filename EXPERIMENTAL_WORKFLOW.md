# Experimental Development Workflow 🧪

## Overview
This document outlines the workflow for experimental development using a private fork strategy.

## Repository Structure

- **Main Repository** (Public): `kansofy-trade` - Stable, production-ready code
- **Experimental Repository** (Private): `kansofy-trade-experimental` - Sandbox for testing and experimentation

## Setup Instructions

### 1. Create Private Experimental Repository

**Note**: GitHub doesn't allow private forks of your own public repos. Use one of these methods:

#### Method A: GitHub Import (Easiest)
1. Go to https://github.com/new/import
2. Enter URL: `https://github.com/vadik-el/kansofy-trade.git`
3. Name it: `kansofy-trade-experimental`
4. Set visibility to **Private**
5. Click "Begin import"

#### Method B: Manual Clone and Push
1. Create a new **private** repository on GitHub named `kansofy-trade-experimental`
2. Don't initialize with README, license, or .gitignore
3. Run these commands locally:
```bash
git clone https://github.com/vadik-el/kansofy-trade.git kansofy-trade-experimental
cd kansofy-trade-experimental
git remote set-url origin https://github.com/vadik-el/kansofy-trade-experimental.git
git remote add upstream https://github.com/vadik-el/kansofy-trade.git
git push -u origin main
```

### 2. Clone and Configure Experimental Repo

```bash
# Clone the experimental repository
git clone https://github.com/vadik-el/kansofy-trade-experimental.git
cd kansofy-trade-experimental

# Add the main repo as upstream for syncing
git remote add upstream https://github.com/vadik-el/kansofy-trade.git

# Verify remotes
git remote -v
# Should show:
# origin    https://github.com/vadik-el/kansofy-trade-experimental.git (fetch/push)
# upstream  https://github.com/vadik-el/kansofy-trade.git (fetch/push)
```

### 3. Working in Experimental

```bash
# Create experimental branches
git checkout -b experiment/new-feature

# Make changes freely - break things, test wild ideas
# Commit with informal messages if you want
git add .
git commit -m "WIP: testing new approach"

# Push to experimental repo
git push origin experiment/new-feature
```

## Syncing Workflows

### Keep Experimental Updated with Main

```bash
# In experimental repo
git checkout main
git fetch upstream
git merge upstream/main
git push origin main
```

### Moving Successful Experiments to Main Repo

#### Option 1: Cherry-Pick Specific Commits

```bash
# In your main public repo
cd ~/path/to/kansofy-trade

# Add experimental as a remote (one-time setup)
git remote add experimental https://github.com/vadik-el/kansofy-trade-experimental.git

# Fetch and cherry-pick specific commits
git fetch experimental
git cherry-pick <commit-hash>

# Or cherry-pick a range
git cherry-pick <start-hash>..<end-hash>
```

#### Option 2: Create Clean Feature Branch

```bash
# In experimental repo, create clean version
git checkout main
git pull upstream main
git checkout -b feature/clean-implementation

# Manually apply your experimental changes cleanly
# Make clean commits with proper messages
git add .
git commit -m "feat: Add new trading analysis feature"

# Push to experimental
git push origin feature/clean-implementation

# Then in main repo, pull this clean branch
cd ~/path/to/kansofy-trade
git fetch experimental feature/clean-implementation:feature/new-feature
git checkout feature/new-feature
# Create PR or merge to main
```

#### Option 3: Patch File Transfer

```bash
# In experimental repo, create a patch
git format-patch main --stdout > feature.patch

# In main repo, apply the patch
cd ~/path/to/kansofy-trade
git apply --check feature.patch  # Test first
git apply feature.patch          # Apply if test passes
```

## Best Practices

### Experimental Repository

- **Commit freely**: Use WIP commits, experiment without worry
- **Branch naming**: Use prefixes like `experiment/`, `wild/`, `test/`, `maybe/`
- **No PR requirements**: Merge directly to main if you want
- **Keep messy history**: It's private, so document your learning process

### Main Repository

- **Clean commits**: Well-structured commit messages
- **Proper PR process**: Code review, tests, documentation
- **Branch naming**: Professional prefixes like `feature/`, `fix/`, `chore/`
- **Maintain standards**: Follow all coding standards and best practices

## Security Notes

- **Never commit secrets** to experimental repo (it might become public later)
- **Use .env files** for API keys and credentials (already in .gitignore)
- **Be careful** when cherry-picking to not include experimental credentials

## Experimental README Template

Add this to your experimental repo's README:

```markdown
# ⚠️ EXPERIMENTAL REPOSITORY ⚠️

This is a **private experimental fork** of [kansofy-trade](https://github.com/vadik-el/kansofy-trade).

## Warning
- 🔬 Code here is unstable and experimental
- 🐛 Things will break frequently
- 🚧 Not for production use
- 📝 Commit history is messy by design

## Purpose
This repository is used for:
- Testing new features and approaches
- Breaking changes experimentation
- Performance testing
- Learning and exploration

For stable, production-ready code, please see the [main repository](https://github.com/vadik-el/kansofy-trade).
```

## Quick Reference Commands

```bash
# Sync experimental with main
git fetch upstream && git merge upstream/main

# List experiments not in main
git log upstream/main..HEAD --oneline

# See what changed in experiment
git diff upstream/main...HEAD

# Clean up experimental branches
git branch --merged | grep experiment/ | xargs git branch -d

# Archive an experiment before deleting
git tag archive/experiment-name experiment/branch-name
git branch -d experiment/branch-name
```