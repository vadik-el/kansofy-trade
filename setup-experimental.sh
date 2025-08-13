#!/bin/bash

# Setup script for experimental repository workflow
# This script helps set up the private experimental fork

echo "🧪 TradeMCP Experimental Repository Setup"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if GitHub CLI is installed
if command -v gh &> /dev/null; then
    echo -e "${GREEN}✓${NC} GitHub CLI detected"
    
    echo ""
    echo "Would you like to create the fork using GitHub CLI? (y/n)"
    read -r use_cli
    
    if [[ $use_cli == "y" ]]; then
        echo "Creating private experimental repository..."
        
        # Clone the original repo
        git clone https://github.com/vadik-el/kansofy-trade.git kansofy-trade-experimental
        cd kansofy-trade-experimental
        
        # Create new private repo on GitHub
        gh repo create kansofy-trade-experimental --private --description "Private experimental fork of kansofy-trade"
        
        if [ $? -eq 0 ]; then
            # Update remotes
            git remote set-url origin https://github.com/vadik-el/kansofy-trade-experimental.git
            
            # Add upstream remote
            git remote add upstream https://github.com/vadik-el/kansofy-trade.git
            
            echo -e "${GREEN}✓${NC} Experimental repository created and configured!"
        else
            echo -e "${RED}✗${NC} Failed to create fork"
            exit 1
        fi
    fi
else
    echo -e "${YELLOW}!${NC} GitHub CLI not found. Please follow manual steps:"
    echo ""
    echo "1. Go to https://github.com/vadik-el/kansofy-trade"
    echo "2. Click 'Fork' button"
    echo "3. Name it: kansofy-trade-experimental"
    echo "4. After creation, go to Settings → Change visibility → Make private"
    echo ""
    echo "5. Then run these commands:"
    echo ""
    echo "   git clone https://github.com/vadik-el/kansofy-trade-experimental.git"
    echo "   cd kansofy-trade-experimental"
    echo "   git remote add upstream https://github.com/vadik-el/kansofy-trade.git"
fi

echo ""
echo "📚 Next Steps:"
echo "============="
echo "1. Review EXPERIMENTAL_WORKFLOW.md for detailed workflow"
echo "2. Create your first experimental branch:"
echo "   git checkout -b experiment/my-first-test"
echo "3. Start experimenting!"
echo ""
echo "Happy experimenting! 🚀"