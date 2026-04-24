"""
One-time script to create all tables directly.
Run this instead of 'alembic upgrade head' if alembic is giving trouble.
After running this, Alembic is told the migration is already done.
"""
from sqlalchemy import create_engine, text
from app.config import settings

engine = create_engine(settings.database_url)

SETUP_SQL = """
-- Clean up anything leftover
DROP TABLE IF EXISTS team_assignments CASCADE;
DROP TABLE IF EXISTS team_results CASCADE;
DROP TABLE IF EXISTS players CASCADE;
DROP TABLE IF EXISTS rooms CASCADE;
DROP TABLE IF EXISTS alembic_version CASCADE;
DROP TYPE IF EXISTS room_status CASCADE;
DROP TYPE IF EXISTS assignment_status CASCADE;

-- Create types
CREATE TYPE room_status AS ENUM ('open', 'closed');
CREATE TYPE assignment_status AS ENUM ('playing', 'waiting');

-- Create tables
CREATE TABLE rooms (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_code VARCHAR(4) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    creator_token VARCHAR(64) NOT NULL,
    status room_status NOT NULL DEFAULT 'open',
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    closed_at TIMESTAMP
);
CREATE INDEX ix_rooms_room_code ON rooms (room_code);

CREATE TABLE players (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES rooms(id),
    name VARCHAR(50) NOT NULL,
    joined_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_player_name_per_room UNIQUE (room_id, name)
);

CREATE TABLE team_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    room_id UUID NOT NULL REFERENCES rooms(id),
    run_number INTEGER NOT NULL,
    generated_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE team_assignments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    result_id UUID NOT NULL REFERENCES team_results(id),
    player_id UUID NOT NULL REFERENCES players(id),
    team_number INTEGER NOT NULL,
    status assignment_status NOT NULL DEFAULT 'playing'
);

-- Tell Alembic this migration is already applied
CREATE TABLE alembic_version (version_num VARCHAR(32) NOT NULL);
INSERT INTO alembic_version (version_num) VALUES ('001');
"""

with engine.connect() as conn:
    conn.execute(text(SETUP_SQL))
    conn.commit()
    print("All tables created successfully.")
    print("Alembic migration marked as applied.")
