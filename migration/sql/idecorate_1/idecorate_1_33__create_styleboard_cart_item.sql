BEGIN;
CREATE TABLE `styleboard_cart_items` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `styleboard_item_id` integer NOT NULL,
    `product_id` integer NOT NULL,
    `quantity` integer UNSIGNED NOT NULL
);
ALTER TABLE `styleboard_cart_items` ADD CONSTRAINT `styleboard_item_id_refs_id_616fdc83` FOREIGN KEY (`styleboard_item_id`) REFERENCES `styleboard_items` (`id`);
ALTER TABLE `styleboard_cart_items` ADD CONSTRAINT `product_id_refs_id_3c99d46d` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);
CREATE INDEX `styleboard_cart_items_86de2996` ON `styleboard_cart_items` (`styleboard_item_id`);
CREATE INDEX `styleboard_cart_items_bb420c12` ON `styleboard_cart_items` (`product_id`);
COMMIT;