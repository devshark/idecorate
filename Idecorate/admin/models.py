from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class LoginLog(models.Model):

	id = models.AutoField(db_column='ID', primary_key=True)
	created = models.DateTimeField(db_column='CREATED', auto_now_add=True, blank=True)
	ip_address = models.CharField(db_column='IP_ADDRESS', max_length=64, blank=True)

	class Meta:
		db_table = 'LOGIN_LOG'
		ordering = ["id"]
		verbose_name = _("Login Log") 

class EmbellishmentsType(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)
	name = models.CharField(db_column='description', max_length=256, blank=True)
	
	class Meta:
		db_table = 'embellishments_type'
		ordering = ["id"]
		verbose_name = _("Embellishments Type")

class Embellishments(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)
	is_active = models.BooleanField(db_column="is_active", default=True)
	description = models.CharField(db_column='description', max_length=256, blank=True)
	e_type = models.ForeignKey(EmbellishmentsType,db_column='embellishments_type_id', null=True)
	image = models.CharField(db_column='image', max_length=256, blank=True)
	image_thumb = models.CharField(db_column='image_thumb', max_length=256, blank=True)
	created = models.DateField(db_column='created', auto_now_add=True, blank=True)
	is_deleted = models.BooleanField(db_column='is_deleted', default=False)
	
	class Meta:
		db_table = 'embellishments'
		ordering = ["id"]
		verbose_name = _("Embellishments")


class TextFonts(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)
	is_active = models.BooleanField(db_column="is_active", default=True)
	description = models.CharField(db_column='description', max_length=256, blank=True)
	font = models.CharField(db_column='font', max_length=256, blank=True)
	created = models.DateField(db_column='created', auto_now_add=True, blank=True)
	is_deleted = models.BooleanField(db_column='is_deleted', default=False)
	
	class Meta:
		db_table = 'text_fonts'
		ordering = ["id"]
		verbose_name = _("Text Fonts")