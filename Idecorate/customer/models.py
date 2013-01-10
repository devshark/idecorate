from django.db import models
from django.utils.translation import ugettext_lazy as _
from stdimage import StdImageField
from django.conf import settings
from django.contrib.auth.models import User
from cart.models import Product

class CustomerProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	nickname = models.CharField(db_column='nickname', max_length=256, db_index=True)
	picture = models.CharField(db_column='picture', max_length=256, null=True)
	description = models.TextField(db_column='description', null=True)
	hash_set_password = models.CharField(db_column='hash_set_password', max_length=256, null=True)

	class Meta:
		db_table = 'customer_profiles'
		verbose_name = _("Customer Profiles")

class CustomerFacebookFriends(models.Model):
	id = models.AutoField(db_column='id', primary_key=True)
	user = models.ForeignKey(User, db_column='user_id')
	friend_id = models.CharField(db_column='friend_id', max_length=256)
	friend_name = models.CharField(db_column='friend_name', max_length=256)
	friend_image = models.CharField(db_column='friend_image', max_length=256)

	class Meta:
		db_table = 'customer_facebook_friends'
		verbose_name = _("Customer Facebook Friends")

class StyleboardItems(models.Model):
	id = models.AutoField(db_column='id', primary_key=True)
	name = models.CharField(db_column="name", max_length=256, null=True)
	description = models.TextField(db_column='description', null=True)
	item = models.TextField(db_column='item', null=True)
	browser = models.CharField(db_column='browser', max_length=100, null=True)
	item_guest = models.IntegerField(null=True)
	item_tables = models.IntegerField(null=True)
	deleted = models.IntegerField(db_column='deleted', default=0)
	created = models.DateField(db_column='created', auto_now_add=True, blank=True)

	class Meta:
		db_table = 'styleboard_items'
		verbose_name = _("Styleboard Items")

class CustomerStyleBoard(models.Model):
	id = models.AutoField(db_column='id', primary_key=True)
	user = models.ForeignKey(User, db_column='user_id')
	styleboard_item = models.ForeignKey(StyleboardItems, db_column='styleboard_item_id', blank=True)
	created = models.DateField(db_column='created', auto_now_add=True, blank=True)

	class Meta:
		db_table = 'customer_styleboards'
		verbose_name = _("Customer Styleboards")

class StyleBoardCartItems(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    styleboard_item = models.ForeignKey(StyleboardItems, db_column='styleboard_item_id')
    product = models.ForeignKey(Product, db_column='product_id')
    quantity = models.PositiveIntegerField(db_column='quantity')

    class Meta:
        verbose_name = _('Styleboard Cart Items')
        db_table = 'styleboard_cart_items'
