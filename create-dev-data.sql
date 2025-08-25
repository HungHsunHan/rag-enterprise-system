-- Development data setup script
-- Run this directly against PostgreSQL

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS vector;

-- Create tables (based on models.py)
CREATE TABLE IF NOT EXISTS companies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS admins (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    employee_id VARCHAR(100) NOT NULL,
    company_id UUID NOT NULL REFERENCES companies(id),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_company_employee UNIQUE(company_id, employee_id)
);

CREATE TABLE IF NOT EXISTS knowledge_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    file_name VARCHAR(255) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'PROCESSING',
    company_id UUID NOT NULL REFERENCES companies(id),
    uploaded_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS document_chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES knowledge_documents(id),
    company_id UUID NOT NULL REFERENCES companies(id),
    chunk_text TEXT NOT NULL,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    embedding vector(384),
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS feedback_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES users(id),
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    feedback VARCHAR(20) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT NOW()
);

-- Insert development data
INSERT INTO companies (id, name) VALUES 
    ('550e8400-e29b-41d4-a716-446655440001', 'Acme Corp'),
    ('550e8400-e29b-41d4-a716-446655440002', 'Tech Innovations Inc')
ON CONFLICT (id) DO NOTHING;

-- Insert development admin (password: admin123)
-- Hash generated with: python3 -c "from passlib.context import CryptContext; pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto'); print(pwd_context.hash('admin123'))"
INSERT INTO admins (id, email, password_hash) VALUES 
    (uuid_generate_v4(), 'admin@dev.com', '$2b$12$zZL/yfr1h7bHi0aVjK/3j.TkCeraBgJViVTwSPxogMRxbxed/8pvi')
ON CONFLICT (email) DO NOTHING;

-- Insert development users with names
INSERT INTO users (id, employee_id, company_id, name) VALUES 
    (uuid_generate_v4(), 'BRIAN001', '550e8400-e29b-41d4-a716-446655440001', 'Brian Zhang'),
    (uuid_generate_v4(), 'TONY001', '550e8400-e29b-41d4-a716-446655440001', 'Tony Chen'),
    (uuid_generate_v4(), 'LISA001', '550e8400-e29b-41d4-a716-446655440002', 'Lisa Wang'),
    (uuid_generate_v4(), 'DEV001', '550e8400-e29b-41d4-a716-446655440002', 'Developer User')
ON CONFLICT (company_id, employee_id) DO NOTHING;

-- Display created data
SELECT 'Companies:' as info;
SELECT name, id FROM companies;

SELECT 'Admins:' as info;  
SELECT email FROM admins;

SELECT 'Users:' as info;
SELECT u.employee_id, u.name, c.name as company FROM users u JOIN companies c ON u.company_id = c.id ORDER BY c.name, u.employee_id;