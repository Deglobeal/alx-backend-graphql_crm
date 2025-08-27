# Celery CRM Report Setup

## 1. Install Redis
- **Linux**: `sudo apt install redis-server`
- **macOS**: `brew install redis && brew services start redis`
- **Windows (WSL)**: `sudo apt install redis-server && sudo service redis-server start`

## 2. Install Python deps
```bash
pip install -r requirements.txt