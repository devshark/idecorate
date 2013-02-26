INSERT INTO `shop_taxclass` VALUES (1,'Test Tax','0.00',0);
INSERT INTO `product_guest_table` VALUES (1,'table'),(2,'guest');
INSERT INTO `product_guest_table` VALUES ('3', 'wedding');

ALTER TABLE shop_order MODIFY COLUMN notes longtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;
ALTER TABLE shop_orderpayment MODIFY COLUMN notes longtext CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL;