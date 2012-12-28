from django import forms
from django.conf import settings
from django.contrib.flatpages.models import FlatPage
from django.utils.translation import ugettext, ugettext_lazy as _

class EditFlatpageForm(forms.ModelForm):

    url = forms.RegexField(label=_("URL"), max_length=100, regex=r'^[-\w/\.~]+$',
        help_text = _("Example: '/about/contact/'. Make sure to have leading"
            " and trailing slashes. Site pages will be created under the /sites/ directory."),
        error_message = _("This value must contain only letters, numbers,"
            " dots, underscores, dashes, slashes or tildes."))  

    class Meta:
        model = FlatPage

    def clean_url(self):        
        url = self.cleaned_data['url']
        if not url.startswith('/'):
            raise forms.ValidationError(ugettext("URL is missing a leading slash."))
        if (settings.APPEND_SLASH and
            'django.middleware.common.CommonMiddleware' in settings.MIDDLEWARE_CLASSES and
            not url.endswith('/')):
            raise forms.ValidationError(ugettext("URL is missing a trailing slash."))
        return url