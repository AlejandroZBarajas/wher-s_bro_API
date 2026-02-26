-- init.sql
-- Script para inicializar MySQL con tabla de usuarios

-- Crear base de datos si no existe
CREATE DATABASE IF NOT EXISTS location_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE location_db;

-- Crear tabla de usuarios
CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insertar usuario de prueba
-- Password: "test123" (ya hasheado con bcrypt)
INSERT INTO user (username, email, hashed_password) 
VALUES ('testuser', 'test@example.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYSv.fNu1Gu')
ON DUPLICATE KEY UPDATE username=username;

-- Verificar que se creó correctamente
SELECT 'Database initialized successfully' AS status;
SELECT COUNT(*) AS total_users FROM user;
