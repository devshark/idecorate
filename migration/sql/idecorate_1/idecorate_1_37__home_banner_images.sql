BEGIN;
CREATE TABLE `home_banner_images` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `home_banner_id` integer NOT NULL,
    `image` varchar(256) NOT NULL
)
;
CREATE INDEX `home_banner_images_d6eacc97` ON `home_banner_images` (`home_banner_id`);
COMMIT;