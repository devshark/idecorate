from django.contrib.auth.models import User
from django.db import DatabaseError, transaction
from models import CustomerProfile

@transaction.commit_manually
def register_user(data):
	try:
		user = User.objects.create_user(data['username'], "", data['password'])
		user.email = data['username']
		user.first_name = None
		user.last_name = None
		user.is_active = True
		user.save()

		cp = CustomerProfile()
		cp.user = user
		cp.nickname = dta['nickname']
		cp.save()
		transaction.commit()
		return user
	except Exception as e:
		return None

def is_registered(uname):
	return User.objects.filter(username=uname).exists()
