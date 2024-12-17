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
│  ├─ initializers
│  │  ├─ __init__.py
│  │  └─ populate_roles.py
│  ├─ middleware
│  │  ├─ __init__.py
│  │  └─ standardize_middleware.py
│  ├─ models
│  │  ├─ __init__.py
│  │  ├─ base.py
│  │  ├─ calculations.py
│  │  ├─ customer.py
│  │  ├─ offer.py
│  │  ├─ offer_document.py
│  │  ├─ role.py
│  │  └─ user.py
│  ├─ prompts
│  │  ├─ offer_prompt.txt
│  │  └─ offer_prompt_v1.txt
│  ├─ repositories
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  ├─ customer.py
│  │  └─ offer.py
│  ├─ routers
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  ├─ customer.py
│  │  ├─ location.py
│  │  ├─ offer.py
│  │  └─ user.py
│  ├─ schemas
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  ├─ customer.py
│  │  ├─ location.py
│  │  └─ offer.py
│  ├─ services
│  │  ├─ __init__.py
│  │  ├─ auth.py
│  │  ├─ customer.py
│  │  ├─ extract_documents.py
│  │  ├─ location.py
│  │  ├─ offer.py
│  │  └─ openai.py
│  └─ utils
│     ├─ __init__.py
│     └─ generate_pdf_offer.py
├─ docker-compose-local.yml
├─ docker-compose.yml
├─ main.py
├─ requirements.txt
└─ wait-for-it.sh

```