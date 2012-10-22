from django.db import models
from django.utils.translation import ugettext_lazy as _

from plata.product.models import ProductBase
from plata.shop.models import PriceBase
from category.models import Categories

class ProductGuestTable(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    name = models.CharField(db_column='name', max_length=64, blank=True)

    class Meta:
        db_table = 'product_guest_table'
        ordering = ["id"]
        verbose_name = _("Product Per Guest Table") 

class Product(ProductBase):

    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=100)
    slug = models.SlugField(_('slug'), unique=True, max_length=201)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)
    description = models.TextField(_('description'), blank=True)
    original_image = models.TextField(_('original_image'), blank=True)
    original_image_thumbnail = models.TextField(_('original_image_thumbnail'), blank=True)
    no_background = models.TextField(_('no_background'), blank=True)
    sku = models.CharField(_('sku'), max_length=100)
    categories = models.ManyToManyField(Categories)
    is_deleted = models.BooleanField(_('is active'), default=False)
    default_quantity = models.PositiveIntegerField(_('default_quantity'), default=1)
    guest_table = models.ForeignKey(ProductGuestTable, db_column='guest_table')

    class Meta:
        ordering = ['ordering', 'name']
        verbose_name = _('product')
        verbose_name_plural = _('products')
        db_table = 'product'

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('plata_product_detail', (), {'object_id': self.pk})


class ProductPrice(PriceBase):
    product = models.ForeignKey(Product, verbose_name=_('product'),
        related_name='prices')

    class Meta:
        get_latest_by = 'id'
        ordering = ['-id']
        verbose_name = _('price')
        verbose_name_plural = _('prices')
        db_table = 'product_price'

