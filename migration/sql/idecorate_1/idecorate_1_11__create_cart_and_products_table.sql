CREATE TABLE `contact_contact` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `billing_company` varchar(100) NOT NULL,
  `billing_first_name` varchar(100) NOT NULL,
  `billing_last_name` varchar(100) NOT NULL,
  `billing_address` longtext NOT NULL,
  `billing_zip_code` varchar(50) NOT NULL,
  `billing_city` varchar(100) NOT NULL,
  `billing_country` varchar(3) NOT NULL,
  `shipping_same_as_billing` tinyint(1) NOT NULL,
  `shipping_company` varchar(100) NOT NULL,
  `shipping_first_name` varchar(100) NOT NULL,
  `shipping_last_name` varchar(100) NOT NULL,
  `shipping_address` longtext NOT NULL,
  `shipping_zip_code` varchar(50) NOT NULL,
  `shipping_city` varchar(100) NOT NULL,
  `shipping_country` varchar(3) NOT NULL,
  `user_id` int(11) NOT NULL,
  `dob` date DEFAULT NULL,
  `created` datetime NOT NULL,
  `currency` varchar(3) NOT NULL,
  `notes` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `user_id` (`user_id`)
);

CREATE TABLE `discount_applieddiscount` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `type` int(10) unsigned NOT NULL,
  `value` decimal(18,10) NOT NULL,
  `currency` varchar(3) DEFAULT NULL,
  `tax_class_id` int(11) DEFAULT NULL,
  `config` longtext NOT NULL,
  `order_id` int(11) NOT NULL,
  `code` varchar(30) NOT NULL,
  `remaining` decimal(18,10) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `discount_applieddiscount_17c56b03` (`tax_class_id`),
  KEY `discount_applieddiscount_7cc8fcf5` (`order_id`)
);

CREATE TABLE `discount_discount` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `type` int(10) unsigned NOT NULL,
  `value` decimal(18,10) NOT NULL,
  `currency` varchar(3) DEFAULT NULL,
  `tax_class_id` int(11) DEFAULT NULL,
  `config` longtext NOT NULL,
  `code` varchar(30) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `valid_from` date NOT NULL,
  `valid_until` date DEFAULT NULL,
  `allowed_uses` int(11) DEFAULT NULL,
  `used` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `code` (`code`),
  KEY `discount_discount_17c56b03` (`tax_class_id`)
);

CREATE TABLE `product` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `is_active` tinyint(1) NOT NULL,
  `name` varchar(100) NOT NULL,
  `slug` varchar(50) NOT NULL,
  `ordering` int(10) unsigned NOT NULL,
  `description` longtext NOT NULL,
  `original_image` longtext NOT NULL,
  `original_image_thumbnail` longtext NOT NULL,
  `no_background` longtext NOT NULL,
  `sku` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `slug` (`slug`)
);

CREATE TABLE `product_price` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `currency` varchar(3) NOT NULL,
  `_unit_price` decimal(18,10) NOT NULL,
  `tax_included` tinyint(1) NOT NULL,
  `tax_class_id` int(11) NOT NULL,
  `product_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `product_price_17c56b03` (`tax_class_id`),
  KEY `product_price_44bdf3ee` (`product_id`)
);

CREATE TABLE `shop_order` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `billing_company` varchar(100) NOT NULL,
  `billing_first_name` varchar(100) NOT NULL,
  `billing_last_name` varchar(100) NOT NULL,
  `billing_address` longtext NOT NULL,
  `billing_zip_code` varchar(50) NOT NULL,
  `billing_city` varchar(100) NOT NULL,
  `billing_country` varchar(3) NOT NULL,
  `shipping_same_as_billing` tinyint(1) NOT NULL,
  `shipping_company` varchar(100) NOT NULL,
  `shipping_first_name` varchar(100) NOT NULL,
  `shipping_last_name` varchar(100) NOT NULL,
  `shipping_address` longtext NOT NULL,
  `shipping_zip_code` varchar(50) NOT NULL,
  `shipping_city` varchar(100) NOT NULL,
  `shipping_country` varchar(3) NOT NULL,
  `created` datetime NOT NULL,
  `confirmed` datetime DEFAULT NULL,
  `user_id` int(11) DEFAULT NULL,
  `language_code` varchar(10) NOT NULL,
  `status` int(10) unsigned NOT NULL,
  `_order_id` varchar(20) NOT NULL,
  `email` varchar(75) NOT NULL,
  `currency` varchar(3) NOT NULL,
  `items_subtotal` decimal(18,10) NOT NULL,
  `items_discount` decimal(18,10) NOT NULL,
  `items_tax` decimal(18,10) NOT NULL,
  `shipping_method` varchar(100) NOT NULL,
  `shipping_cost` decimal(18,10) DEFAULT NULL,
  `shipping_discount` decimal(18,10) DEFAULT NULL,
  `shipping_tax` decimal(18,10) NOT NULL,
  `total` decimal(18,10) NOT NULL,
  `paid` decimal(18,10) NOT NULL,
  `notes` longtext NOT NULL,
  `data` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `shop_order_403f60f` (`user_id`)
);

CREATE TABLE `shop_orderitem` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `product_id` int(11) DEFAULT NULL,
  `name` varchar(100) NOT NULL,
  `sku` varchar(100) NOT NULL,
  `quantity` int(11) NOT NULL,
  `currency` varchar(3) NOT NULL,
  `_unit_price` decimal(18,10) NOT NULL,
  `_unit_tax` decimal(18,10) NOT NULL,
  `tax_rate` decimal(10,2) NOT NULL,
  `tax_class_id` int(11) DEFAULT NULL,
  `is_sale` tinyint(1) NOT NULL,
  `_line_item_price` decimal(18,10) NOT NULL,
  `_line_item_discount` decimal(18,10) DEFAULT NULL,
  `_line_item_tax` decimal(18,10) NOT NULL,
  `data` longtext NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `order_id` (`order_id`,`product_id`),
  KEY `shop_orderitem_7cc8fcf5` (`order_id`),
  KEY `shop_orderitem_44bdf3ee` (`product_id`),
  KEY `shop_orderitem_17c56b03` (`tax_class_id`)
);

CREATE TABLE `shop_orderpayment` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `timestamp` datetime NOT NULL,
  `status` int(10) unsigned NOT NULL,
  `currency` varchar(3) NOT NULL,
  `amount` decimal(10,2) NOT NULL,
  `payment_module_key` varchar(20) NOT NULL,
  `payment_module` varchar(50) NOT NULL,
  `payment_method` varchar(50) NOT NULL,
  `transaction_id` varchar(50) NOT NULL,
  `authorized` datetime DEFAULT NULL,
  `notes` longtext NOT NULL,
  `data` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `shop_orderpayment_7cc8fcf5` (`order_id`)
);

CREATE TABLE `shop_orderstatus` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `order_id` int(11) NOT NULL,
  `created` datetime NOT NULL,
  `status` int(10) unsigned NOT NULL,
  `notes` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `shop_orderstatus_7cc8fcf5` (`order_id`)
);

CREATE TABLE `shop_taxclass` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `rate` decimal(10,2) NOT NULL,
  `priority` int(10) unsigned NOT NULL,
  PRIMARY KEY (`id`)
);

INSERT INTO `shop_taxclass` VALUES (1,'Test Tax','0.00',0);