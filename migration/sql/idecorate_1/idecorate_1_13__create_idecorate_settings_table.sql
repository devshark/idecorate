BEGIN;
CREATE TABLE `idecorate_settings` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `global_default_quantity` integer UNSIGNED NOT NULL,
    `global_table` integer UNSIGNED NOT NULL
)
;
COMMIT;

INSERT INTO `idecorate_settings` VALUES (1,1,1);