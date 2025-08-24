from http.server import BaseHTTPRequestHandler, HTTPServer
import requests

CF_BACKEND_URL = 'https://your-cf-tunnel.example/path'  # <<<< EDIT this to your actual CF backend URL
LOG_FILE = 'sms_log.txt'

class SMSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        sms_data = self.rfile.read(content_length)
        sms_str = sms_data.decode('utf-8')
        print("Received SMS:", sms_str)
        
        # Save to file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(sms_str + '\n')
        
        # Try forwarding to CF backend
        try:
            r = requests.post(CF_BACKEND_URL, data=sms_str, timeout=5)
            print(f'Forwarded to CF backend, status: {r.status_code}')
        except requests.RequestException as e:
            print('[Warning] Could not forward to CF backend (tunnel may be down):', str(e))

        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SMSHandler)
    print('Listening on port 8080...')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Server stopped by user.')