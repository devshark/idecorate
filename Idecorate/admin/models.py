from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from stdimage import StdImageField

from PIL import Image

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
    title = models.CharField(db_column='title', max_length=256, blank=True)
    
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
    is_used = models.BooleanField(db_column='is_used', default=False)
    
    class Meta:
        db_table = 'embellishments'
        ordering = ["id"]
        verbose_name = _("Embellishments")

    @property
    def image_size(self):
        img = Image.open("%s%s%s" % (settings.MEDIA_ROOT, "embellishments/images/", self.image))
        width, height = img.size
        return {'width':width, 'height':height}  


class TextFonts(models.Model):
    id = models.AutoField(db_column='ID', primary_key=True)
    is_active = models.BooleanField(db_column="is_active", default=True)
    description = models.CharField(db_column='description', max_length=256, blank=True)
    font = models.CharField(db_column='font', max_length=256, blank=True)
    created = models.DateField(db_column='created', auto_now_add=True, blank=True)
    is_deleted = models.BooleanField(db_column='is_deleted', default=False)
    is_used = models.BooleanField(db_column='is_used', default=False)
    
    class Meta:
        db_table = 'text_fonts'
        ordering = ["id"]
        verbose_name = _("Text Fonts")

class HomeBanners(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    is_active = models.BooleanField(db_column="is_active", default=True)
    link = models.CharField(db_column='link', max_length=256, blank=True)
    image = StdImageField(upload_to='banners', blank=True, size=(322,400,True))
    order = models.IntegerField(db_column='order', null=True)
    size = models.IntegerField(db_column='size', null=True)
    is_deleted = models.BooleanField(db_column='is_deleted', default=False)
    created = models.DateField(db_column='created', auto_now_add=True, blank=True)

    class Meta:
        db_table = 'home_banners'
        ordering = ["created"]
        verbose_name = _("Home Banners")

    def get_image(self):
        return self.homebannerimages_set.all()[0].image

    def get_name(self):
        return self.homebannerimages_set.all()[0].name

class HomeBannerImages(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    home_banner = models.ForeignKey(HomeBanners)
    image = models.CharField(db_column='image', max_length=256)
    link = models.CharField(db_column='link', max_length=256)
    name = models.CharField(db_column='name', max_length=256)
    description = models.CharField(db_column='description', max_length=256)
    tinyUrl = models.CharField(db_column='tinyurl', max_length=256)

    class Meta:
        db_table = 'home_banner_images'
        verbose_name = _("Home Banner Images")

class HomeInfoGrapics(models.Model):
    id = models.AutoField(db_column='id', primary_key=True)
    image = models.CharField(db_column='image', max_length=256)
    is_active = models.BooleanField(db_column="is_active", default=False)
    is_deleted = models.BooleanField(db_column='is_deleted', default=False)
    created = models.DateField(db_column='created', auto_now_add=True, blank=True)

    class Meta:
        db_table = 'home_info_grapics'
        verbose_name = _("Home Info Grapics")