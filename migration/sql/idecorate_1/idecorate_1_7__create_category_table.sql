BEGIN;
CREATE TABLE `categories` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `parent_id` integer,
    `name` varchar(256) NOT NULL,
    `order` integer,
    `created` date NOT NULL,
    `deleted` integer NOT NULL
)
;
ALTER TABLE `categories` ADD CONSTRAINT `parent_id_refs_ID_d28b8177` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`ID`);
CREATE TABLE `category_thumbnails` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `thumbnail` varchar(100) NOT NULL,
    `category_id` integer
)
;
ALTER TABLE `category_thumbnails` ADD CONSTRAINT `category_id_refs_ID_c4048c52` FOREIGN KEY (`category_id`) REFERENCES `categories` (`ID`);
CREATE INDEX `categories_63f17a16` ON `categories` (`parent_id`);
CREATE INDEX `category_thumbnails_42dc49bc` ON `category_thumbnails` (`category_id`);
COMMIT;