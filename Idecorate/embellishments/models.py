from django.db import models
from django.utils.translation import ugettext_lazy as _

class StyleboardTemplateItems(models.Model):
	id = models.AutoField(db_column='id', primary_key=True)
	name = models.CharField(db_column="name", max_length=256, null=True)
	description = models.TextField(db_column='description', null=True)
	item = models.TextField(db_column='item', null=True)
	browser = models.CharField(db_column='browser', max_length=100, null=True)
	deleted = models.IntegerField(db_column='deleted', default=0)
	created = models.DateField(db_column='created', auto_now_add=True, blank=True)
	is_used = models.BooleanField(db_column="is_used", default=False);

	class Meta:
		db_table = 'styleboard_template_items'
		verbose_name = _("Styleboard Template Items")