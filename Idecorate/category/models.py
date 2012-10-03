from django.db import models
from django.utils.translation import ugettext_lazy as _
from stdimage import StdImageField
from django.conf import settings

class Categories(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)
	parent = models.ForeignKey('self',db_column='parent_id', null=True)
	name = models.CharField(db_column='name', max_length=256, blank=True)
	order = models.IntegerField(db_column='order', null=True)	
	created = models.DateField(db_column='created', auto_now_add=True, blank=True)
	deleted = models.IntegerField(db_column='deleted', default=0)

	class Meta:
		db_table = 'categories'
		ordering = ["order"]
		verbose_name = _("Categories")

class CategoryThumbnail(models.Model):
	id = models.AutoField(db_column='ID', primary_key=True)
	thumbnail = StdImageField(upload_to='categories/thumbnail')
	category = models.ForeignKey(Categories, db_column='category_id', null=True)

	class Meta:
		db_table = 'category_thumbnails'
		verbose_name = _("Categories Thumbnail")
