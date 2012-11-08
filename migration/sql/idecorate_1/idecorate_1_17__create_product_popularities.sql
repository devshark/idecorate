BEGIN;
CREATE TABLE `product_popularities` (
    `product_id` integer NOT NULL PRIMARY KEY,
    `dropped` integer UNSIGNED NOT NULL
)
;
ALTER TABLE `product_popularities` ADD CONSTRAINT `product_id_refs_id_74531054` FOREIGN KEY (`product_id`) REFERENCES `product` (`id`);
COMMIT;
