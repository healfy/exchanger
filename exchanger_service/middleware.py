class HeadersMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        response['Content-Security-Policy'] = "frame-ancestors 'none'"
        response['X-Frame-Options'] = 'DENY'
        response['X-Content-Type-Options'] ='nosniff'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = ''
        response['Feature-Policy'] = ''
        if 'Cache-Control' not in response:
            response['Cache-Control'] = 'max-age=0 no-cache s-maxage=0'
        return response
