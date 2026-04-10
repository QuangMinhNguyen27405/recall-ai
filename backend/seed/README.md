## Seed Data

This folder contains a script and sample `.txt` files to seed:
- 1 user
- 1 workspace
- multiple files

The script uploads files to S3, inserts corresponding rows in PostgreSQL, and then runs the ingestion pipeline for each seeded file.

### Run

From the `backend/` directory:

```bash
poetry run python seed/seed_data.py
```

Drop all tables:

```bash
poetry run python seed/seed_data.py drop-all
```

Drop all tables, then seed again:

```bash
poetry run python seed/seed_data.py reset
```

If LocalStack/S3 is unavailable, seed database rows only:

```bash
poetry run python seed/seed_data.py reset --skip-s3
```

If you want to upload and seed rows without running ingestion:

```bash
poetry run python seed/seed_data.py reset --skip-ingestion
```

### Seeded entities

- User email: `seed.student@recallai.dev`
- Workspace name: `Biology 101`
- Files: all `.txt` files in `seed/files/`

### Notes

- Script is idempotent for the same user/workspace/file keys.
- S3 keys use `/users/{user_id}/workspaces/{workspace_id}/files/{filename}`.
