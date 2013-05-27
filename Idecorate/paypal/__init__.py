from django.conf import settings
import urllib

class PayPal(object):
	
	def __init__(self, *args, **kwargs):
		self.cmd = kwargs.get('cmd','_cart')
		self.business = kwargs.get('business', settings.PAYPAL_EMAIL)
		self.currency_code = kwargs.get('currency_code', 'USD')
		self.upload = kwargs.get('upload', '1')
		self.return_url = kwargs.get('return_url',settings.PAYPAL_RETURN_URL)
		self.cancel_return_url = kwargs.get('cancel_return_url','')
		self.custom = kwargs.get('custom','')
		self.items = []

	def addItems(self, item):
		self.items.append(item.__dict__)

	def generateInputForm(self):

		form = ''

		for k,v in self.__dict__.items():

			if type(v) == type([]):
				if len(v) > 0:
					#generate items
					for n, item in enumerate(v):
						for k2,v2 in item.items():
							form += '<input type="hidden" name="%s_%s" value="%s" />' % (k2, n + 1, v2)
			else:
				form += '<input type="hidden" name="%s" value="%s" />' % (k.replace("_url", ""), v)

		return form

	@staticmethod
	def isSuccessfull(**kwargs):

		postData = {} 

		postData['st'] = kwargs.get('st','')
		postData['tx'] = kwargs.get('tx','')
		postData['cmd'] = "_notify-synch"
		postData['at'] = settings.PAYPAL_PDT_TOKEN

		pdt = urllib.urlopen(settings.PAYPAL_PDT_URL, urllib.urlencode(postData)).read()
		lines = pdt.split("\n")

		return True if lines[0].strip() == "SUCCESS" and postData['st'].strip() == "Completed" else False

class PayPalItem(object):
	
	def __init__(self, **kwargs):
		self.item_number = kwargs.get('item_number','')
		self.item_name = kwargs.get('item_name','')
		self.quantity = kwargs.get('quantity','')
		self.amount = kwargs.get('amount','')