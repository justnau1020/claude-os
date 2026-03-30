---
name: db-migration
description: Guide through a database schema change. Use when you need to modify the database schema, add columns, create tables, or run migrations.
disable-model-invocation: true
argument-hint: <migration-description>
---

# Database Migration

Guide a database schema change: $ARGUMENTS

## Steps

### 1. Modify the model

Update the relevant model in the project's model/schema directory. ORM classes (SQLModel, SQLAlchemy, Prisma, etc.) define both the application model and the database schema.

### 2. Create migration

Generate the migration using the project's migration tool:

```bash
# Alembic (Python/SQLAlchemy)
alembic revision --autogenerate -m "$ARGUMENTS"

# Prisma (TypeScript/Node)
npx prisma migrate dev --name "$ARGUMENTS"

# Django
python manage.py makemigrations
```

Review the generated migration before applying.

### 3. Database-specific limitations

**SQLite** has limited ALTER TABLE support:
- Can ADD COLUMN
- Cannot DROP COLUMN (before SQLite 3.35)
- Cannot ALTER COLUMN type
- For complex changes, may need to recreate the table

**PostgreSQL/MySQL** support most ALTER TABLE operations but watch for:
- Lock contention on large tables
- Default values requiring table rewrites

If the migration requires unsupported operations, create a manual migration that:
1. Creates a new table with the desired schema
2. Copies data from the old table
3. Drops the old table
4. Renames the new table

### 4. Backup first

Before running any migration on production data:
```bash
# SQLite
cp database.db database.db.backup

# PostgreSQL
pg_dump dbname > backup.sql
```

### 5. Apply migration

```bash
# Alembic
alembic upgrade head

# Prisma
npx prisma migrate deploy

# Django
python manage.py migrate
```

### 6. Test

Write tests to verify:
- New schema works with existing data
- Migration is reversible (if supported by the migration tool)
- Application still functions correctly with the new schema
