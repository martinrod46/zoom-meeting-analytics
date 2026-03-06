=============================================================================
-- 01_create_schema.sql
-- Zoom Meeting Analytics Platform — Schema Definition
-- =============================================================================
-- Description : Creates all tables, constraints, and indexes for the
--               Zoom Meeting Analytics data warehouse.
--
-- Compatibility: SQLite 3.x (primary) and PostgreSQL 14+ (notes inline)
--
-- Run order   : 1st — must run before 02_load_data.sql
--
-- Tables created:
--   zoom_departments   → dimension table (12 rows)
--   zoom_hosts         → dimension table (150 rows)
--   zoom_meetings      → fact table     (2,000 rows)
--   zoom_participants  → fact table     (53,126 rows)
-- =============================================================================



------- Safety: Drop tables in reverse FK dependency order -------
---- (Useful when re-running this script during development)

DROP TABLE IF EXISTS zoom_participants;
DROP TABLE IF EXISTS zoom_meetings;
DROP TABLE IF EXISTS zoom_hosts;
DROP TABLE IF EXISTS zoom_departments;


-- =============================================================================
-- TABLE 1: zoom_departments

-- (Dimension Table)
-- -> One row per company department
-- =============================================================================

CREATE TABLE zoom_departments (
    department_id VARCHAR(10) NOT NULL,
    department_name VARCHAR(60) NOT NULL,
    division VARCHAR(60) NOT NULL,
    cost_center VARCHAR(10) NOT NULL,
    headcount INTEGER NOT NULL CHECK (headcount > 0),

    CONSTRAINT pk_departments PRIMARY KEY (department_id)
);

-- Index: Lookups by division (Used in GROUP BY aggregations)
CREATE INDEX idx_dept_division ON zoom_departments (division);

-- =============================================================================
-- TABLE 2: zoom_hosts

-- (Dimension Table)
-- -> One row per meeting host (Employee)
-- =============================================================================

CREATE TABLE zoom_hosts (
    host_id VARCHAR(10) NOT NULL,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) NOT NULL,
    department_id VARCHAR(10) NOT NULL,
    seniority_level VARCHAR(20) NOT NULL
     CHECK (seniority_level IN ('Junior', 'Mid', 'Senior', 'Director')),
    region VARCHAR(10) NOT NULL
     CHECK (region IN ('AMER', 'EMEA', 'APAC')),
    hire_date DATE NOT NULL,

    CONSTRAINT pk_hosts PRIMARY KEY (host_id),
    CONSTRAINT uq_hosts_email UNIQUE(email),
    CONSTRAINT fk_hosts_dept FOREIGN KEY (department_id) REFERENCES zoom_departments (department_id)
);

-- Indexes: Common filter/join columns
CREATE INDEX idx_hosts_dept ON zoom_hosts (department_id);
CREATE INDEX idx_hosts_region ON zoom_hosts (region);
CREATE INDEX idx_hosts_seniority ON zoom_hosts (seniority_level);


-- =============================================================================
-- TABLE 3: zoom_meetings

-- (Fact Table)
-- -> Core fact table - One row per Zoom meeting
-- =============================================================================

