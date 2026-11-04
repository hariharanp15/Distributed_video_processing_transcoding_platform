-- Apply with: mysql video_platform < 001_initial_schema.sql
-- SQLAlchemy creates the equivalent schema at gateway startup for local development.
CREATE TABLE IF NOT EXISTS videos (id VARCHAR(36) PRIMARY KEY, filename VARCHAR(255) NOT NULL, storage_path VARCHAR(500) NOT NULL, status VARCHAR(30) NOT NULL, created_at DATETIME NOT NULL);
CREATE TABLE IF NOT EXISTS video_metadata (video_id VARCHAR(36) PRIMARY KEY, title VARCHAR(255) NOT NULL, format VARCHAR(20) NOT NULL, duration INT NOT NULL DEFAULT 0, width INT NOT NULL DEFAULT 0, height INT NOT NULL DEFAULT 0, file_size INT NOT NULL, FOREIGN KEY(video_id) REFERENCES videos(id));
CREATE TABLE IF NOT EXISTS processing_jobs (id VARCHAR(36) PRIMARY KEY, video_id VARCHAR(36) NOT NULL, status VARCHAR(30) NOT NULL, progress INT NOT NULL, retries INT NOT NULL, error_message TEXT, created_at DATETIME NOT NULL, updated_at DATETIME NOT NULL, FOREIGN KEY(video_id) REFERENCES videos(id));
CREATE TABLE IF NOT EXISTS processing_attempts (id VARCHAR(36) PRIMARY KEY, job_id VARCHAR(36) NOT NULL, attempt_number INT NOT NULL, status VARCHAR(20) NOT NULL, error_message TEXT, created_at DATETIME NOT NULL, UNIQUE(job_id, attempt_number));
CREATE TABLE IF NOT EXISTS transcoding_outputs (id VARCHAR(36) PRIMARY KEY, video_id VARCHAR(36) NOT NULL, resolution VARCHAR(10) NOT NULL, url VARCHAR(500) NOT NULL, status VARCHAR(20) NOT NULL, UNIQUE(video_id, resolution));
CREATE TABLE IF NOT EXISTS video_thumbnails (id VARCHAR(36) PRIMARY KEY, video_id VARCHAR(36) NOT NULL UNIQUE, url VARCHAR(500) NOT NULL, status VARCHAR(20) NOT NULL);
