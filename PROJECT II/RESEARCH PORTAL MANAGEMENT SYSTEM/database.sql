CREATE TABLE IF NOT EXISTS `users` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `username` VARCHAR(80) NOT NULL UNIQUE,
    `email` VARCHAR(120) NOT NULL UNIQUE,
    `password_hash` VARCHAR(256) NOT NULL,
    `orcid_id` VARCHAR(50) UNIQUE,
    `user_type` VARCHAR(20) NOT NULL,
    `created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    `updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `papers` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `title` VARCHAR(200) NOT NULL,
    `author_name` VARCHAR(200) NOT NULL,
    `category` VARCHAR(50) NOT NULL,
    `publication_name` VARCHAR(200) NOT NULL,
    `publication_date` DATE NOT NULL,
    `file_path` VARCHAR(300) NOT NULL,
    `uploaded_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_paper_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS `orcid_data` (
    `id` INT AUTO_INCREMENT PRIMARY KEY,
    `user_id` INT NOT NULL,
    `put_code` VARCHAR(50),
    `title` VARCHAR(500),
    `work_type` VARCHAR(100),
    `publication_year` VARCHAR(10),
    `journal_title` VARCHAR(300),
    `doi` VARCHAR(100),
    `fetched_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT `fk_orcid_user`
        FOREIGN KEY (`user_id`)
        REFERENCES `users` (`id`)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    INDEX `idx_orcid_user_id` (`user_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;