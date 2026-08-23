#!/usr/bin/env bash
set -e

REPO_NAME="${1:-nebula-v9}"

echo "Configuring remote for https://github.com/ApurvaRajj/${REPO_NAME}.git ..."
git remote remove origin 2>/dev/null || true
git remote add origin "https://github.com/ApurvaRajj/${REPO_NAME}.git"
git branch -M main

echo "Pushing to GitHub..."
git push -u origin main

echo "✓ Successfully deployed Nebula v9 to GitHub!"
