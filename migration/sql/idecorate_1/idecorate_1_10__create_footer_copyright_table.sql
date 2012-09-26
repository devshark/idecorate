ALTER TABLE `footer_menu` ADD CONSTRAINT `parent_id_refs_ID_3f55b077` FOREIGN KEY (`parent_id`) REFERENCES `footer_menu` (`ID`);
CREATE TABLE `footer_copyright` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `created` date NOT NULL,
    `copyright` varchar(256) NOT NULL
)
;

INSERT INTO `footer_copyright` VALUES (1,'2012-09-25','&copy; iDecorate');