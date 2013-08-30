from django.db import models
from django.utils.translation import ugettext_lazy as _

# Create your models here.
class Countries( models.Model ):
    id                  = models.AutoField(db_column='id', primary_key=True)
    name                = models.CharField(db_column='name', max_length=64, blank=True)
    code                = models.CharField(db_column='code', max_length=16, blank=True)
    country_code        = models.CharField(db_column='country_code', max_length=16, blank=True)
    iso_numerical_code  = models.CharField(db_column='iso_numerical_code', max_length=3, blank=True)
    is_activated        = models.BooleanField(db_column="is_activated", default=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        db_table = 'countries'
        ordering = ["name"]
        verbose_name = _("Countries")


class QuickTip(models.Model):
    title   = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)

    class Meta:
        db_table = 'common_quick_tips'