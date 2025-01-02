"""Initial schema

Revision ID: 57fd959e2426
Revises: 
Create Date: 2025-01-02 21:10:57.682552

"""
from typing import Sequence, Union

from alembic import op

revision: str = '57fd959e2426'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        CREATE TABLE public.clubs (
            club_id SERIAL PRIMARY KEY,
            name VARCHAR NOT NULL
        );

        CREATE TABLE public.constraints (
            constraint_id SERIAL PRIMARY KEY,
            schedule_entry_id INTEGER NOT NULL,
            team_id INTEGER NOT NULL,
            required_size VARCHAR,
            subfield_type VARCHAR,
            required_cost INTEGER,
            sessions INTEGER NOT NULL,
            length INTEGER NOT NULL,
            partial_ses_space_size VARCHAR,
            partial_ses_space_cost INTEGER,
            partial_ses_time INTEGER,
            start_time TIME,
            club_id INTEGER,
            CONSTRAINT notation_exclusivity CHECK (
                ((required_size IS NOT NULL AND required_cost IS NULL) OR 
                (required_size IS NULL AND required_cost IS NOT NULL))
            ),
            CONSTRAINT partial_ses_space_exclusivity CHECK (
                ((partial_ses_space_size IS NOT NULL AND partial_ses_space_cost IS NULL) OR 
                (partial_ses_space_size IS NULL AND partial_ses_space_cost IS NOT NULL) OR 
                (partial_ses_space_size IS NULL AND partial_ses_space_cost IS NULL))
            )
        );

        CREATE TABLE public.facilities (
            facility_id SERIAL PRIMARY KEY,
            club_id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE NOT NULL,
            CONSTRAINT unique_club_facility_name UNIQUE (club_id, name)
        );

        CREATE TABLE public.field_availability (
            field_id INTEGER NOT NULL,
            day_of_week VARCHAR(10) NOT NULL,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            PRIMARY KEY (field_id, day_of_week, start_time),
            CONSTRAINT field_availability_day_of_week_check CHECK (
                day_of_week IN ('Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun')
            )
        );

        CREATE TABLE public.fields (
            field_id SERIAL PRIMARY KEY,
            facility_id INTEGER NOT NULL,
            name VARCHAR(255) NOT NULL,
            size VARCHAR(10),
            field_type VARCHAR(10),
            parent_field_id INTEGER,
            is_active BOOLEAN DEFAULT TRUE NOT NULL,
            CONSTRAINT fields_field_type_check CHECK (
                field_type IN ('full', 'half', 'quarter')
            ),
            CONSTRAINT fields_size_check CHECK (
                size IN ('11v11', '8v8', '5v5', '3v3')
            ),
            CONSTRAINT fields_facility_id_name_key UNIQUE (facility_id, name)
        );

        CREATE TABLE public.schedule_entries (
            schedule_entry_id SERIAL PRIMARY KEY,
            schedule_id INTEGER NOT NULL,
            team_id INTEGER,
            field_id INTEGER,
            parent_schedule_entry_id INTEGER,
            start_time TIME NOT NULL,
            end_time TIME NOT NULL,
            week_day SMALLINT NOT NULL,
            CONSTRAINT week_day_check CHECK (week_day BETWEEN 0 AND 6)
        );

        CREATE TABLE public.schedules (
            schedule_id SERIAL PRIMARY KEY,
            club_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            created_at TIMESTAMP DEFAULT now() NOT NULL,
            facility_id INTEGER
        );

        CREATE TABLE public.teams (
            team_id SERIAL PRIMARY KEY,
            club_id INTEGER NOT NULL,
            name VARCHAR NOT NULL,
            year VARCHAR NOT NULL,
            is_active BOOLEAN DEFAULT TRUE NOT NULL,
            gender VARCHAR(5) NOT NULL,
            is_academy BOOLEAN NOT NULL,
            minimum_field_size INTEGER NOT NULL,
            preferred_field_size INTEGER,
            level INTEGER NOT NULL,
            weekly_trainings INTEGER,
            CONSTRAINT teams_gender_check CHECK (
                gender IN ('boys', 'girls')
            ),
            CONSTRAINT teams_level_check CHECK (level BETWEEN 1 AND 5),
            CONSTRAINT teams_minimum_field_size_check CHECK (
                minimum_field_size IN (125, 250, 500, 1000)
            ),
            CONSTRAINT teams_preferred_field_size_check CHECK (
                preferred_field_size IN (125, 250, 500, 1000)
            ),
            CONSTRAINT teams_weekly_trainings_check CHECK (weekly_trainings BETWEEN 1 AND 5),
            CONSTRAINT teams_year_check CHECK (year ~ '^U([4-9]|1[0-9]|2[0-4])$')
        );

        CREATE TABLE public.user_club (
            user_id INTEGER NOT NULL,
            club_id INTEGER NOT NULL,
            is_primary BOOLEAN DEFAULT FALSE,
            added_at TIMESTAMP DEFAULT now(),
            PRIMARY KEY (user_id, club_id)
        );

        CREATE TABLE public.users (
            user_id SERIAL PRIMARY KEY,
            username VARCHAR(255) NOT NULL UNIQUE,
            email VARCHAR(255) NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            role VARCHAR(50) DEFAULT 'member' NOT NULL,
            created_at TIMESTAMP DEFAULT now(),
            updated_at TIMESTAMP DEFAULT now(),
            is_active BOOLEAN DEFAULT TRUE
        );
    """)


def downgrade() -> None:
    op.execute("""
        DROP TABLE public.users;
        DROP TABLE public.user_club;
        DROP TABLE public.teams;
        DROP TABLE public.schedules;
        DROP TABLE public.schedule_entries;
        DROP TABLE public.fields;
        DROP TABLE public.field_availability;
        DROP TABLE public.facilities;
        DROP TABLE public.constraints;
        DROP TABLE public.clubs;
    """)
