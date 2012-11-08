CREATE TABLE `guest_tables` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `guests` integer UNSIGNED NOT NULL,
    `tables` integer UNSIGNED NOT NULL,
    `order_id` integer NOT NULL
)
;
ALTER TABLE `guest_tables` ADD CONSTRAINT `order_id_refs_id_33439f92` FOREIGN KEY (`order_id`) REFERENCES `shop_order` (`id`);
COMMIT;