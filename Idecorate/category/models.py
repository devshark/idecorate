from django.db import models
from django.utils.translation import ugettext_lazy as _

class Categories(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)
	parent = models.ForeignKey('self',db_column='parent_id', null=True)
	name = models.CharField(db_column='name', max_length=256, blank=True)
	order = models.IntegerField(db_column='order')
	created = models.DateField(db_column='created', auto_now_add=True, blank=True)

	class Meta:
		db_table = 'categories'
		ordering = ["id"]
		verbose_name = _("Categories")