BEGIN;
CREATE TABLE `info_menu` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `parent_id` integer,
    `name` varchar(256) NOT NULL,
    `order` integer NOT NULL,
    `created` date NOT NULL
)
;
ALTER TABLE `info_menu` ADD CONSTRAINT `parent_id_refs_ID_22cfb85` FOREIGN KEY (`parent_id`) REFERENCES `info_menu` (`ID`);
CREATE TABLE `site_menu` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `parent_id` integer,
    `name` varchar(256) NOT NULL,
    `order` integer NOT NULL,
    `created` date NOT NULL
)
;
ALTER TABLE `site_menu` ADD CONSTRAINT `parent_id_refs_ID_78c535f3` FOREIGN KEY (`parent_id`) REFERENCES `site_menu` (`ID`);
CREATE TABLE `footer_menu` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `parent_id` integer,
    `name` varchar(256) NOT NULL,
    `order` integer NOT NULL,
    `created` date NOT NULL
)
;
ALTER TABLE `footer_menu` ADD CONSTRAINT `parent_id_refs_ID_3f55b077` FOREIGN KEY (`parent_id`) REFERENCES `footer_menu` (`ID`);
CREATE INDEX `info_menu_63f17a16` ON `info_menu` (`parent_id`);
CREATE INDEX `site_menu_63f17a16` ON `site_menu` (`parent_id`);
CREATE INDEX `footer_menu_63f17a16` ON `footer_menu` (`parent_id`);
COMMIT;
