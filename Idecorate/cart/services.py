from models import Product, ProductPrice, CartTemp, GuestTableTemp,ProductDetails
from random import choice
from string import digits, letters
from django.contrib.auth.models import User

def generate_unique_id(length=32):
    s = ''
    for i in range(length):
        s += choice(digits + letters)
    return s

def get_product(prod_id):
	product = ProductPrice.objects.get(product__id=int(prod_id))
	return product

def get_product_detail(prod_id):

	ProductDetail = ProductDetails.objects.get(product_id = int(prod_id))

	return ProductDetail

def remove_from_cart_temp(cart_temp_id):
	ct = CartTemp.objects.get(id=cart_temp_id)
	ct.delete()

def clear_cart_temp(session_id):
	ct = CartTemp.objects.filter(sessionid=session_id)
	for c in ct:
		remove_from_cart_temp(c.id)

def add_to_cart(data):
	exists = CartTemp.objects.filter(product=data['product'],sessionid=data['sessionid']).exists()
	existsGT = GuestTableTemp.objects.filter(sessionid=data['sessionid']).exists()		

	if not exists:
		cartTemp = CartTemp()
		cartTemp.product = data['product']
		cartTemp.quantity = data['quantity']
		cartTemp.sessionid = data['sessionid']
		cartTemp.save()

	if not existsGT:
		guestTable = GuestTableTemp()
		guestTable.guests = data['guests']
		guestTable.tables = data['tables']
		guestTable.wedding = data['wedding'] # edited added weding option -ryan -02152013
		guestTable.sessionid = data['sessionid']
		guestTable.save()
