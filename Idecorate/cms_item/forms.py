import datetime
from django.conf import settings
from django import forms
from django.utils.translation import ugettext_lazy as _
from django.contrib.sites.models import Site
from django.contrib.flatpages.models import FlatPage
from flatpages.models import IdecoratePage, IdecoratePageItem

class AddFlatpageForm(forms.ModelForm):

    class Meta:
        model = FlatPage
        exclude = ('enable_comments','template_name','registration_required','status')

    def clean_title(self):
        id = self.instance.id
        title = self.cleaned_data['title']
        page = FlatPage.objects.filter(title__iexact=title)
        if page.exists():
            if page.all()[0].id == id:
                return title
            else:
                raise forms.ValidationError(_("This title already exists in the system."))
        return title

    def clean_url(self):
        id = self.instance.id
        url = self.cleaned_data['url']
        page = FlatPage.objects.filter(url__iexact=url)
        if page.exists():
            if page.all()[0].id == id:
                return url
            else:
                raise forms.ValidationError(_("This URL already exists in the system."))
        return url
    
# class AddWalletPageForm(forms.ModelForm):
    
#     class Meta:
#         model = WalletPage
        
#     def clean_slug(self):
#         id = self.instance.id
#         slug = self.cleaned_data['slug']
#         page = WalletPage.objects.filter(slug__exact=slug)
#         if page.exists():
#             if page.all()[0].id == id:
#                 return slug
#             else:
#                 raise forms.ValidationError(_("This slug already exists in the system."))
#         return slug
    
#     def clean_url(self):
#         from Wallet.util.resolver import resolve_to_name
#         from django.core.urlresolvers import Resolver404
        
#         id = self.instance.id
#         url = self.cleaned_data['url']
#         page = WalletPage.objects.filter(url__iexact=url)
#         if page.exists():
#             if not page.all()[0].id == id:
#                 raise forms.ValidationError(_("This URL already exists in the system."))
            
#         try:
#             name = resolve_to_name(url)
#             self.data['view_name'] = name
#             self.cleaned_data['view_name'] = name
#             if name == None:
#                 raise forms.ValidationError(_("This is not a valid URL in the system."))
#         except Resolver404:
#             raise forms.ValidationError(_("This is not a valid URL in the system."))
        
#         return url
    
# class AddWalletPageItemForm(forms.ModelForm):
    
#     class Meta:
#         model = WalletPageItem
        
#     def clean_slug(self):
#         id = self.instance.id
#         slug = self.cleaned_data['slug']
#         item = WalletPageItem.objects.filter(slug__exact=slug)
#         if item.exists():
#             if item.all()[0].id == id:
#                 return slug
#             else:
#                 raise forms.ValidationError(_("This slug already exists in the system."))
#         return slug