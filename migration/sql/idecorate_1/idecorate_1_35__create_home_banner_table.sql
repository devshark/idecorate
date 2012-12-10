CREATE TABLE `home_banners` (
    `id` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `is_active` bool NOT NULL,
    `link` varchar(256) NOT NULL,
    `image` varchar(100) NOT NULL,
    `order` integer,
    `is_deleted` bool NOT NULL,
    `created` date NOT NULL
)
;