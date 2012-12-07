CREATE TABLE `home_banners` (
    `ID` integer AUTO_INCREMENT NOT NULL PRIMARY KEY,
    `is_active` bool NOT NULL,
    `link` varchar(256) NOT NULL,
    `image_whole` varchar(100) NOT NULL,
    `image_half1` varchar(100) NOT NULL,
    `image_half2` varchar(100) NOT NULL,
    `image_third1` varchar(100) NOT NULL,
    `image_third2` varchar(100) NOT NULL,
    `image_third3` varchar(100) NOT NULL,
    `order` integer,
    `is_deleted` bool NOT NULL,
    `created` date NOT NULL
)
;
