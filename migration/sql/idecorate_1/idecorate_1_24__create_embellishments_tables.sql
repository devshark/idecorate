BEGIN;
CREATE TABLE `embellishments_type` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `description` varchar(256) NOT NULL
)
;
CREATE TABLE `embellishments` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `is_active` bool NOT NULL,
    `description` varchar(256) NOT NULL,
    `embellishments_type_id` integer,
    `image` varchar(256) NOT NULL,
    `image_thumb` varchar(256) NOT NULL,
    `created` date NOT NULL
)
;
ALTER TABLE `embellishments` ADD CONSTRAINT `embellishments_type_id_refs_ID_4687159` FOREIGN KEY (`embellishments_type_id`) REFERENCES `embellishments_type` (`ID`);
COMMIT;