-- 1) Drop tables in reverse dependency order
DROP TABLE IF EXISTS `notifications`;
DROP TABLE IF EXISTS `plant_status`;
DROP TABLE IF EXISTS `light_intensity`;
DROP TABLE IF EXISTS `soil_moisture`;
DROP TABLE IF EXISTS `air_pressure`;
DROP TABLE IF EXISTS `air_temperature`;
DROP TABLE IF EXISTS `air_humidity`;
DROP TABLE IF EXISTS `edge_devices`;
DROP TABLE IF EXISTS `fog_devices`;
DROP TABLE IF EXISTS `users`;

-- 2) Create users table
CREATE TABLE `users` (
  `user_id`        INT AUTO_INCREMENT PRIMARY KEY,
  `username`       VARCHAR(50)      NOT NULL,
  `password`       VARCHAR(255)     NOT NULL,
  `email`          VARCHAR(100)     DEFAULT NULL,
  `created_at`     DATETIME         DEFAULT CURRENT_TIMESTAMP,
  `updated_at`     DATETIME         DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 3) Create fog_devices table
CREATE TABLE `fog_devices` (
  `fog_device_id`   INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_name` VARCHAR(50)    NOT NULL,
  `status`          VARCHAR(20)    DEFAULT 'offline',
  `user_id`         INT            NOT NULL,
  `created_at`      DATETIME       DEFAULT CURRENT_TIMESTAMP,
  `updated_at`      DATETIME       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_fog_user`
    FOREIGN KEY (`user_id`) REFERENCES `users`(`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 4) Create air_humidity table
CREATE TABLE `air_humidity` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id`   INT           NOT NULL,
  `humidity_value`  FLOAT         NOT NULL,
  `measured_at`     DATETIME      NOT NULL,
  `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_airhumidity_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 5) Create air_temperature table
CREATE TABLE `air_temperature` (
  `id`                INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id`     INT           NOT NULL,
  `temperature_value` FLOAT         NOT NULL,
  `measured_at`       DATETIME      NOT NULL,
  `created_at`        DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_airtemp_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 6) Create air_pressure table
CREATE TABLE `air_pressure` (
  `id`                INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id`     INT           NOT NULL,
  `pressure_value`    FLOAT         NOT NULL,
  `measured_at`       DATETIME      NOT NULL,
  `created_at`        DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_airpressure_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 7) Create soil_moisture table
CREATE TABLE `soil_moisture` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id`   INT           NOT NULL,
  `moisture_value`  FLOAT         NOT NULL,
  `measured_at`     DATETIME      NOT NULL,
  `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_soil_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 8) Create light_intensity table
CREATE TABLE `light_intensity` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id`   INT           NOT NULL,
  `light_value`     FLOAT         NOT NULL,
  `measured_at`     DATETIME      NOT NULL,
  `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_light_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9) Create plant_status table
CREATE TABLE `plant_status` (
  `plant_id`      INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id` INT           NOT NULL,
  `status`        VARCHAR(50)   DEFAULT 'healthy',
  `description`   TEXT          DEFAULT NULL,
  `measured_at`   DATETIME      NOT NULL,
  `created_at`    DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_plant_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10) Create notifications table
CREATE TABLE `notifications` (
  `notification_id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id`         INT           NOT NULL,
  `fog_device_id`   INT           DEFAULT NULL,
  `message`         TEXT          NOT NULL,
  `type`            VARCHAR(50)   DEFAULT 'INFO',
  `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_notif_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_notif_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

INSERT INTO `users` (`username`, `password`, `email`)
VALUES ('admin', '123456', 'xieyuening2002@gmail.com');

INSERT INTO `fog_devices` (`fog_device_name`, `status`, `user_id`)
VALUES ('raspberry-01', 'offline', 1);