CREATE TABLE zoom_meetings (
    meeting_id VARCHAR(20) NOT NULL,
    host_id VARCHAR(10) NOT NULL,
    department_id VARCHAR(10) NOT NULL,
    meeting_date DATE NOT NULL,
    start_time TIMESTAMP NOT NULL,
    scheduled_duration_min INTEGER NOT NULL
     CHECK (scheduled_duration_min > 0),
    actual_duration_min INTEGER NOT NULL,
     CHECK (actual_duration_min > 0),
    meeting_type VARCHAR(20) NOT NULL
     CHECK (meeting_type IN ('Internal', 'External', 'Webinar', 'Training')),
    total_invited INTEGER NOT NULL
     CHECK (total_invited >= 1),
    total_joined INTEGER NOT NULL
     CHECK (total_joined >= 0),
    recording_enabled BOOLEAN DEFAULT 0,
    chat_messages_count INTEGER NOT NULL,
     CHECK (chat_messages_count >= 0),
    reactions_count INTEGER NOT NULL
     CHECK (reactions_count >= 0),
    screen_shares_count INTEGER NOT NULL
     CHECK (screen_shares_count >= 0),
    
    CONSTRAINT pk_meetings PRIMARY KEY (meeting_id),
    CONSTRAINT fk_meetings_host FOREIGN KEY (host_id) REFERENCES zoom_hosts (host_id),
    CONSTRAINT fk_meetings_dept FOREIGN KEY (department_id) REFERENCES zoom_departments (department_id),
    -- Business rule: Can't have more joined than invited
    CONSTRAINT chk_attendance CHECK (total_joined <= total_invited)
    
);

CREATE INDEX idx_meetings_date ON zoom_meetings (meeting_date);
CREATE INDEX idx_meetings_host ON zoom_meetings (host_id);
CREATE INDEX idx_meetings_dept ON zoom_meetings (department_id);
CREATE INDEX idx_meetings_type ON zoom_meetings (meeting_type);
-- Composite index for date + type filtering (common dashboard pattern)
CREATE INDEX idx_meetings_date_type ON zoom_meetings (meeting_date, meeting_type);


-- =============================================================================
-- TABLE 4: zoom_participants

-- (Fact Table)
-- -> One row per participant per meeting
-- -> This creates the many-to-many relationships between meetings and users
-- =============================================================================

CREATE TABLE zoom_participants (
    participant_id VARCHAR(15) NOT NULL, 
    meeting_id VARCHAR(20) NOT NULL,
    user_email VARCHAR(150) NOT NULL,
    join_time TIMESTAMP NOT NULL,
    leave_time TIMESTAMP NOT NULL,
    time_in_meeting_min INTEGER NOT NULL 
     CHECK (time_in_meeting_min >= 0),
    camera_on_pct REAL NOT NULL DEFAULT 0
     CHECK (camera_on_pct BETWEEN 0.0 AND 1.0),
    mic_on_pct REAL NOT NULL DEFAULT 0
     CHECK (mic_on_pct BETWEEN 0.0 AND 1.0),
    attentiveness_score REAL NOT NULL DEFAULT 0
     CHECK (attentiveness_score BETWEEN 0.0 AND 100.0),
    raised_hand BOOLEAN NOT NULL DEFAULT 0,
    device_type VARCHAR(20) NOT NULL
     CHECK (device_type IN ('Desktop', 'Mobile', 'Web', 'Room System')),

    CONSTRAINT pk_participants PRIMARY KEY (participant_id),
    CONSTRAINT fk_participants_meeting FOREIGN KEY (meeting_id),
    -- Business rule: Leave time must be after join time
    CONSTRAINT chk_time_order 
     CHECK (leave_time > join_time)
);

-- Indexes: meeting_id is the most common join/filter column here
CREATE INDEX idx_part_meeting ON zoom_participants (meeting_id);
CREATE INDEX idx_part_email ON zoom_participants (user_email);
CREATE INDEX idx_part_device ON zoom_participants (device_type);

-- Composite: meeting + attentiveness for engagement scoring queries 
CREATE INDEX idx_part_meeting_att ON zoom_participants (meeting_id, attentiveness_score);

-- =============================================================================
-- Verification query — run after loading data to confirm row counts
-- =============================================================================
-- SELECT 'zoom_departments'  AS table_name, COUNT(*) AS row_count FROM zoom_departments
-- UNION ALL
-- SELECT 'zoom_hosts',                       COUNT(*)             FROM zoom_hosts
-- UNION ALL
-- SELECT 'zoom_meetings',                    COUNT(*)             FROM zoom_meetings
-- UNION ALL
-- SELECT 'zoom_participants',                COUNT(*)             FROM zoom_participants;