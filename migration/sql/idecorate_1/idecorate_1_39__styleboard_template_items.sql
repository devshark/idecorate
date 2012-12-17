BEGIN;
CREATE TABLE `styleboard_template_items` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `name` varchar(256),
    `description` longtext,
    `item` longtext,
    `browser` varchar(100),
    `deleted` integer NOT NULL,
    `created` date NOT NULL
)
;
COMMIT;