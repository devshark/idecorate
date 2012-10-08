BEGIN;
CREATE TABLE `categories` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `parent_id` integer,
    `name` varchar(256) NOT NULL,
    `thumbnail` varchar(256),
    `order` integer,
    `created` date NOT NULL,
    `deleted` integer NOT NULL
)
;
ALTER TABLE `categories` ADD CONSTRAINT `parent_id_refs_ID_d28b8177` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`ID`);
CREATE TABLE `category_thumbnail_temps` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `thumbnail` varchar(100) NOT NULL
)
;
CREATE INDEX `categories_63f17a16` ON `categories` (`parent_id`);
COMMIT;