from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import json
import datetime
import os
import sys

# Path to config file (you can move this file wherever you want)
CONFIG_FILE = os.path.expanduser('~/sms_gateway_config.json')

# Load configuration
try:
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    
    # Extract configuration values
    CF_BACKEND_URL = config.get('cf_endpoint', 'https://geoprasidh-backend.jadhavshantanu.workers.dev/sms')
    LOG_FILE = config.get('log_file', 'sms_log.txt')
    API_KEY = config.get('cf_api_key', '')
    
    if not API_KEY:
        print("Warning: API key is not set in the configuration file.")
        
except FileNotFoundError:
    print(f"Error: Configuration file not found at {CONFIG_FILE}")
    print("Please create a config.json file with the following structure:")
    print("""
    {
      "cf_api_key": "YOUR_API_KEY_HERE",
      "cf_endpoint": "https://geoprasidh-backend.jadhavshantanu.workers.dev/sms",
      "log_file": "sms_log.txt"
    }
    """)
    sys.exit(1)
except json.JSONDecodeError:
    print(f"Error: Configuration file at {CONFIG_FILE} is not valid JSON")
    sys.exit(1)

class SMSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        sms_data = self.rfile.read(content_length)
        sms_str = sms_data.decode('utf-8')
        print("Received SMS:", sms_str)
        
        # Save to file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(f"[{datetime.datetime.now()}] {sms_str}\n")
        
        # Try to parse the SMS data
        try:
            # Assuming SMS data is in JSON format; if not, we need to transform it
            if not sms_str.strip().startswith('{'):
                # Basic parsing if not in JSON format
                # This is a simple example - adjust based on your actual SMS format
                sender, message = sms_str.split(':', 1) if ':' in sms_str else ('Unknown', sms_str)
                sms_data = {
                    'sender': sender.strip(),
                    'message': message.strip(),
                    'timestamp': datetime.datetime.now().isoformat()
                }
            else:
                sms_data = json.loads(sms_str)
            
            # Try forwarding to CF backend
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {API_KEY}'  # Add API key for authentication
            }
            r = requests.post(CF_BACKEND_URL, json=sms_data, headers=headers, timeout=5)
            print(f'Forwarded to CF backend, status: {r.status_code}, response: {r.text[:100]}')
        except json.JSONDecodeError:
            print('[Error] Could not parse SMS as JSON:', sms_str)
        except requests.RequestException as e:
            print('[Warning] Could not forward to CF backend:', str(e))
        except Exception as e:
            print('[Error] Unexpected error:', str(e))

        self.send_response(200)
        self.end_headers()

if __name__ == '__main__':
    server_address = ('', 8080)
    httpd = HTTPServer(server_address, SMSHandler)
    print('SMS receiver started. Listening on port 8080...')
    print(f'Will forward SMS data to: {CF_BACKEND_URL}')
    print(f'Logs will be saved to: {LOG_FILE}')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print('Server stopped by user.')