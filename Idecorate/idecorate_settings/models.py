from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.

class IdecorateSettings(models.Model):

	id = models.AutoField(db_column='ID', primary_key=True)
	global_default_quantity = models.PositiveIntegerField(_('global_default_quantity'), default=1)
	global_table = models.PositiveIntegerField(_('global_table'), default=1)
	"""
    delivery_date_note = models.TextField(_('delivery_date_note'), blank=True)
    any_question = models.TextField(_('any_question'), blank=True)
	created = models.DateTimeField(db_column='CREATED', auto_now_add=True, blank=True)
	ip_address = models.CharField(db_column='IP_ADDRESS', max_length=64, blank=True)
	"""
	class Meta:
		db_table = 'idecorate_settings'
		ordering = ["id"]
		verbose_name = _("Idecorate Settings") 
