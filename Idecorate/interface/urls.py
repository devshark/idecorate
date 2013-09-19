from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns =  patterns('interface.views',
    url(r'^$', 'home', {}, name='home'),
    url(r'^styleboard/$', 'styleboard', {}, name='styleboard'),
    url(r'^styleboard2/$', 'styleboard2', {}, name='styleboard2'),
    url(r'^styleboard/(?P<cat_id>\d+)$', 'styleboard', {}, name='styleboard_cat'),
    url(r'^styleboard_ajax/$', 'styleboard_ajax', {}, name='styleboard_ajax'),
    url(r'^styleboard_product_ajax/$', 'styleboard_product_ajax', {}, name='styleboard_product_ajax'),    
    url(r'^get_category_tree_ajax/$', 'get_category_tree_ajax', {}, name='get_category_tree_ajax'),
    url(r'^get_product_original_image/$', 'get_product_original_image', {}, name='get_product_original_image'),
    url(r'^styleboard_ajax/product_detail$', 'get_product_details', {}, name='get_product_details'),    
    url(r'^crop/(?P<id>.*)$', 'crop', {}, name='crop'),
    url(r'^crop_view/$', 'crop_view', {}, name='crop_view'),
    url(r'^cropped/$', 'cropped', {}, name='cropped'),
    url(r'^set_product_positions/$', 'set_product_positions', {}, name='set_product_positions'),
    url(r'^search_suggestions/$', 'search_suggestions', {}, name='search_suggestions'),
    url(r'^search_products/$', 'search_products', {}, name='search_products'),
    url(r'^generate_text/$', 'generate_text', {}, name='generate_text'),
    url(r'^generate_embellishment/$', 'generate_embellishment', {}, name='generate_embellishment'),
    url(r'^styleboard/new$', 'new_styleboard', {}, name='new_styleboard'),
    url(r'^styleboard/embellishment_items$', 'get_embellishment_items', {}, name='get_embellishment_items'),
    url(r'^styleboard/get_cart_items$', 'get_personalize_cart_items', {}, name='get_personalize_cart_items'),
    url(r'^set_password_user/(?P<param>[\w\-]+)$', 'set_password_user', {}, name='set_password_user'),    
    url(r'^styleboard/template_details/$', 'get_template_details', {}, name='get_template_details'),
    url(r'^checkout_login/$', 'checkout_login', {}, name='checkout_login'),
    url(r'^invite_friends/$', 'invite_friends', {}, name='invite_friends'),
    url(r'^invite_friends_content/$', 'invite_friends_content', {}, name='invite_friends_content'),
    url(r'^ideas/$', 'ideas', {}, name='ideas'),
    url(r'^save_styleboard_to_session/$', 'save_styleboard_to_session', {}, name='save_styleboard_to_session'),
    url(r'^clear_session_sbid/$', 'clear_session_sbid', {}, name='clear_session_sbid'),
    url(r'^get_user_email/$', 'get_user_email', {}, name='get_user_email'),
    url(r'^instruction_tag/$', 'instruction_tag', {}, name='instruction_tag'),
    url(r'^tag_instruction/$', 'tag_instruction', {}, name='tag_instruction'),
    url(r'^save_template_session/$', 'save_template_session', {}, name='save_template_session'),
    url(r'^set_save_template/$', 'set_save_template', {}, name='set_save_template'),
    url(r'^print_styleboard_view/(?P<is_pdf>\d+)/$', 'print_styleboard_view', {}, name='print_styleboard_view'),
    url(r'^styleboard_email/$', 'styleboard_email', {}, name='styleboard_email'),

    url(r'^load/products/ajax/$', 'load_products_ajax', {}, name='load_products_ajax'),
    url(r'^wishlist/add/$', 'add_wishlist_ajax', {}, name='add_wishlist_ajax'),
    #url(r'^load/wishlist/ajax/$', 'load_wishlist_ajax', {}, name='load_wishlist_ajax'),
    url(r'^newsletter/subscriber/add/$', 'subscribe_newsletter_ajax', {}, name='subscribe_newsletter_ajax'),

    url(r'^send_product_to_styleboard/$', 'send_product_to_styleboard', {}, name='send_product_to_styleboard'),
    url(r'^send_styleboard_to_styleboard/$', 'send_styleboard_to_styleboard', {}, name='send_styleboard_to_styleboard'),
)
