BEGIN;
CREATE TABLE `cart_temps` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `product_id` integer NOT NULL,
    `quantity` integer UNSIGNED NOT NULL,
    `user_id` integer,
    `session_key` varchar(200)
);

CREATE INDEX `cart_temps_bb420c12` ON `cart_temps` (`product_id`);
CREATE INDEX `cart_temps_fbfc09f1` ON `cart_temps` (`user_id`);
COMMIT;