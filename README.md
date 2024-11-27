```
ibgpt-backend
├─ .gitignore
├─ Dockerfile.backend
├─ README.md
├─ alembic
│  ├─ README
│  ├─ env.py
│  ├─ script.py.mako
│  └─ versions
├─ alembic.ini
├─ app
│  ├─ __init__.py
│  ├─ config
│  │  ├─ __init__.py
│  │  └─ config.py
│  ├─ db
│  │  ├─ __init__.py
│  │  └─ database.py
│  ├─ models
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ customers.py
│  │  ├─ offer.py
│  │  ├─ role.py
│  │  └─ user.py
│  ├─ repositories
│  │  ├─ __init__.py
│  │  └─ auth.py
│  ├─ routers
│  │  ├─ __init__.py
│  │  └─ auth.py
│  ├─ schemas
│  │  ├─ __init__.py
│  │  └─ auth.py
│  └─ services
│     ├─ __init__.py
│     └─ auth.py
├─ docker-compose.yml
├─ main.py
├─ requirements.txt
└─ wait-for-it.sh

```