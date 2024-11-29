import http.server
from functools import wraps
import json
import re
import cgi

# A dictionary to hold routes and their associated handlers
route_registry = []

# Decorator for registering routes
def route(path_pattern, method="GET"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        
        # Define a function to replace the patterns
        def replacer(match):
            var_type, var_name = match.groups()
            if var_type == 'int':
                return r'(?P<{}>\d+)'.format(var_name)
            elif var_type == 'string':
                return r'(?P<{}>[^/]+)'.format(var_name)
            else:
                # Default to matching any non-slash characters
                return r'(?P<{}>[^/]+)'.format(var_name)
        
        # Use re.sub with a function to handle replacements
        pattern_re = re.compile(r'<(int|string):(\w+)>')
        regex_pattern = '^' + pattern_re.sub(replacer, path_pattern) + '$'
        pattern = re.compile(regex_pattern)
        route_registry.append((pattern, method, func))
        return wrapper
    return decorator

# Custom HTTP handler to process requests based on the route registry
class CustomHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def _handle_response(self, response):
        """Helper function to handle responses."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

        # Handle dictionary response (send as JSON)
        if not isinstance(response[0], str):
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response[0])

        else:
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response[0].encode('utf-8'))
            

    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


    def do_OPTIONS(self):
        self.send_response(200, "OK")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()


    def do_GET(self):
        handler = None
        params = {}
        for pattern, method, func in route_registry:
            if method == "GET":
                match = pattern.match(self.path)
                if match:
                    handler = func
                    params = match.groupdict()
                    break
        if handler:
            self.send_response(200)
            response = handler(**params)
            self._handle_response(response)
        else:
            print("Handler Missing!")
            self.send_error(404, "Not Found")

    def do_POST(self):
        handler = None
        params = {}

        # Find the matching handler based on the registered routes
        for pattern, method, func in route_registry:
            if method == "POST":
                match = pattern.match(self.path)
                if match:
                    handler = func
                    params = match.groupdict()
                    break

        if handler:
            print("Handler Found")
            content_type = self.headers.get('Content-Type', '')
            # Handle CORS preflight requests
            if self.headers.get('Origin'):
                self.send_response(200)
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                self.end_headers()
                if self.command == 'OPTIONS':
                    return

            # Check if the content type is multipart/form-data for file uploads
            if 'multipart/form-data' in content_type:
                print("File Upload Detected")
                form = cgi.FieldStorage(
                    fp=self.rfile,
                    headers=self.headers,
                    environ={
                        'REQUEST_METHOD': 'POST',
                        'CONTENT_TYPE': content_type,
                    }
                )
                try:
                    #print("Form: ", form)
                    print("Handler: ", handler)
                    response = handler(form=form, **params)
                except Exception as e:
                    self.send_error(500, f"Error processing form data: {e}")
                    return
            else:
                # Read the request body
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length) if content_length > 0 else None
                try:
                    response = handler(post_data=post_data, **params)
                except Exception as e:
                    self.send_error(500, f"Error processing POST data: {e}")
                    return

            # Handle the response from the handler
            if isinstance(response, tuple):
                # Unpack the response tuple
                content, status_code, *rest = response
                mime_type = rest[0] if rest else 'application/json'
            else:
                content = response
                status_code = 200
                mime_type = 'application/json'

            self.send_response(status_code)
            self.send_header('Content-Type', mime_type)
            self.send_header('Access-Control-Allow-Origin', '*')  # Allow CORS
            self.end_headers()

            if content:
                if isinstance(content, str):
                    self.wfile.write(content.encode('utf-8'))
                elif isinstance(content, bytes):
                    self.wfile.write(content)
                else:
                    # If content is a dictionary or list, serialize it to JSON
                    self.wfile.write(json.dumps(content).encode('utf-8'))
        else:
            self.send_error(404, "Not Found")

