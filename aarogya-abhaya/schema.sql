-- ============================================
-- Aarogya Abhaya - Database Schema
-- ============================================
-- Run this file to set up the database:
--   1. Create the database:  createdb aarogya_abhaya
--   2. Run this file:        psql -d aarogya_abhaya -f schema.sql
-- ============================================

-- Users table (all roles: asha_worker, jpha, lha, pregnant_woman, teenager, newborn)
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    full_name VARCHAR(200) DEFAULT '',
    email VARCHAR(200) DEFAULT '',
    phone VARCHAR(20) DEFAULT '',
    dob DATE,
    gender VARCHAR(20) DEFAULT '',
    blood_group VARCHAR(10) DEFAULT '',
    health_status VARCHAR(100) DEFAULT '',
    village VARCHAR(200) DEFAULT '',
    guardian VARCHAR(200) DEFAULT '',
    address TEXT DEFAULT '',
    area VARCHAR(200) DEFAULT '',
    profile_photo VARCHAR(500),
    created_by INTEGER REFERENCES users(id),
    jpha_id INTEGER REFERENCES users(id),
    lha_id INTEGER REFERENCES users(id),
    approval_status VARCHAR(20) DEFAULT 'pending',
    lha_status VARCHAR(20) DEFAULT 'pending',
    otp VARCHAR(10),
    otp_expiry TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Vaccination schedule for newborns
CREATE TABLE IF NOT EXISTS vaccinations (
    id SERIAL PRIMARY KEY,
    newborn_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    vaccine_name VARCHAR(100) NOT NULL,
    due_date DATE NOT NULL,
    given_date DATE,
    status VARCHAR(20) DEFAULT 'pending',
    recorded_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Notices from ASHA workers to beneficiaries
CREATE TABLE IF NOT EXISTS notices (
    id SERIAL PRIMARY KEY,
    message TEXT NOT NULL,
    created_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    target_roles TEXT[] DEFAULT '{}',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Videos uploaded by ASHA workers
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT DEFAULT '',
    category VARCHAR(100) NOT NULL,
    video_path VARCHAR(500) NOT NULL,
    uploaded_by INTEGER REFERENCES users(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================
-- Indexes for performance
-- ============================================
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);
CREATE INDEX IF NOT EXISTS idx_users_created_by ON users(created_by);
CREATE INDEX IF NOT EXISTS idx_users_jpha_id ON users(jpha_id);
CREATE INDEX IF NOT EXISTS idx_users_lha_id ON users(lha_id);
CREATE INDEX IF NOT EXISTS idx_vaccinations_newborn ON vaccinations(newborn_id);
CREATE INDEX IF NOT EXISTS idx_notices_created_by ON notices(created_by);
CREATE INDEX IF NOT EXISTS idx_videos_uploaded_by ON videos(uploaded_by);
