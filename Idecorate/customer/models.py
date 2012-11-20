from django.db import models
from django.utils.translation import ugettext_lazy as _
from stdimage import StdImageField
from django.conf import settings
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	nickname = models.CharField(db_column='nickname', max_length=256, db_index=True)
	picture = models.CharField(db_column='picture', max_length=256, null=True)
	description = models.TextField(db_column='description', null=True)

	class Meta:
		db_table = 'customer_profiles'
		verbose_name = _("Customer Profiles")

class StyleboardItems(models.Model):
	id = models.AutoField(db_column='id', primary_key=True)
	name = models.CharField(db_column="name", max_length=256, null=True)
	description = models.TextField(db_column='description', null=True)
	item = models.TextField(db_column='item', null=True)
	browser = models.CharField(db_column='browser', max_length=100, null=True)
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
