from models import Product, ProductPrice
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

