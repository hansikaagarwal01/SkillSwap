# AGENTS.md — SkillSwap JKLU Development Guidelines

## Project Overview
SkillSwap JKLU is a DBMS academic project for JK Lakshmipat University, Jaipur.
A university peer-mentoring, skill-sharing, and student marketplace platform.

## Operating Rules
1. **Work in phases:** Verify commands at each gate, record real outputs, and list passes/failures.
2. **Never claim something works without real execution.** Unrun commands must be marked `UNVERIFIED`.
3. **Roll_No is universal PK:** No `student_id` or `id` for student. Immutable via profile edit. Matches regex `^(20[0-9]{2})(BTECH|BBA|BDES)[0-9]{3}$`.
4. **Programs:** Only `BTECH`, `BBA`, `BDES`.
5. **Emails:** Must strictly end with `@jklu.edu.in`. No lookalike domains (`evil-jklu.edu.in`, `jklu.edu.in.evil.com`).
6. **Free Sessions & Non-spendable Reputation:** All sessions have `credit_cost = 0`. Reputation points cannot be spent or transferred.
7. **Safe Concurrency:**
   - Session completion uses `SELECT ... FOR UPDATE` + `reputation_awarded` check on `learning_session`.
   - Marketplace purchase uses conditional `UPDATE listing SET status='SOLD', buyer_roll_no=:buyer, sold_at=NOW() WHERE listing_id=:id AND status='AVAILABLE' AND seller_roll_no <> :buyer`.
8. **No Placeholders or Stubs:** All code must be complete, typed, modular, and verified.

## Tech Stack
- **Backend:** Python 3.12+, FastAPI, SQLAlchemy 2.0, Pydantic v2, Alembic, PyMySQL, `email-validator`, Argon2 (`argon2-cffi`), PyJWT, slowapi, pytest + TestClient.
- **Frontend:** React 18+, Vite, Tailwind CSS, React Router v6, Axios, lucide-react, Recharts.
- **Database:** MySQL 8.0+, InnoDB, utf8mb4. Primary dev database `skillswap`, test database `skillswap_test`.

## Directory Scaffolding
- `backend/app/`: FastAPI application code
  - `core/`: Config, security, dependencies
  - `db/`: Engine, session, declarative base
  - `models/`: SQLAlchemy 2.0 models
  - `schemas/`: Pydantic v2 schemas
  - `repositories/`: Raw queries and SQL repository abstractions
  - `services/`: Transactional business logic
  - `routers/`: Thin API endpoints
  - `tests/`: Automated pytest suite
- `backend/alembic/`: Alembic schema migrations
- `backend/database/`:
  - `schema.sql`: Standalone DDL equivalent to Alembic
  - `seed.sql`: Realistic academic seed data
  - `test_queries.sql`: 34 required SQL demonstration queries
- `frontend/`: React + Vite application
- `docs/`:
  - `DECISIONS.md`: Architectural decisions record
  - `PROGRESS.md`: Phased tracker with status and gate outputs
  - `SCHEMA.md`: Normalization breakdown (1NF->3NF/BCNF) and name mapping
  - `ER.md`: Mermaid ER diagram
