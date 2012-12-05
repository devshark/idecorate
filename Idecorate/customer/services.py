from django.contrib.auth.models import User
from django.db import DatabaseError, transaction
from models import CustomerProfile, CustomerStyleBoard, StyleboardItems, CustomerStyleBoard, StyleBoardCartItems
from cart.models import CartTemp, ProductPrice

@transaction.commit_manually
def register_user(data):
	try:
		user = User.objects.create_user(data['username'], "", data['password'])
		user.email = data['username']
		user.first_name = ''
		user.last_name = ''
		user.is_active = True
		user.save()

		cp = CustomerProfile()
		cp.user = user
		cp.nickname = data['nickname']
		cp.save()
		transaction.commit()
		return user
	except Exception as e:
		transaction.rollback()
		return None

def is_registered(uname):
	return User.objects.filter(username=uname).exists()

def customer_profile(user):
	profile = {}
	picture = None
	description = None
	try:
		customer = CustomerProfile.objects.get(user=user)
		nickname = customer.nickname
		username = customer.user.username
		first_name = customer.user.first_name
		last_name = customer.user.last_name
		email = customer.user.email
		picture = customer.picture
		description = customer.description
	except:
		nickname = user.username
		username = nickname
		first_name = user.first_name
		last_name = user.last_name
		email = user.email

	profile['nickname'] = nickname
	profile['username'] = username
	profile['first_name'] = first_name
	profile['last_name'] = last_name
	profile['email'] = email
	profile['picture'] = picture
	profile['description'] = description

	return profile

def get_client_ip(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
		ip = x_forwarded_for.split(',')[-1].strip()
	else:
		ip = request.META.get('REMOTE_ADDR')
	return ip

def get_user_styleboard(user=None,styleboard_id=None):
	styleboards = None
	if user:
		styleboards = CustomerStyleBoard.objects.filter(user=user,styleboard_item__deleted=0)
	elif styleboard_id:
		try:
			styleboards = CustomerStyleBoard.objects.get(styleboard_item__id=styleboard_id)
		except:
			styleboards = None
	return styleboards

@transaction.commit_manually
def save_styleboard_item(data):
	try:
		customer_styleboard = data['customer_styleboard']
		if customer_styleboard:
			st = customer_styleboard.styleboard_item
			csb = customer_styleboard
		else:
			st = StyleboardItems()
			csb = CustomerStyleBoard()
		st.name = data['name']
		st.description = data['description']
		st.item = data['item']
		st.browser = data['browser']
		st.item_guest = data['guest']
		st.item_tables = data['tables']
		st.save()

		csb.user = data['user']
		csb.styleboard_item = st
		csb.save()

		manage_styleboard_cart_items(data['sessionid'],st)		
		transaction.commit()
		return csb
	except Exception as e:		
		transaction.rollback()
		return False

def get_customer_styleboard_item(customer_styleboard):
	return CustomerStyleBoard.objects.get(id=customer_styleboard.id)

def manage_styleboard_cart_items(sessionid, styleboard_item):
	cart_temp_items = CartTemp.objects.filter(sessionid=sessionid)	
	if cart_temp_items.count()>0:
		for item in cart_temp_items:
			save_styleboard_cart_item(item.product, item.quantity, styleboard_item)

def save_styleboard_cart_item(product, quantity, styleboard_item):	
	try:
		styleboard_cart = StyleBoardCartItems.objects.get(product=product, styleboard_item=styleboard_item)		
		if styleboard_cart.quantity != quantity:
			styleboard_cart.quantity = quantity
			styleboard_cart.save()
	except:
		styleboard_cart = StyleBoardCartItems()
		styleboard_cart.styleboard_item = styleboard_item
		styleboard_cart.product = product
		styleboard_cart.quantity = quantity
		styleboard_cart.save()

def get_save_styleboard_total(styleboard_item_id):
	items = StyleBoardCartItems.objects.filter(styleboard_item__id=styleboard_item_id)
	res = {}
	total_amount = 0
	for item in items:
		price = ProductPrice.objects.get(product=item.product)
		total_amount += (price._unit_price)*item.quantity

	return total_amount

def get_styleboard_cart_item(styleboard_item=None,styleboard_item_id=None):
	if styleboard_item:
		return StyleBoardCartItems.objects.filter(styleboard_item=styleboard_item).order_by('id')
	elif styleboard_item_id:
		return StyleBoardCartItems.objects.filter(styleboard_item__id=styleboard_item_id).order_by('id')
	return False

