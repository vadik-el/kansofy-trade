#!/bin/bash

# Script to push existing code to your private experimental repository

echo "🚀 Pushing TradeMCP code to private experimental repo..."
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Option 1: If you want to work in a separate directory
echo -e "${YELLOW}Option 1:${NC} Clone to a new directory (Recommended)"
echo "Run these commands:"
echo ""
echo "  cd .."
echo "  git clone https://github.com/vadik-el/kansofy-trade.git kansofy-trade-experimental"
echo "  cd kansofy-trade-experimental"
echo "  git remote set-url origin git@github.com:vadik-el/kansofy-trade-experimental.git"
echo "  git remote add upstream https://github.com/vadik-el/kansofy-trade.git"
echo "  git push -u origin main"
echo ""
echo "=================================================="
echo ""

# Option 2: Push from current directory to experimental
echo -e "${YELLOW}Option 2:${NC} Push current code directly to experimental"
echo "Run these commands:"
echo ""
echo "  git remote add experimental git@github.com:vadik-el/kansofy-trade-experimental.git"
echo "  git push experimental main"
echo ""
echo "Then clone the experimental repo separately for experimental work:"
echo "  cd .."
echo "  git clone git@github.com:vadik-el/kansofy-trade-experimental.git"
echo ""
echo "=================================================="
echo ""

echo -e "${GREEN}Recommended workflow:${NC}"
echo "1. Use Option 1 to create a separate experimental directory"
echo "2. Work in kansofy-trade-experimental/ for experiments"
echo "3. Work in kansofy-trade/ for stable development"
echo "4. Cherry-pick successful experiments back to main repo"