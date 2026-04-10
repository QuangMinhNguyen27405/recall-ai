# RecallAI Plan

## Product Direction

RecallAI is a RAG-powered study app for students. The core workflow is:

1. A user creates a workspace.
2. The user uploads files into that workspace.
3. Files are ingested into OpenSearch.
4. Chat and study tools operate within the workspace context.

The workspace is the main retrieval boundary. Each workspace should feel like an isolated study folder with its own sources, chat history, and future study artifacts.

## Current State

### Backend

Implemented backend modules:

- `users`
- `workspaces`
- `files`
- `chat_sessions`
- `pipeline/ingestion.py`

Current backend architecture:

```text
router -> service -> crud -> model/db
```

Responsibilities are now split as follows:

- Routers handle HTTP transport only.
- Services own business logic, orchestration, and HTTP-facing exceptions.
- CRUD modules are database-only.

Current backend files:

```text
backend/src/app/
├── api/router.py
├── config/
│   ├── logger.py
│   └── settings.py
├── db/session.py
├── users/
│   ├── model.py
│   ├── schemas.py
│   ├── crud.py
│   ├── service.py
│   └── router.py
├── workspaces/
│   ├── model.py
│   ├── schemas.py
│   ├── crud.py
│   ├── service.py
│   └── router.py
├── files/
│   ├── model.py
│   ├── schemas.py
│   ├── crud.py
│   ├── service.py
│   └── router.py
├── chat_sessions/
│   ├── model.py
│   ├── schemas.py
│   ├── crud.py
│   ├── service.py
│   └── router.py
└── pipeline/
    └── ingestion.py
```

### Data Layer

Current entities:

- `users`
- `workspaces`
- `files`
- `chat_sessions`

Current file lifecycle:

- `unprocessed`
- `processing`
- `ready`
- `error`

### Local Infrastructure

Current local services in [`compose-native.yaml`](/Users/minh/Code/recall-ai/compose-native.yaml):

- PostgreSQL
- LocalStack S3
- OpenSearch
- OpenSearch Dashboards

Key local endpoints:

- PostgreSQL: `localhost:5432`
- LocalStack: `http://localhost:4566`
- OpenSearch: `http://localhost:9200`
- Dashboards: `http://localhost:5601`

### Seed Flow

The seed flow is implemented in [`backend/seed/seed_data.py`](/Users/minh/Code/recall-ai/backend/seed/seed_data.py).

What it does now:

- creates the schema if needed
- seeds the demo user and workspace
- uploads seed files to LocalStack S3
- runs ingestion for each seeded file
- prints file ingestion results

Seeded file keys use:

```text
/users/{user_id}/workspaces/{workspace_id}/files/{filename}
```

## API Status

Current implemented endpoints:

### Users

- `POST /api/users`
- `GET /api/users`
- `GET /api/users/{user_id}`
- `DELETE /api/users/{user_id}`

### Workspaces

- `POST /api/workspaces`
- `GET /api/workspaces`
- `GET /api/workspaces/{workspace_id}`
- `DELETE /api/workspaces/{workspace_id}`

### Files

- `POST /api/files/presigned-url`
- `GET /api/files`
- `GET /api/files/{file_id}`
- `DELETE /api/files/{file_id}`

### Chat Sessions

- `POST /api/chat-sessions`
- `GET /api/chat-sessions`
- `GET /api/chat-sessions/{chat_session_id}`
- `DELETE /api/chat-sessions/{chat_session_id}`

## Near-Term Priorities

### Phase 1: Stabilize the Core Data + Ingestion Path

Goal: make the current backend reliable before expanding the feature set.

Tasks:

- Add Alembic migrations for the current schema.
- Add backend tests for router, service, and CRUD layers.
- Validate file upload flow end-to-end against LocalStack and OpenSearch.
- Improve ingestion error handling and logging.
- Add health checks and smoke-test commands for local development.

Definition of done:

- schema is reproducible through migrations
- seed works consistently in local dev
- upload -> ingest -> ready flow is tested

### Phase 2: Retrieval + QA Layer

Goal: make uploaded content queryable in a workspace-scoped chat experience.

Tasks:

- Add a retrieval module for OpenSearch queries.
- Filter retrieval by `workspace_id`.
- Add answer generation endpoint using retrieved chunks.
- Add source citations in responses.
- Add basic streaming support if the UI needs it.

Definition of done:

- user can ask questions against one workspace
- responses include source references
- retrieval stays scoped to the active workspace

### Phase 3: Notes and Study Workflows

Goal: support more than raw file upload.

Tasks:

- Add text-note creation flow.
- Reuse the same ingestion pipeline for text notes.
- Persist workspace-scoped chat history cleanly.
- Add derived study artifacts such as flashcards, summaries, and quizzes.

Definition of done:

- user can upload files and create notes
- both content types are retrievable
- study artifacts can be generated from workspace context

### Phase 4: Product Reliability and UX

Goal: make the app pleasant and dependable.

Tasks:

- Improve frontend information architecture.
- Add file status indicators in the UI.
- Add retry behavior for ingestion failures.
- Add observability for pipeline failures and slow requests.
- Harden validation, ownership checks, and error messages.

Definition of done:

- failures are visible and actionable
- UI reflects real backend state
- core workflows are debuggable in local and staging environments

## Frontend Plan

The current frontend is still lightweight and component-oriented. It needs to be shaped around the real backend workflows rather than placeholder pages.

Immediate frontend priorities:

- Build a workspace-oriented shell.
- Add file upload UI for presigned S3 uploads.
- Add file list and ingestion status display.
- Add chat UI wired to future retrieval endpoints.
- Add empty, loading, and error states that match backend status.

## Architecture Rules

These rules should stay enforced going forward:

- Routers should stay thin.
- Services should own business logic and orchestration.
- CRUD should remain database-only.
- Ingestion should be reusable from both seed and real upload flows.
- Workspace ownership checks should happen before creating dependent records.

## Known Gaps

These areas are still missing or incomplete:

- no migrations committed yet
- no dedicated retrieval service yet
- no chat answer endpoint yet
- no text-note route yet
- no comprehensive automated test coverage yet
- no production-ready auth model yet

## Recommended Next Tasks

Suggested order for the next implementation pass:

1. Add Alembic and create the initial migration.
2. Add backend tests for services and API routes.
3. Implement retrieval service and chat answer endpoint.
4. Add text-note creation and ingestion flow.
5. Connect the frontend to workspace, file, and chat APIs.

