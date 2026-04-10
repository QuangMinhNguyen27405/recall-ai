## Seed Data

This folder contains a script and sample `.txt` files to seed:
- 1 user
- 1 workspace
- multiple files

The script uploads files to S3 and inserts corresponding rows in PostgreSQL.

### Run

From the `backend/` directory:

```bash
poetry run python ../seed/seed_data.py
```

Drop all tables:

```bash
poetry run python ../seed/seed_data.py drop-all
```

Drop all tables, then seed again:

```bash
poetry run python ../seed/seed_data.py reset
```

If LocalStack/S3 is unavailable, seed database rows only:

```bash
poetry run python ../seed/seed_data.py reset --skip-s3
```

### Seeded entities

- User email: `seed.student@recallai.dev`
- Workspace name: `Biology 101`
- Files: all `.txt` files in `seed/files/`

### Notes

- Script is idempotent for the same user/workspace/file keys.
- S3 keys use `seed/workspaces/{workspace_id}/{filename}`.
