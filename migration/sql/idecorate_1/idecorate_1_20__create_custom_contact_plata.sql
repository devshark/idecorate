CREATE TABLE `cart_contact` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL UNIQUE,
    `first_name` varchar(100) NOT NULL,
    `last_name` varchar(100) NOT NULL,
    `address` longtext NOT NULL,
    `shipping_address2` longtext NOT NULL,
    `billing_address2` longtext NOT NULL,
    `shipping_state` varchar(100) NOT NULL,
    `billing_state` varchar(100) NOT NULL,
    `shipping_salutation` varchar(100) NOT NULL,
    `billing_salutation` varchar(100) NOT NULL,
    `zip_code` varchar(50) NOT NULL,
    `city` varchar(100) NOT NULL,
    `shipping_same_as_billing` bool NOT NULL,
    `currency` varchar(3) NOT NULL
)
;
ALTER TABLE `cart_contact` ADD CONSTRAINT `user_id_refs_id_1a381a8b` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
COMMIT;

