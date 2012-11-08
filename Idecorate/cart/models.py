from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.models import User

from plata.product.models import ProductBase
from plata.shop.models import PriceBase
from category.models import Categories
from plata.shop.models import Order
from plata.fields import CurrencyField

class ProductGuestTable(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    name = models.CharField(db_column='name', max_length=64, blank=True)

    class Meta:
        db_table = 'product_guest_table'
        ordering = ["id"]
        verbose_name = _("Product Per Guest Table") 

class Product(ProductBase):

    is_active = models.BooleanField(_('is active'), default=True)
    name = models.CharField(_('name'), max_length=100, db_index=True)
    slug = models.SlugField(_('slug'), unique=True, max_length=201)
    ordering = models.PositiveIntegerField(_('ordering'), default=0)
    description = models.TextField(_('description'), blank=True, db_index=True)
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

class CartTemp(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    product = models.ForeignKey(Product, db_column='product_id')
    quantity = models.PositiveIntegerField(db_column='quantity')
    user = models.ForeignKey(User, db_column='user_id', null=True)
    sessionid = models.CharField(db_column='session_key', max_length=200, null=True)

    class Meta:
        verbose_name = _('Cart Temp')
        db_table = 'cart_temps'

class ProductPopularity(models.Model):    
    product = models.OneToOneField(Product, db_column='product_id', primary_key=True)
    dropped = models.PositiveIntegerField(db_column='dropped')

    class Meta:
        verbose_name = _('Product Popularity')
        db_table = 'product_popularities'

class GuestTableTemp(models.Model):

    id = models.AutoField(db_column='id', primary_key=True)
    guests = models.PositiveIntegerField(_('guests'), default=1)
    tables = models.PositiveIntegerField(_('tables'), default=1)
    sessionid = models.CharField(db_column='session_key', max_length=200, null=True)

    class Meta:
        verbose_name = _('Temporary Guest and Tables')
        db_table = 'guest_tables_temps'

class GuestTable(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    guests = models.PositiveIntegerField(_('guests'), default=1)
    tables = models.PositiveIntegerField(_('tables'), default=1)
    order = models.ForeignKey(Order, db_column='order_id')

    class Meta:
        verbose_name = _('Guest and Tables')
        db_table = 'guest_tables'

class Contact(models.Model):
    ADDRESS_FIELDS = ['first_name', 'last_name', 'address',
        'zip_code', 'city']

    user = models.OneToOneField(User, verbose_name=_('user'),
        related_name='contact_user')
    #currency = CurrencyField(help_text=_('Preferred currency.'))

    first_name = models.CharField(_('first name'), max_length=100)
    last_name = models.CharField(_('last name'), max_length=100)
    address = models.TextField(_('address'))
    address2 = models.TextField(_('address2'))
    state = models.CharField(_('state'), max_length=100)
    zip_code = models.CharField(_('ZIP code'), max_length=50)
    city = models.CharField(_('city'), max_length=100)
    shipping_same_as_billing = models.BooleanField(_('shipping address equals billing address'),default=True)
    currency = CurrencyField(help_text=_('Preferred currency.'))

    def __unicode__(self):
        return unicode(self.user)

    def update_from_order(self, order, request=None):

        self.currency = order.currency
        self.shipping_same_as_billing = order.shipping_same_as_billing
        
        for field in self.ADDRESS_FIELDS:

            f = 'shipping_' + field

            if hasattr(order, f):
                setattr(self, f, getattr(order, f))

            f = 'billing_' + field

            if hasattr(order, f):
                setattr(self, field, getattr(order, f))