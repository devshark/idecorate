BEGIN;
CREATE TABLE `styleboard_items` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created` date NOT NULL
)
;
CREATE TABLE `customer_styleboards` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `user_id` integer NOT NULL,
    `styleboard_item_id` integer NOT NULL,
    `created` date NOT NULL
)
;
ALTER TABLE `customer_styleboards` ADD CONSTRAINT `styleboard_item_id_refs_id_f0602e12` FOREIGN KEY (`styleboard_item_id`) REFERENCES `styleboard_items` (`id`);
ALTER TABLE `customer_styleboards` ADD CONSTRAINT `user_id_refs_id_bcbba37d` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);
CREATE INDEX `customer_styleboards_fbfc09f1` ON `customer_styleboards` (`user_id`);
CREATE INDEX `customer_styleboards_86de2996` ON `customer_styleboards` (`styleboard_item_id`);
COMMIT;