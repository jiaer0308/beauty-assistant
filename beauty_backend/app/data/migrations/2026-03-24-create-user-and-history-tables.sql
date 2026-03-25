-- Migration script for User Accounts & Recommendation History
-- Date: 2026-03-24
-- Target Database: MySQL
-- Task 1: Create 'users', 'recommendation_sessions', and 'recommendation_items' tables

USE beauty_assisant;

-- 1. Create 'users' table
CREATE TABLE `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `email` VARCHAR(255) UNIQUE NULL,
    `password_hash` VARCHAR(255) NULL,
    `guest_token` VARCHAR(255) UNIQUE NULL,
    `current_season_id` INT NULL,
    `is_guest` BOOLEAN DEFAULT TRUE,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (`current_season_id`) REFERENCES `seasons` (`id`) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 2. Create 'recommendation_sessions' table
CREATE TABLE `recommendation_sessions` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `analysis_type` ENUM('sca_scan', 'manual') NOT NULL,
    `season_id` INT NOT NULL,
    `image_path` VARCHAR(255) NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`season_id`) REFERENCES `seasons` (`id`) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 3. Create 'recommendation_items' table
CREATE TABLE `recommendation_items` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `session_id` INT NOT NULL,
    `cosmetic_id` INT NOT NULL,
    `is_saved` BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (`session_id`) REFERENCES `recommendation_sessions` (`id`) ON DELETE CASCADE,
    FOREIGN KEY (`cosmetic_id`) REFERENCES `cosmetic_products` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Add indexes for better performance on common queries
CREATE INDEX `idx_user_email` ON `users` (`email`);
CREATE INDEX `idx_user_guest_token` ON `users` (`guest_token`);
CREATE INDEX `idx_session_user_id` ON `recommendation_sessions` (`user_id`);
CREATE INDEX `idx_item_session_id` ON `recommendation_items` (`session_id`);
CREATE INDEX `idx_item_cosmetic_id` ON `recommendation_items` (`cosmetic_id`);
