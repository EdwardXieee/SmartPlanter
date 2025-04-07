-- 1) Drop all tables in reverse dependency order
DROP TABLE IF EXISTS `notifications`;
DROP TABLE IF EXISTS `weather_forcast`;
DROP TABLE IF EXISTS `plant_watering_needed`;
DROP TABLE IF EXISTS `plant_light_needed`;
DROP TABLE IF EXISTS `plant_health`;
DROP TABLE IF EXISTS `light_intensity`;
DROP TABLE IF EXISTS `soil_moisture`;
DROP TABLE IF EXISTS `air_pressure`;
DROP TABLE IF EXISTS `air_temperature`;
DROP TABLE IF EXISTS `air_humidity`;
DROP TABLE IF EXISTS `plant_status`;
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
  `status`          VARCHAR(20)    DEFAULT 'offline', -- 'online', 'offline'
  `user_id`         INT            NOT NULL,
  `created_at`      DATETIME       DEFAULT CURRENT_TIMESTAMP,
  `updated_at`      DATETIME       DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  CONSTRAINT `fk_fogdevices_user`
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
  CONSTRAINT `fk_airtemperature_fog`
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
  CONSTRAINT `fk_soilmoisture_fog`
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
  CONSTRAINT `fk_lightintensity_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 9) Create plant_health table
CREATE TABLE `plant_health` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id`   INT           NOT NULL,
  `status`          VARCHAR(50)   DEFAULT 'healthy',
  `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_planthealth_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 10) Create plant_light_needed table
CREATE TABLE `plant_light_needed` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id`   INT           NOT NULL,
  `light_needed`    INT           NOT NULL,
  `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_plantlightneeded_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 11) Create plant_watering_needed table
CREATE TABLE `plant_watering_needed` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id`   INT           NOT NULL,
  `status`          INT           DEFAULT 0, -- 0: need watering, 1: no need
  `water_needed`    FLOAT         DEFAULT 0.0,
  `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_plantwateringneeded_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 12) Create weather_forecast table
CREATE TABLE `weather_forcast` (
  `id`              INT AUTO_INCREMENT PRIMARY KEY,
  `fog_device_id`   INT           NOT NULL,
  `status`          INT           DEFAULT 0, -- 0, 1, 2: bigger number, worse weather
  `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_weatherforecast_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 13) Create notifications table
CREATE TABLE `notifications` (
  `notification_id` INT AUTO_INCREMENT PRIMARY KEY,
  `user_id`         INT           NOT NULL,
  `fog_device_id`   INT           DEFAULT NULL,
  `message`         TEXT          NOT NULL,
  `type`            VARCHAR(50)   DEFAULT 'INFO',
  `created_at`      DATETIME      DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT `fk_notifications_user`
    FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
  CONSTRAINT `fk_notifications_fog`
    FOREIGN KEY (`fog_device_id`) REFERENCES `fog_devices` (`fog_device_id`)
    ON DELETE SET NULL
    ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 14) Insert sample user and fog_device
INSERT INTO `users` (`username`, `password`, `email`)
VALUES ('admin', '123456', 'xieyuening2002@gmail.com');

INSERT INTO `fog_devices` (`fog_device_name`, `status`, `user_id`)
VALUES ('raspberry-01', 'offline', 1);
