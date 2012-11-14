from django.db import models
from django.utils.translation import ugettext_lazy as _
from stdimage import StdImageField
from django.conf import settings
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	nickname = models.CharField(db_column='nickname', max_length=256, db_index=True)
	picture = models.CharField(db_column='picture', max_length=256, null=True)
	description = models.TextField(db_column='description', max_length=256, null=True)

	class Meta:
		db_table = 'customer_profiles'
		verbose_name = _("Customer Profiles")

class StyleboardItems(models.Model):
	id = models.AutoField(db_column='id', primary_key=True)

	class Meta:
		db_table = 'styleboard_itemss'
		verbose_name = _("Styleboard Items")

class CustomerStyleBoard(models.Model):
	id = models.AutoField(db_column='id', primary_key=True)
	user = models.ForeignKey(User, db_column='user_id')

	class Meta:
		db_table = 'customer_styleboards'
		verbose_name = _("Customer Styleboards")
