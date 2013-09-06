
from django import forms
from django.utils.translation import ugettext_lazy as _

from .models import NewsletterSubscriber, NewsletterTemplate

class NewsletterSubscriberForm(forms.ModelForm):

    class Meta:
        model  = NewsletterSubscriber
        fields = ['email',]


class NewsletterTemplateForm(forms.ModelForm):

    class Meta:
        model  = NewsletterTemplate
        fields = ['name','content',]


class EmailNewsletterForm(forms.Form):

    subject = forms.CharField(required=True,
                                error_messages={
                                    'required' : _('Subject is required'),
                                })
    content = forms.CharField(widget=forms.Textarea, 
                                required=True,
                                error_messages={
                                    'required' : _('Content is required')
                                })
    