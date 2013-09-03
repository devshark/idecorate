
from django import forms

from .models import NewsletterSubscriber

class NewsletterSubscriberForm(models.ModelForm):

	class Meta:
		model  = NewsletterSubscriber
		fields = ['email',]