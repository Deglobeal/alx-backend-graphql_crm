# 🧭 Complete Setup Guide  
**alx-backend-graphql_crm** – from zero to running with **GraphQL**, **Celery**, **Redis**, **Celery-Beat**, **Celery Tasks**, and **Django-Crontab**.

---

step 1. Prerequisites

| Tool | Install / Verify |
|------|------------------|
| **Python** | `python --version` (≥3.9) |
| **Git** | `git --version` |
| **Redis** | Linux/WSL: `sudo apt install redis-server`<br>macOS: `brew install redis`<br>Windows: [Download MSI](https://github.com/microsoftarchive/redis/releases) |

---

step 2. Clone & Enter Project

```bash
git clone https://github.com/<your-org>/alx-backend-graphql_crm.git
cd alx-backend-graphql_crm
```

---

step 3. Python Environment

```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

> `requirements.txt` already contains all packages.

---
step 4. Configure Django Settings

Ensure these lines exist in **crm/settings.py** (or `alx_backend_graphql/settings.py`):

```python
INSTALLED_APPS += [
    "django_celery_beat",
    "django_crontab",
]

CELERY_BROKER_URL     = "redis://localhost:6379/0"
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"
CELERY_TIMEZONE       = "UTC"

from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    "generate-crm-report": {
        "task": "crm.tasks.generate_crm_report",
        "schedule": crontab(day_of_week=1, hour=6, minute=0),
    },
}

CRONJOBS = [
    ('*/5 * * * *', 'crm.cron.log_crm_heartbeat'),
    ('0 9 * * *',   'crm.cron.updateLowStockProducts'),
]
```

---

step 5. Database Migrations

```bash
python manage.py migrate
```

---

step 6. Start Redis

| OS | Command |
|----|---------|
| Linux/WSL | `sudo service redis-server start` |
| macOS | `brew services start redis` |
| Windows | Double-click `redis-server.exe` |

Verify:
```bash
redis-cli ping  # → PONG
```

---

## 7. Launch Django

```bash
python manage.py runserver
```
GraphQL endpoint: [http://localhost:8000/graphql](http://localhost:8000/graphql)

---

## 8. Start Celery Services

| Terminal 1 – Worker |
|---------------------|
| `celery -A alx_backend_graphql worker -l info` |

| Terminal 2 – Scheduler |
|------------------------|
| `celery -A alx_backend_graphql beat -l info` |

> Replace `alx_backend_graphql` with `crm` if your project is named `crm`.

---

## 9. Enable Django-Crontab

```bash
python manage.py crontab add
```

---

## 10. Verify Everything Works

### a) GraphQL playground
Visit [http://localhost:8000/graphql](http://localhost:8000/graphql)

### b) Manual Celery task
```bash
celery -A alx_backend_graphql call crm.tasks.generate_crm_report
```

### c) Check logs
```bash
cat /tmp/crm_report_log.txt
cat /tmp/crm_heartbeat_log.txt
cat /tmp/low_stock_updates_log.txt
```

---

## 11. Stop Services

- **Worker** & **Beat**: `Ctrl + C` in each terminal  
- **Redis**: `redis-cli shutdown` (Linux/WSL) or close window (Windows)

---

## 12. Troubleshooting

| Error | Fix |
|-------|-----|
| `ModuleNotFoundError: django_celery_beat` | `pip install django-celery-beat` |
| `Redis connection refused` | Ensure `redis-server` is running |
| `Django settings not found` | `export DJANGO_SETTINGS_MODULE=alx_backend_graphql.settings` (Linux/WSL) or `set DJANGO_SETTINGS_MODULE=alx_backend_graphql.settings` (Windows) |
| `404 on /` | Django root route not defined (see `urls.py`) |

---

