# Django settings for Idecorate project.
import os
PROJECT_PATH = os.path.dirname(__file__)
SITE_ROOT = os.path.dirname(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

EMAIL_HOST = '127.0.0.1'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_USE_TLS = True

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'idecorate_refactor',                      # Or path to database file if using sqlite3.
        'USER': 'root',                      # Not used with sqlite3.
        'PASSWORD': '',                  # Not used with sqlite3.
        'HOST': '127.0.0.1',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Asia/Manila'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
# MEDIA_ROOT = "%s%s" % (PROJECT_PATH, "/../media/")
MEDIA_ROOT = os.path.join(SITE_ROOT, 'media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = 'media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(SITE_ROOT, 'assets')

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(SITE_ROOT, 'static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '-+f5p%49+o7$9dv-=uyj*25he61vxz*8n$ukdxn_f9w^es7vso'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)


AUTHENTICATION_BACKENDS = (
    'social_auth.backends.twitter.TwitterBackend',
    'social_auth.backends.facebook.FacebookBackend',
    'django.contrib.auth.backends.ModelBackend',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.contrib.messages.context_processors.messages",
    "django.core.context_processors.request",
    'plata.context_processors.plata_context',
    'social_auth.context_processors.social_auth_by_type_backends',
    'common.context_processors.social_network_settings',
    'common.context_processors.misc_settings',
    'common.context_processors.account_access',
)

MIDDLEWARE_CLASSES = (
    'customer.middleware.IdecorateMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'debug_toolbar.middleware.DebugToolbarMiddleware',
    'interface.middlewares.InterfaceMiddleware',
)

ROOT_URLCONF = 'Idecorate.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'Idecorate.wsgi.application'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    # "%s%s" % (PROJECT_PATH, "/../templates"),
    os.path.join(SITE_ROOT, 'templates'),
    os.path.join(SITE_ROOT, 'styleboard/templates'),
    os.path.join(SITE_ROOT, 'interface/templates'),
    os.path.join(SITE_ROOT, 'sites/templates'),
)

INSTALLED_APPS = (
    'django.contrib.humanize',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.flatpages',
    'admin',
    'interface',
    'category',
    'menu',
    'debug_toolbar',
    'stdimage',
    'widget_tweaks',
    'cart',
    'plata',
    'plata.contact',
    'plata.discount',
    'plata.payment',
    'plata.product',
    'plata.shop',
    'bootstrap-pagination',
    'idecorate_settings',
    'customer',
    'social_auth',
    'embellishments',
    'common',
    'paypal',
    'styleboard'
    # Uncomment the next line to enable the admin:
    # 'django.contrib.admin',
    # Uncomment the next line to enable admin documentation:
    # 'django.contrib.admindocs',
)

SESSION_EXPIRE_AT_BROWSER_CLOSE = True

SOCIAL_AUTH_ENABLED_BACKENDS = ('twitter', 'facebook',)  
SOCIAL_AUTH_CREATE_USERS          = True
SOCIAL_AUTH_FORCE_RANDOM_USERNAME = False
SOCIAL_AUTH_DEFAULT_USERNAME      = 'socialauth_user'
SOCIAL_AUTH_COMPLETE_URL_NAME     = 'socialauth_complete'
#SOCIAL_AUTH_USER_MODEL           = 'app.CustomUser'
SOCIAL_AUTH_ERROR_KEY             = 'socialauth_error'
SOCIAL_AUTH_FORCE_POST_DISCONNECT = True
SOCIAL_AUTH_SESSION_EXPIRATION = False

TWITTER_CONSUMER_KEY = 'prOK4KmIyYRlSLbSgnb8Q'
TWITTER_CONSUMER_SECRET = 'duHZCipNTNZd6oU9KeP5sOi2BImJjjaymmDy1jtKpo'


FACEBOOK_APP_ID = '250262231769530'
FACEBOOK_API_SECRET = '95a3252b750cb86fb27e5df6e575eb6b'

#STAGING SETTINGS
#FACEBOOK_APP_ID = '267814813348756'
#FACEBOOK_API_SECRET = '70a26a68da9c86ef7faeb0de14bfc3ef'

FACEBOOK_EXTENDED_PERMISSIONS = ['email','read_friendlists', 'publish_stream']
FACEBOOK_PROFILE_EXTRA_PARAMS = {'locale': 'ru_RU'}

FACEBOOK_INVITE_FRIENDS_PER_PAGE = 15


#LOGIN_URL          = '/login-form/'
LOGIN_REDIRECT_URL = '/social_redirect/'
LOGIN_ERROR_URL    = '/login/error/'

SOCIAL_AUTH_PIPELINE = (
    #'social_auth.backends.pipeline.misc.save_status_to_session',
    #'social_auth.backends.pipeline.social.social_auth_user',
    #'social_auth.backends.pipeline.associate.associate_by_email',
    
    #'social_auth.backends.pipeline.user.create_user',
    #'social_auth.backends.pipeline.social.associate_user',
    #'social_auth.backends.pipeline.social.load_extra_data',
    #'social_auth.backends.pipeline.user.update_user_details',
    
    'social_auth.backends.pipeline.social.social_auth_user',
    
    #'social_auth.backends.pipeline.associate.associate_by_email',
    #'customer.pipeline.social_auth_user',
    'customer.pipeline.associate_by_username',
    'social_auth.backends.pipeline.user.get_username',
    'social_auth.backends.pipeline.user.create_user',
    'social_auth.backends.pipeline.social.associate_user',
    #'social_auth.backends.pipeline.user.update_user_details',
    'social_auth.backends.pipeline.social.load_extra_data',
    'customer.pipeline.get_user_avatar',
)


# Add to your settings file
CONTENT_TYPES = ['image']
FONT_TYPES = ['font/ttf', 'font/truetype','application/x-font-ttf','application/octet-stream']
ALLOWED_CATEGORY_IMAGES = ['png','gif','jpeg','jpg','pjpeg']
ALLOWED_UPLOAD_EMBELLISHMENT_IMAGES = ['png','gif','jpeg','jpg','pjpeg','tiff','tif']
# 1MB - 1048576
# 2MB - 2097152
# 2.5MB - 2621440
# 5MB - 5242880
# 10MB - 10485760
# 20MB - 20971520n
# 50MB - 5242880
# 100MB 104857600
# 250MB - 214958080
# 500MB - 429916160
MAX_UPLOAD_CATEGORY_IMAGE_SIZE = 2097152
MAX_UPLOAD_PRODUCT_IMAGE_SIZE = 10485760
MAX_UPLOAD_EMBELLISHMENT_IMAGE_SIZE = 2097152
MAX_UPLOAD_FONT_SIZE = 1048576
MAX_UPLOAD_PROFILE_PIC = 1048576

CATEGORY_THUMBNAIL_WIDTH = 100
CATEGORY_THUMBNAIL_HEIGHT = 100

PRODUCT_THUMBNAIL_WIDTH = 100
PRODUCT_THUMBNAIL_HEIGHT = 100
PRODUCT_WIDTH = 400
PRODUCT_HEIGHT = 400

EMBELLISHMENT_THUMBNAIL_WIDTH = 100
EMBELLISHMENT_THUMBNAIL_HEIGHT = 100
EMBELLISHMENT_MAX_WIDTH_HEIGHT = 1024

HOME_BANNER_WHOLE_WIDTH = 936
HOME_BANNER_HALF_WIDTH = 450
HOME_BANNER_THIRD_WIDTH = 288
HOME_BANNER_HEIGHT = 285
MAX_BANNER_SIZE = 2621440

HOME_INFO_GRAPHICS_WIDTH = 960
HOME_INFO_GRAPHICS_HEIGHT = 470
HOME_INFO_GRAPHICS_SIZE = 2621440


IDECORATE_HOST = 'idecorateweddings.com:8000'

# paydollar settings
"""
#LIVE SETTINGS
PAYDOLLAR_SS_DIRECT_URL = 'https://www.paydollar.com/b2c2/eng/directPay/payComp.jsp'  # LIVE
PAYDOLLAR_CP_THROUGH_BROWSER_URL = 'https://www.paydollar.com/b2c2/eng/payment/payForm.jsp'  # LIVE
PAYDOLLAR_API_URL = 'https://www.paydollar.com/b2c2/eng/merchant/api/orderApi.jsp'  # LIVE
"""

#TEST SETTINGS
PAYDOLLAR_SS_DIRECT_URL = 'https://test.paydollar.com/b2cDemo/eng/directPay/payComp.jsp'
PAYDOLLAR_CP_THROUGH_BROWSER_URL = 'https://test.paydollar.com/b2cDemo/eng/payment/payForm.jsp'
PAYDOLLAR_API_URL = 'https://test.paydollar.com/b2cDemo/eng/merchant/api/orderApi.jsp'

PAYDOLLAR_API_LOGIN_ID = ''
PAYDOLLAR_API_PASSWORD = ''
PAYDOLLAR_SECURE_HASH_SECRET = 'E1qaoDmP7MBPUXBuCc1IJqlxrwE1UiJt'
PAYDOLLAR_CURRENCY = '840'  # 840(USD), 344(HKD)
PAYDOLLAR_MERCHANT_ID = '88110388'

#Plata Settings
POSTFINANCE = {
    'PSPID': 'plataTEST',
    'SHA1_IN': 'plataSHA1_IN',
    'SHA1_OUT': 'plataSHA1_OUT',
    'LIVE': False,
    }

PAYPAL = {
    'BUSINESS': 'example@paypal.com',
    'LIVE': False,
    }

PLATA_REPORTING_ADDRESSLINE = 'Example Corp. - 3. Example Street - 1234 Example'

PLATA_SHOP_PRODUCT = 'cart.Product'
PLATA_SHOP_CONTACT = 'cart.Contact'
CURRENCIES = ('USD',)
#End of Plata Settings

#Idecorate Paypal Settings
PAYPAL_PDT_TOKEN = '8Ddb2VFSiDE2l4Kzfe3d8d1oLDqX_Ux9oi2GeTFKU4L9hatKExbRMAukwcG'
PAYPAL_EMAIL = 'seller_1358214077_biz@yahoo.com'
PAYPAL_RETURN_URL = 'http://172.29.19.180:8000'

#Sandbox
PAYPAL_URL = 'https://www.sandbox.paypal.com/au/cgi-bin/webscr'
PAYPAL_PDT_URL = 'https://www.sandbox.paypal.com/au/cgi-bin/webscr'
PAYPAL_IPN_URL = 'https://www.sandbox.paypal.com/au/cgi-bin/webscr'
#End of Idecorate Paypal Settings

#Other Idecorate Weddings Setup
SKIPPING_MODE = True #Used to skip some code block if True
IDECORATE_MAIL = "noreply@idecorateweddings.com"

IDECORATE_ENABLE_PAYPAL = True
IDECORATE_ENABLE_VISA = True
IDECORATE_ENABLE_MASTERCARD = True
IDECORATE_ENABLE_AMERICAN_EXPRESS = True


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'filters': {
#         'require_debug_false': {
#             '()': 'django.utils.log.RequireDebugFalse'
#         }
#     },
#     'handlers': {
#         'mail_admins': {
#             'level': 'ERROR',
#             'filters': ['require_debug_false'],
#             'class': 'django.utils.log.AdminEmailHandler'
#         }
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['mail_admins'],
#             'level': 'ERROR',
#             'propagate': True,
#         },
#     }
# }

LOGGING = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        }
    },
    'handlers': {
        'debug_log': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), "../logs/debug.log"),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'info_log': {
            'level': 'INFO',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), "../logs/info.log"),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'warning_log': {
            'level': 'WARNING',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), "../logs/warning.log"),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'error_log': {
            'level': 'ERROR',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), "../logs/error.log"),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'critical_log': {
            'level': 'CRITICAL',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), "../logs/critical.log"),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
        'django_request': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.path.join(os.path.dirname(__file__), "../logs/django_request.log"),
            'maxBytes': 1024*1024*5, # 5 MB
            'backupCount': 5,
            'formatter': 'verbose'
        },
    },
    'loggers': {
        '': {
            'handlers': ['debug_log', 'info_log', 'warning_log', 'error_log', 'critical_log'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'django.request': {
            'handlers': ['django_request'],
            'level': 'DEBUG',
            'propagate': True,
        },
    }
}


#INTERNAL_IPS = ('127.0.0.1',)

PRODUCT_HOME_NUM_RECORDS      = 20
STYLEBOARD_HOME_NUM_RECORDS   = 10
INSPIRATION_NUM_RECORDS       = 5
PRODUCT_SITUATION_NUM_RECORDS = 5

#styleboards constants
STYLEBOARD_GET_PRODUCTS_NUM_RECORDS = 15

try:
    from localsettings import *
except:
    pass
