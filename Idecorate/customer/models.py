from django.db import models
from django.utils.translation import ugettext_lazy as _
from stdimage import StdImageField
from django.conf import settings
from django.contrib.auth.models import User

class CustomerProfile(models.Model):
	user = models.OneToOneField(User, primary_key=True)
	nickname = models.CharField(db_column='nickname', max_length=256, db_index=True)
	picture = 	models.CharField(db_column='picture', max_length=256, null=True)

	class Meta:
		db_table = 'customer_profiles'
		verbose_name = _("Customer Profiles")