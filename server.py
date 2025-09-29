from http.server import HTTPServer, SimpleHTTPRequestHandler
import os

class MyHandler(SimpleHTTPRequestHandler):
    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        SimpleHTTPRequestHandler.end_headers(self)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 3000))
    server_address = ('', port)
    httpd = HTTPServer(server_address, MyHandler)
    print(f'Server running on port {port}...')
    httpd.serve_forever() 