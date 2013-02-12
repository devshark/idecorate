from django.contrib.auth.models import User
from django.db import DatabaseError, transaction
from models import CustomerProfile, CustomerStyleBoard, StyleboardItems, StyleBoardCartItems
from cart.models import CartTemp, ProductPrice
import urllib2, urllib

@transaction.commit_manually
def register_user(data):
	try:
		user = User.objects.create_user(data['username'], "", data['password'])
		user.email = data['username']
		user.first_name = data['firstname']
		user.last_name = data['lastname']
		user.is_active = True
		user.save()

		cp = CustomerProfile()
		cp.user = user
		cp.nickname = data['username']
		cp.save()
		transaction.commit()
		return user
	except Exception as e:
		transaction.rollback()
		return None

def is_registered(uname):
	return User.objects.filter(username=uname).exists() or User.objects.filter(email=uname).exists()

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
		mode = 'new'
		if customer_styleboard:
			st = customer_styleboard.styleboard_item
			csb = customer_styleboard
			mode = 'edit'
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

		if 'personalize_total' in data:
			if data['personalize_total']:
				csb.total_price = data['personalize_total']
		
		if 'product_positions' in data['session_in_request']:
			p_position = data['session_in_request'].get('product_positions')
			if 'total' in p_position:
				csb.total_price = p_position.get('total','0.00')

		csb.styleboard_item = st
		csb.save()

		manage_styleboard_cart_items(data['sessionid'],st,mode)		
		transaction.commit()
		return csb
	except Exception as e:
		print "The error is: %s" % e	
		transaction.rollback()
		return False

def get_customer_styleboard_item(customer_styleboard):
	return CustomerStyleBoard.objects.get(id=customer_styleboard.id)

def manage_styleboard_cart_items(sessionid, styleboard_item, mode):
	print "The mode is: %s" % mode
	cart_temp_items = CartTemp.objects.filter(sessionid=sessionid)
	print "The cart_temp count is: %s" % cart_temp_items.count()
	if cart_temp_items.count()>0:
		for item in cart_temp_items:
			save_styleboard_cart_item(item.product, item.quantity, styleboard_item)
	"""
	delete item in StyleBoardCartItems when it is deleted
	"""
	if mode == 'edit':
		styleboard_cart = StyleBoardCartItems.objects.filter(styleboard_item=styleboard_item)
		for item_cart in styleboard_cart:
			is_exist = CartTemp.objects.filter(sessionid=sessionid, product=item_cart.product).count()
			if is_exist == 0:
				item_cart.delete()


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

def get_facebook_friends(access_token, name, limit, offset):

	#"https://graph.facebook.com/%s/members?%s" % (d['id'], urllib.urlencode({'access_token': response['access_token']}))
	if name:
		fql = "SELECT name, uid FROM user WHERE uid IN(SELECT uid2 FROM friend WHERE uid1 = me()) AND strpos(lower(name),lower('%s')) >=0 ORDER BY name LIMIT %s,%s" % (name, offset, limit)
	else:
		fql = "SELECT name, uid FROM user WHERE uid IN(SELECT uid2 FROM friend WHERE uid1 = me()) ORDER BY name LIMIT %s,%s" % (offset, limit)

	fql_url = "https://graph.facebook.com/fql?%s" % urllib.urlencode({'q':fql, 'access_token': access_token})
	ret = {}
	try:
		connection = urllib2.urlopen(fql_url)
		responseString = connection.read()
		connection.close()

		print "The fql is: %s" % fql
		#print "The url is: %s" % fql_url
		#print "The responseString is: %s" % responseString

		exec("ret=%s" % responseString)
		return ret
	except Exception as e:
		print "Error fetching friends: %s" % e
		return ret
