---
name: neon-postgres
description: >-
  Guides and best practices for working with Lakebase Postgres, the database
  behind Neon. Covers setup, connection methods and drivers, pooled vs direct
  connections, branching, schema migrations, autoscaling, scale-to-zero, instant
  restore, read replicas, connection pooling, IP allow lists, and logical
  replication.
  Use when users ask about "Lakebase Postgres", "Neon setup", "connect to Neon",
  "Neon project", "DATABASE_URL", "serverless Postgres", "Neon CLI", "neon", "Neon MCP",
  "Neon Auth", "@neondatabase/serverless", "@neondatabase/neon-js",
  "scale to zero", "Neon autoscaling", "Neon read replica",
  "Neon connection pooling", or "schema migrations".
metadata:
  parent: neon
  source: https://github.com/neondatabase/agent-skills/tree/main/skills/neon-postgres
---

# Lakebase Postgres

Lakebase Postgres is the database at the core of Neon. It runs on the lakebase architecture — OLTP built directly on cloud object storage — which decouples storage from compute to offer autoscaling, branching, instant restore, and scale-to-zero. It's fully compatible with Postgres and works with any language, framework, or ORM that supports Postgres.

## Setup Flow

### 1. Select the organization and project
Project: `AyuRaksha` (`hidden-wind-77590258`)
Org: `Vishesh` (`org-damp-frost-09319742`)

### 2. Connection Strings

| Use case | Connection type | Suffix / Port |
|---|---|---|
| Web applications, FastAPI, queries | Pooled | `-pooler.us-east-2.aws.neon.tech` (Port 5432/6543) |
| Migrations, DDL, pg_dump | Direct | `.us-east-2.aws.neon.tech` (Port 5432) |

```env
DATABASE_URL=postgresql://neondb_owner:<PASSWORD>@ep-hidden-wind-77590258-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require
DIRECT_URL=postgresql://neondb_owner:<PASSWORD>@ep-hidden-wind-77590258.us-east-2.aws.neon.tech/neondb?sslmode=require
```

### 3. Drivers & Best Practices
- Python / FastAPI: Use `asyncpg` or `psycopg3` with connection pooling, SSL required.
- Enable `pgvector` for embedding search: `CREATE EXTENSION IF NOT EXISTS vector;`
