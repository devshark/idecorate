
from django import forms

from .models import NewsletterSubscriber, NewsletterTemplate

class NewsletterSubscriberForm(forms.ModelForm):

	class Meta:
		model  = NewsletterSubscriber
		fields = ['email',]


class NewsletterTemplateForm(forms.ModelForm):

	class Meta:
		model  = NewsletterTemplate
		fields = ['name','content',]