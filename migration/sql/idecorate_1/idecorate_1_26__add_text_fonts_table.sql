CREATE TABLE `text_fonts` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `is_active` bool NOT NULL,
    `description` varchar(256) NOT NULL,
    `font` varchar(256) NOT NULL,
    `created` date NOT NULL
)
;