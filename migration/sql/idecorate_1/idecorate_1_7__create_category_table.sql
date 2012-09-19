CREATE TABLE `categories` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `parent_id` integer,
    `name` varchar(256) NOT NULL,
    `order` integer NOT NULL,
    `created` date NOT NULL
)
;
COMMIT;
