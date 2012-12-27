from django.db import models
from django.template.defaultfilters import slugify
from django.utils.translation import ugettext_lazy as _


class IdecoratePage(models.Model):
    url     = models.CharField(db_column='url', max_length=100, db_index=True)
    name    = models.CharField(db_column='name', max_length=64)
    view_name = models.CharField(db_column='view_name', max_length=64, blank=True)
    slug    = models.SlugField(db_column='slug', max_length=64)
    status  = models.IntegerField(db_column='status', default=0)
    
    def __unicode__(self):
        return u"%s -- %s" % (self.url, self.name)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(WalletPage, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'idecorate_page'
        verbose_name = _("Idecorate Page")
        
class IdecoratePageItem(models.Model):
    page        = models.ForeignKey(WalletPage, db_column='idecorate_page_id')
    name        = models.CharField(db_column='name', max_length=64)
    slug        = models.SlugField(db_column='slug', max_length=64)
    content     = models.TextField(blank=True)
    status      = models.IntegerField(db_column='status', default=0)
    
    def __unicode__(self):
        return u"%s" % (self.name)
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super(WalletPageItem, self).save(*args, **kwargs)
    
    class Meta:
        db_table = 'idecorate_page_item'
        verbose_name = _("Idecorate Page Item")