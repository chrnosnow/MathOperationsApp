# Math Operations API

A lightweight FastAPI microservice that exposes three math utilities - integer power, Fibonacci, and factorial - while
recording every call to a SQLite database. Admin-role users can manage the log table; regular users only
call math endpoints. JWT tokens and role links manage access.

---

## ⚡ FastAPI

FastAPI is a modern Python web framework that turns simple, type-hinted functions into high-performance REST endpoints.
It auto-validates inputs, generates interactive Swagger docs at /docs, and runs asynchronously on Uvicorn—so you get
speed, built-in validation, and ready-made documentation with almost no boilerplate.

---

## Live FastAPI API Explorer

![Swagger UI overview](docs/images/swagger-ui.png)

---

## 📈 Prometheus

Prometheus is an open-source metrics monitoring and alerting toolkit that scrapes time-series data from configured targets (like this app’s /metrics endpoint) and stores it for querying, alerting, and dashboarding.
You may also add custom metrics (e.g., math_calls_total) to track specific function calls, sources (cache vs compute), or errors.
To query Prometheus se expressions like up, http_requests_total, math_calls_total.

___

## Live Prometheus API Explorer

![Prometheus UI overview](docs/images/prometheus-ui.png)

---

## ✨ Features

* **LRU-cached math functions** → logarithmic power, fast-doubling Fibonacci, C-backed factorial.
* **Role-based access control** → JWT auth; user role for math endpoints, admin role for full CRUD on the /logs table.
* **Automatic DB bootstrap** → tables (User, Role, UserRoleLink, RequestLog) created on first start; `seed_admin()`
  inserts a default admin.
* **Prometheus metrics** – built-in `/metrics` endpoint (Prometheus text format) for request count, latency, and
  cache-hit ratios; ready to scrape.
* **Pre-commit quality gate** → Black ⇢ isort ⇢ Ruff ⇢ Flake8.
* **Fully async test-suite** → Pytest suite with isolated temporary database fixture.

---

## 🚀 Quick Start

```bash
git clone https://github.com/your-org/MathOperationsApp.git
cd MathOperationsApp
cp .env.example .env                     # set a strong SECRET_KEY inside!
python -m venv .venv && .\.venv\Scripts\Activate
pip install -r requirements.txt -r requirements-dev.txt
pytest -q                        # optional: run tests
uvicorn main:app --reload --port 8080
# open http://localhost:8080/docs for fastapi
# open http://localhost:9090/ for prometheus
```

SQLite file requests.db is created in the project root; it’s already .gitignored.

---

## 📦 Docker (optional)

This project can be run in a Docker container for easy deployment and isolation. To run the API in a Docker container,
you can build and run it with the following commands:

```bash
bash
docker-compose down -v : Stops and removes all services, including volumes (e.g., metrics or DB data).
docker-compose up --build : Builds and starts all services defined in the docker-compose.yml.
```

Or use Rancher Desktop / Kubernetes with the provided k8s/ manifests (Deployment, Service, Secret).

---

## 👥 Contributors

| Name               | Key areas                                                                                                                              |
|--------------------|----------------------------------------------------------------------------------------------------------------------------------------|
| **Irina Morosanu** | • Core FastAPI app & routing<br> • Auth & role-based access control<br>• Math algorithms & caching<br>• Pre-commit config<br>• Testing |
| **Alexandru Baba** | • Project setup<br>• Core FastAPI app & routing<br> • Prometheus `/metrics` integration<br>• Containerization<br>• Testing             |