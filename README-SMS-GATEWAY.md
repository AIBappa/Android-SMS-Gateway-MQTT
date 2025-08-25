# Android SMS Gateway MQTT

This project creates an SMS gateway that receives messages from an Android device and forwards them to a Cloudflare Worker, which stores them in a D1 database.

## Components

1. **Android App**: Sends SMS messages to the Laptop Receiver
2. **Laptop Receiver**: Receives SMS messages and forwards them to Cloudflare
3. **Cloudflare Worker**: Authenticates and processes SMS data, storing it in D1 database

## Setup Instructions

### Laptop Receiver

1. Create a configuration file at `~/sms_gateway_config.json`:
   ```json
   {
     "cf_api_key": "YOUR_API_KEY_HERE",
     "cf_endpoint": "https://your-worker-name.your-account.workers.dev/sms",
     "log_file": "sms_log.txt"
   }
   ```

2. Run the receiver:
   ```bash
   cd Laptop_Reciever
   python3 Laptoprec.py
   ```

### Cloudflare Worker

1. Copy `wrangler.example.toml` to `wrangler.toml` and update with your database information
2. Set up your API key:
   ```bash
   cd cf-worker
   wrangler secret put API_KEY
   # Enter your API key when prompted (same as in sms_gateway_config.json)
   ```
3. Deploy the worker:
   ```bash
   wrangler deploy
   ```

## Security Notes

The following files contain sensitive information and should never be committed to Git:

1. `sms_gateway_config.json` - Contains API key
2. `Laptop_Reciever/sms_log.txt` - Contains actual SMS messages and phone numbers
3. `cf-worker/node_modules/.cache/wrangler/wrangler-account.json` - Contains Cloudflare account ID
4. `cf-worker/node_modules/.mf/cf.json` - Contains location data and Cloudflare metadata
5. `cf-worker/wrangler.toml` - Contains database IDs (use wrangler.example.toml as a template)

These files are already added to `.gitignore` to prevent accidental commits.

## Database Schema

The worker creates the following table in your D1 database:

```sql
CREATE TABLE IF NOT EXISTS sms_messages (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sms_text TEXT NOT NULL,
  sender TEXT NOT NULL,
  received_at TEXT NOT NULL
)
```
