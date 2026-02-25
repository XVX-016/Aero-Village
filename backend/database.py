import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/smavita")

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    # Import models lazily so Base has all table metadata before create_all.
    import models  # noqa: F401

    with engine.begin() as conn:
        if engine.dialect.name == "postgresql":
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS postgis"))
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        Base.metadata.create_all(bind=conn)
        if engine.dialect.name == "postgresql":
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS extracted_features_geom_idx ON extracted_features USING GIST (geom)")
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS extracted_features_project_idx ON extracted_features (project_id)")
            )
            conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS extracted_features_project_ingestion_idx "
                    "ON extracted_features (project_id, ingestion_version)"
                )
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS infrastructure_layers_geom_idx ON infrastructure_layers USING GIST (geom)")
            )
            conn.execute(
                text("CREATE INDEX IF NOT EXISTS infrastructure_layers_project_idx ON infrastructure_layers (project_id)")
            )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
