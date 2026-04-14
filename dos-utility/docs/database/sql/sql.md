# Table of Contents

* [dos\_utility.database.sql](#dos_utility.database.sql)
  * [get\_async\_session](#dos_utility.database.sql.get_async_session)

<a id="dos_utility.database.sql"></a>

# dos\_utility.database.sql

Provides an async SQLAlchemy session factory for PostgreSQL, using the `asyncpg` driver. The engine is created once (via `lru_cache`) and reused across all sessions.

<a id="dos_utility.database.sql.get_async_session"></a>

#### get\_async\_session

```python
async def get_async_session() -> AsyncGenerator[AsyncSession, None]
```

Async generator that yields an `AsyncSession` bound to the configured PostgreSQL database.
Intended for use as a FastAPI dependency.

**Yields**:

  AsyncGenerator[AsyncSession, None]: A SQLAlchemy async session. The session is automatically
  closed when the generator exits.

**Configuration**:

All settings have defaults for local development:

```env
DB_USERNAME=postgres      # Default: postgres
DB_PASSWORD=password      # Default: password
DB_HOST=localhost         # Default: localhost
DB_PORT=5432              # Default: 5432
DB_NAME=db                # Default: db
```

**Examples**:

As a FastAPI dependency:

  >>> from typing import Annotated
  >>> from fastapi import Depends
  >>> from sqlalchemy.ext.asyncio import AsyncSession
  >>> from dos_utility.database.sql import get_async_session
  >>>
  >>> @app.get("/users")
  >>> async def get_users(session: Annotated[AsyncSession, Depends(get_async_session)]):
  >>>     result = await session.execute(select(User))
  >>>     return result.scalars().all()
