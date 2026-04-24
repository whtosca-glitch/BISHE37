CREATE TABLE IF NOT EXISTS `onenet_devices` (
  `record_id` VARCHAR(64) NOT NULL,
  `display_name` VARCHAR(255) NOT NULL,
  `onenet_device_name` VARCHAR(255) NOT NULL,
  `product_id` VARCHAR(128) NOT NULL,
  `user_id` VARCHAR(128) NOT NULL,
  `access_key` TEXT NOT NULL,
  `auth_version` VARCHAR(32) NOT NULL,
  `device_secret` TEXT NULL,
  `device_id` VARCHAR(128) NULL,
  `ip` VARCHAR(128) NULL,
  `start_success_count` INT NOT NULL DEFAULT 0,
  `notes` TEXT NULL,
  `created_at` VARCHAR(32) NOT NULL,
  `updated_at` VARCHAR(32) NOT NULL,
  PRIMARY KEY (`record_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
