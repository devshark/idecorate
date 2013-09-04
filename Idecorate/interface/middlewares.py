from cart.services import generate_unique_id

class InterfaceMiddleware(object):
    def process_request(self, request):
        sessionid = request.session.get('sessionid', False)
        if not sessionid:
            sessionid = generate_unique_id()
        request.session['sessionid'] = sessionid
