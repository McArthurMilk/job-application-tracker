-- Job Application Tracker - database creation script
-- Run with:  mysql -u root -p < schema.sql

DROP DATABASE IF EXISTS job_tracker;
CREATE DATABASE job_tracker;
USE job_tracker;

-- 1. Companies I'm interested in
CREATE TABLE companies (
    company_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_name VARCHAR(100) NOT NULL,
    industry     VARCHAR(50),
    website      VARCHAR(200),
    city         VARCHAR(50),
    state        VARCHAR(50),
    notes        TEXT
);

-- 2. Job postings (each belongs to a company)
CREATE TABLE jobs (
    job_id       INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT,
    job_title    VARCHAR(100) NOT NULL,
    job_type     ENUM('Full-time','Part-time','Contract','Internship'),
    salary_min   INT,
    salary_max   INT,
    job_url      VARCHAR(300),
    date_posted  DATE,
    requirements JSON,          -- list of skills, e.g. ["Python", "SQL"]
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- 3. Applications I've submitted (each is for one job)
CREATE TABLE applications (
    application_id    INT PRIMARY KEY AUTO_INCREMENT,
    job_id            INT,
    application_date  DATE NOT NULL,
    status            ENUM('Applied','Screening','Interview','Offer','Rejected','Withdrawn') DEFAULT 'Applied',
    resume_version    VARCHAR(50),
    cover_letter_sent BOOLEAN DEFAULT FALSE,
    interview_data    JSON,     -- e.g. {"interview_date": "...", "interviewer": "...", "notes": "..."}
    FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
);

-- 4. People I know at each company
CREATE TABLE contacts (
    contact_id   INT PRIMARY KEY AUTO_INCREMENT,
    company_id   INT,
    contact_name VARCHAR(100) NOT NULL,
    title        VARCHAR(100),
    email        VARCHAR(100),
    phone        VARCHAR(20),
    linkedin_url VARCHAR(200),
    notes        TEXT,
    FOREIGN KEY (company_id) REFERENCES companies(company_id) ON DELETE CASCADE
);

-- ---------- Sample data ----------
INSERT INTO companies (company_name, industry, website, city, state, notes) VALUES
('TechCorp',      'Software',   'https://techcorp.example.com',  'Austin',   'TX', 'Fast-growing startup'),
('DataCo',        'Analytics',  'https://dataco.example.com',    'Chicago',  'IL', 'Heard great things about the culture'),
('CloudNine',     'Cloud',      'https://cloudnine.example.com', 'Seattle',  'WA', NULL),
('HealthBridge',  'Healthcare', 'https://healthbridge.example.com', 'Boston', 'MA', 'Remote friendly');

INSERT INTO jobs (company_id, job_title, job_type, salary_min, salary_max, job_url, date_posted, requirements) VALUES
(1, 'Software Developer',     'Full-time',  70000, 90000, 'https://techcorp.example.com/jobs/1',  '2026-10-01', '["Python", "SQL", "Flask"]'),
(2, 'Data Analyst',           'Full-time',  60000, 75000, 'https://dataco.example.com/jobs/7',    '2026-10-05', '["Python", "SQL", "Tableau"]'),
(3, 'Cloud Engineer Intern',  'Internship', 20000, 25000, 'https://cloudnine.example.com/jobs/3', '2026-10-12', '["AWS", "Linux", "Python"]'),
(4, 'Web Developer',          'Contract',   50000, 65000, 'https://healthbridge.example.com/jobs/2', '2026-10-20', '["HTML", "CSS", "JavaScript", "Flask"]'),
(1, 'Database Administrator', 'Part-time',  40000, 50000, NULL, '2026-11-02', '["SQL", "MySQL", "Linux"]');

INSERT INTO applications (job_id, application_date, status, resume_version, cover_letter_sent, interview_data) VALUES
(1, '2026-10-03', 'Interview', 'v2-software', TRUE,  '{"interview_date": "2026-10-15", "interviewer": "Sarah Lee", "notes": "Technical round went well"}'),
(2, '2026-10-07', 'Applied',   'v1-data',     FALSE, NULL),
(3, '2026-10-14', 'Screening', 'v2-software', TRUE,  NULL),
(4, '2026-10-22', 'Rejected',  'v1-web',      FALSE, NULL);

INSERT INTO contacts (company_id, contact_name, title, email, phone, linkedin_url, notes) VALUES
(1, 'Sarah Lee',   'Engineering Manager', 'sarah.lee@techcorp.example.com', '512-555-0101', 'https://linkedin.com/in/sarahlee', 'Met at career fair'),
(2, 'Marcus Diaz', 'Recruiter',           'marcus@dataco.example.com',      '312-555-0144', NULL, NULL),
(3, 'Priya Shah',  'Senior Engineer',     'priya@cloudnine.example.com',    NULL,           'https://linkedin.com/in/priyashah', 'Alumni from my school');
