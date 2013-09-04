from cart.services import generate_unique_id
from customer.models import WishList

class InterfaceMiddleware(object):
    def process_request(self, request):
        sessionid = request.session.get('sessionid', False)
        if not sessionid:
            sessionid = generate_unique_id()

        # get wishlist added before logging in
        # add this to customer login
        """
        wishlist_session = request.session.get('wishlist_session', False)
        if wishlist_session:            
            if request.user.is_authenticated():
                wishlists = WishList.objects.filter(sessionid=wishlist_session)
                for wishlist in wishlists:
                    wishlist.user = request.user
                    wishlist.save()
                    del request.session['wishlist_session']
        """

        request.session['sessionid'] = sessionid
