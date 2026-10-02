from app.core.db import Base, engine
from app.models import entities

target_metadata = Base.metadata

def run_migrations_online():
    from alembic import context
    with engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction(): context.run_migrations()

run_migrations_online()
