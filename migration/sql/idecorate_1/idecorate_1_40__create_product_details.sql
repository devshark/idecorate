BEGIN;
CREATE TABLE `product_details` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `product_id` integer NOT NULL,
    `comment` longtext,
    `size` varchar(255),
    `color` varchar(100),
    `unit_price` numeric(19, 2),
    `pieces_per_carton` integer UNSIGNED,
    `min_order_qty_carton` integer UNSIGNED,
    `min_order_qty_pieces` integer UNSIGNED,
    `cost_min_order_qty` numeric(19, 2),
    `qty_sold` integer UNSIGNED
)
;
ALTER TABLE `product_details` ADD CONSTRAINT `product_id_refs_id_f9ecd29c` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);
COMMIT;