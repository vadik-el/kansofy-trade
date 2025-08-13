# ✅ Experimental Workflow Setup Complete!

## Your Repository Structure

1. **Public Main Repo**: `https://github.com/vadik-el/kansofy-trade`
   - Location: `/Users/vadik/kansofy-trade` (current directory)
   - Purpose: Stable, production-ready code
   - Visibility: Public

2. **Private Experimental Repo**: `git@github.com:vadik-el/kansofy-trade-experimental.git`
   - Purpose: Private experimentation and testing
   - Visibility: Private
   - Status: ✅ Code pushed successfully

## Quick Start Commands

### To start experimenting in a separate directory:
```bash
# Go to parent directory and clone experimental
cd ..
git clone git@github.com:vadik-el/kansofy-trade-experimental.git
cd kansofy-trade-experimental

# Add upstream to sync with main
git remote add upstream https://github.com/vadik-el/kansofy-trade.git

# Create an experimental branch
git checkout -b experiment/my-cool-feature
```

### Working from current directory:
```bash
# You've already added experimental remote, so you can:
# Push branches directly to experimental
git checkout -b experiment/test-feature
# ... make changes ...
git push experimental experiment/test-feature

# Or push any branch to experimental
git push experimental <branch-name>
```

## Syncing Between Repos

### Update experimental with latest from main:
```bash
# In experimental repo directory
git fetch upstream
git checkout main
git merge upstream/main
git push origin main
```

### Cherry-pick from experimental to main:
```bash
# In main repo (current directory)
git fetch experimental
git cherry-pick <commit-hash>
# or
git checkout experimental/<branch-name>
```

## ⚠️ Note About Large Files

Your repo contains a large model file (86MB). Consider:
1. Adding it to `.gitignore` if not needed in experimental
2. Using Git LFS for large files: https://git-lfs.github.com

## Next Steps

1. **Clone experimental repo** in a separate directory for clean separation
2. **Start experimenting** without affecting your public repo
3. **Cherry-pick** successful experiments back to main when ready

Happy experimenting! 🚀