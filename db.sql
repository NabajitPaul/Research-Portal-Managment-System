CREATE TABLE IF NOT EXISTS `users` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(80) NOT NULL,
  `email` VARCHAR(120) NOT NULL,
  `password_hash` VARCHAR(256) NOT NULL,
  `orcid_id` VARCHAR(50) DEFAULT NULL,
  `user_type` VARCHAR(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `uq_username` (`username`),
  UNIQUE KEY `uq_email` (`email`),
  UNIQUE KEY `uq_orcid_id` (`orcid_id`) -- ORCID ID should be unique across users
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Table structure for table `papers`
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `papers` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `title` VARCHAR(200) NOT NULL,
  `author_name` VARCHAR(200) NOT NULL,
  `category` VARCHAR(50) NOT NULL,
  `publication_name` VARCHAR(200) NOT NULL,
  `publication_date` DATE NOT NULL,
  `file_path` VARCHAR(300) NOT NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_papers_user_id` (`user_id`),
  CONSTRAINT `fk_papers_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Table structure for table `orcid_data`
-- (Corresponds to OrcidWork model)
-- --------------------------------------------------------
CREATE TABLE IF NOT EXISTS `orcid_data` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `user_id` INT NOT NULL,
  `put_code` VARCHAR(50) DEFAULT NULL,      -- ORCID internal identifier for the work
  `title` VARCHAR(500) DEFAULT NULL,       -- Increased length for potentially long titles
  `work_type` VARCHAR(100) DEFAULT NULL,
  `publication_year` VARCHAR(10) DEFAULT NULL, -- Storing as VARCHAR as ORCID can have YYYY or YYYY-MM etc.
  `journal_title` VARCHAR(300) DEFAULT NULL,
  `doi` VARCHAR(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_orcid_data_user_id` (`user_id`),
  CONSTRAINT `fk_orcid_data_user_id` FOREIGN KEY (`user_id`) REFERENCES `users` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
  -- Optional: You might want a unique constraint on (user_id, put_code) if put_code is reliably unique per user work
  -- UNIQUE KEY `uq_user_put_code` (`user_id`, `put_code`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- --------------------------------------------------------
-- Optional: Add Admin User (if not creating through the app first)
-- This is for the username: admin, password: admin123
-- The password_hash here is for 'admin123' using werkzeug.security.generate_password_hash
-- You would typically not add users manually like this if you have a registration system,
-- but the admin user is special.
-- --------------------------------------------------------
-- INSERT INTO `users` (`username`, `email`, `password_hash`, `orcid_id`, `user_type`)
-- VALUES
-- ('admin', 'admin@example.com', 'pbkdf2:sha256:260000$AgYAgZ50jpsh9nSL$82790e58972a8e0141e064a21a52c382a8d4373ce1a81e75b044c914e83f04cb', NULL, 'Admin')
-- ON DUPLICATE KEY UPDATE username = 'admin'; -- Avoids error if admin already exists
-- Note: The hash 'pbkdf2:sha256:260000$AgYAgZ50jpsh9nSL$82790e58972a8e0141e064a21a52c382a8d4373ce1a81e75b044c914e83f04cb' is an example.
-- If you run the Flask app and `db.create_all()` it will be empty, and you log in with 'admin'/'admin123'
-- the system will handle it without needing this insert (as admin is not stored in DB by default in the provided app.py).
-- The app.py handles admin login via a hardcoded check:
-- if username == 'admin' and password == 'admin123':
-- So, this SQL insert for admin is NOT strictly necessary for the provided Python code.
-- I've kept it commented out.
