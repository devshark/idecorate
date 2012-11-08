CREATE TABLE `guest_tables_temps` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `guests` integer UNSIGNED NOT NULL,
    `tables` integer UNSIGNED NOT NULL,
    `session_key` varchar(200)
)
;