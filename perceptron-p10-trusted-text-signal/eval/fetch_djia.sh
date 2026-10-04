#!/usr/bin/env bash
# Kaggle "Daily News for Stock Market Prediction" (aaron7sun/stocknews) via a GitHub mirror; no Kaggle
# credentials on this machine. Verifies git blob SHAs (the news file's blob is identical in two
# independent mirrors: alakamale/... and ShravanChintha/...). ~5.8 MB into .data/kaggle_djia/ (gitignored).
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p .data/kaggle_djia
B=https://raw.githubusercontent.com/alakamale/Deep-Learning-Stock-Market-Prediction-using-News-Headline-/HEAD/dataset
curl -sfL -o .data/kaggle_djia/Combined_News_DJIA.csv "$B/Combined_News_DJIA.csv"
curl -sfL -o .data/kaggle_djia/DJIA.csv "$B/DJIA.csv"
[ "$(git hash-object .data/kaggle_djia/Combined_News_DJIA.csv)" = 9a7899b5c6817c65d57d47bc0cbde673c9a64add ]
[ "$(git hash-object .data/kaggle_djia/DJIA.csv)" = e3faf70c1dc918dd7415a116e597bab4ad3e0493 ]
echo "DJIA data OK"
