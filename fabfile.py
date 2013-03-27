from fabric.api import *
from time import gmtime, strftime

"""
	Please change these configurations
"""
STAGING_USER = "ferdinand"
PRODUCTION_USER = STAGING_USER

STAGING_HOST = "idecorate-b.staging.kitesystems.com"
PRODUCTION_HOST = "172.29.38.48"

"""
	except these configurations
"""
NOW_TIME = strftime("%Y-%m-%d",gmtime())
BUNDLE_FILE = "Wedding-%s.tar.gz" % NOW_TIME
TMP_DIR = "idecorateweddings-%s" % NOW_TIME
BACKUP_DIR = "idecoratebackups-%s" % NOW_TIME
BACKUP_BUNDLE = "idecoratesrcWedding-%s" % NOW_TIME
BACKUP_SQL = "idecoratesql-%s.sql" % NOW_TIME

"""
env.hosts = [
				'%s@%s' % (STAGING_USER, STAGING_HOST), 
				'%s@%s' % (PRODUCTION_USER, PRODUCTION_HOST)
			]
"""
def staging():

	env.host_string = '%s@%s' % (STAGING_USER, STAGING_HOST)

def production():

	env.host_string = '%s@%s' % (PRODUCTION_USER, PRODUCTION_HOST)


def create_staging_tar():
	
	with cd("~"):
		run("mkdir -p ~/workspace/%s" % TMP_DIR)

	with cd("~/workspace/%s" % TMP_DIR):

		run("tar --create --gzip --owner=root --group=www-data --numeric-owner --preserve-permissions -f %s -C /var/www/src --exclude=./Wedding/Idecorate/media/banners --exclude=./Wedding/Idecorate/media/categories --exclude=./Wedding/Idecorate/media/embellishments --exclude=./Wedding/Idecorate/media/fonts --exclude=./Wedding/Idecorate/media/infographics --exclude=./Wedding/Idecorate/media/products --exclude=./Wedding/Idecorate/media/profiles --exclude=./Wedding/Idecorate/Idecorate/localsettings.py --exclude=.gitignore ./Wedding/" % BUNDLE_FILE)
		run("tar -tf %s" % BUNDLE_FILE)
		run("ls -hl %s" % BUNDLE_FILE)

	local("scp %s@%s:/home/%s/workspace/%s/%s ." % (STAGING_USER, STAGING_HOST, STAGING_USER, TMP_DIR, BUNDLE_FILE))
	local("scp ./%s %s@%s:/home/%s" % (BUNDLE_FILE, PRODUCTION_USER, PRODUCTION_HOST, PRODUCTION_USER))

	#local('sudo service httpd restart',capture=True)

def manage_files_production():
	with cd("~"):
		run("mkdir -p ~/workspace/%s" % BACKUP_DIR)	

	with cd("~/workspace/%s" % BACKUP_DIR):
		run("tar -czf %s -C /var/www/www.idecorateweddings.com/src/ ./Wedding/" % BACKUP_BUNDLE)
		run("mysqldump -u idecorate -h db.local.hosting.kitesystems.com -p --add-drop-table idecorate > %s" % BACKUP_SQL)
		run("gzip %s" % BACKUP_SQL)
		run("ls -lh")

	with cd("~"):
		run("sudoedit /var/www/www.idecorateweddings.com/src/Wedding/Idecorate/Idecorate/localsettings.py")
		run("sudo tar -xf %s -C /var/www/www.idecorateweddings.com/src/" % BUNDLE_FILE, capture=True)
		run("sudo chown -R www-data /var/www/www.idecorateweddings.com/src/Wedding/Idecorate/media/banners/", capture=True)
		run("sudo chown -R www-data /var/www/www.idecorateweddings.com/src/Wedding/Idecorate/media/categories/", capture=True)
		run("sudo chown -R www-data /var/www/www.idecorateweddings.com/src/Wedding/Idecorate/media/embellishments/", capture=True)
		run("sudo chown -R www-data /var/www/www.idecorateweddings.com/src/Wedding/Idecorate/media/fonts/", capture=True)
		run("sudo chown -R www-data /var/www/www.idecorateweddings.com/src/Wedding/Idecorate/media/infographics/", capture=True)
		run("sudo chown -R www-data /var/www/www.idecorateweddings.com/src/Wedding/Idecorate/media/products/", capture=True)
		run("sudo chown -R www-data /var/www/www.idecorateweddings.com/src/Wedding/Idecorate/media/profiles/", capture=True)
		run("sudo find /var/www/www.idecorateweddings.com/src/Wedding/ -name \"*.pyc\" -delete", capture=True)
		run("sudo touch /var/www/www.idecorateweddings.com/src/django.wsgi", capture=True)
		run("sudo service apache2 reload", capture=True)
"""
	Main deployment script
"""
def deploy_it():
	staging()
	create_staging_tar()

	production()
	manage_files_production()
