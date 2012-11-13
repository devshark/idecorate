from django.contrib.auth.models import User
from django.db import DatabaseError, transaction
from models import CustomerProfile

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
		print e
		transaction.rollback()
		return None

def is_registered(uname):
	return User.objects.filter(username=uname).exists()

def customer_profile(user):
	profile = {}
	try:
		customer = CustomerProfile.objects.get(user=user)
		nickname = customer.nickname
		username = customer.user.username
		first_name = customer.user.first_name
		last_name = customer.user.last_name
		email = customer.user.email
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

	return profile