BEGIN;
CREATE TABLE `customer_profiles` (
    `user_id` integer NOT NULL PRIMARY KEY,
    `nickname` varchar(256) NOT NULL
)
;
ALTER TABLE `customer_profiles` ADD CONSTRAINT `user_id_refs_id_a8c43864` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE INDEX `customer_profiles_e6a08719` ON `customer_profiles` (`nickname`);
COMMIT;