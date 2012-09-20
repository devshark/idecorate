BEGIN;
CREATE TABLE `categories` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `parent_id` integer,
    `name` varchar(256) NOT NULL,
    `order` integer NOT NULL,
    `created` date NOT NULL
)
;
ALTER TABLE `categories` ADD CONSTRAINT `parent_id_refs_ID_d28b8177` FOREIGN KEY (`parent_id`) REFERENCES `categories` (`ID`);
CREATE INDEX `categories_63f17a16` ON `categories` (`parent_id`);
COMMIT;