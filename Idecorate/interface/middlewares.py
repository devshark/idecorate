from cart.services import generate_unique_id
from customer.models import WishList

class InterfaceMiddleware(object):
    def process_request(self, request):
        sessionid = request.session.get('sessionid', False)
        if not sessionid:
            sessionid = generate_unique_id()
        request.session['sessionid'] = sessionid
        
        if not request.user.is_authenticated():
            wishlist_session_id = request.session.get('wishlist_session_id', False)
            if not wishlist_session_id:
                request.session['wishlist_session_id'] = sessionid

