BEGIN;
CREATE TABLE `product_details` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `product_id` integer NOT NULL,
    `comment` longtext,
    `size` varchar(255),
    `unit_price` numeric(6, 2),
    `pieces_per_carton` integer UNSIGNED,
    `min_order_qty_carton` integer UNSIGNED,
    `min_order_qty_pieces` integer UNSIGNED,
    `cost_min_order_qty` numeric(6, 2)
)
;
ALTER TABLE `product_details` ADD CONSTRAINT `product_id_refs_id_f9ecd29c` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);
CREATE INDEX `product_details_bb420c12` ON `product_details` (`product_id`);
COMMIT;