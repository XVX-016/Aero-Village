from sqlalchemy import Column, String, Float, ForeignKey, DateTime, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from geoalchemy2 import Geometry
from database import Base
import uuid
import datetime

class Village(Base):
    __tablename__ = "villages"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    state = Column(String)
    district = Column(String)
    boundary = Column(Geometry('POLYGON', srid=4326))
    created_at = Column(DateTime, default=datetime.datetime.utcnow)

class Orthophoto(Base):
    __tablename__ = "orthophotos"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    village_id = Column(UUID(as_uuid=True), ForeignKey("villages.id"))
    file_path = Column(String, nullable=False)
    resolution_cm = Column(Float)
    captured_at = Column(DateTime)
    footprint = Column(Geometry('POLYGON', srid=4326))

class ExtractedFeature(Base):
    __tablename__ = "extracted_features"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String, index=True)
    ingestion_version = Column(Integer, default=1, index=True)
    village_id = Column(UUID(as_uuid=True), ForeignKey("villages.id"))
    type = Column(String) # building, road, vegetation, waterbody
    confidence = Column(Float)
    area_sq_m = Column(Float)
    properties = Column(JSONB)
    geom = Column(Geometry('GEOMETRY', srid=4326))

class InfrastructureLayer(Base):
    __tablename__ = "infrastructure_layers"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    project_id = Column(String, index=True)
    village_id = Column(UUID(as_uuid=True), ForeignKey("villages.id"))
    type = Column(String) # sewage, electricity, water_pipeline
    status = Column(String) # proposed, approved, existing
    cost_estimate = Column(Float)
    extra_metadata = Column(JSONB)
    geom = Column(Geometry('LINESTRING', srid=4326))

# For RAG support using pgvector
# Requires: CREATE EXTENSION IF NOT EXISTS vector;
from pgvector.sqlalchemy import Vector

class RAGDocument(Base):
    __tablename__ = "rag_documents"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String)
    source = Column(String)
    content = Column(String) # Chunk text
    embedding = Column(Vector(1536)) # For OpenAI embeddings (1536 dims)
    extra_metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)


class ProjectRun(Base):
    __tablename__ = "project_runs"
    id = Column(String, primary_key=True)
    status = Column(String, nullable=False)
    input_file = Column(String, nullable=False)
    output_dir = Column(String)
    error_message = Column(String)
    extra_metadata = Column(JSONB)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
