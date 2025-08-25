// Cloudflare Worker script for handling SMS data and storing in D1
// Add this to your Cloudflare Workers dashboard

export default {
  async fetch(request, env) {
    // Handle CORS for dev environments
    if (request.method === "OPTIONS") {
      return handleCORS();
    }

    // Only allow POST requests to /sms endpoint
    if (request.method === "POST" && new URL(request.url).pathname === "/sms") {
      try {
        // Check for API key authentication
        const authHeader = request.headers.get('Authorization') || '';
        const apiKey = authHeader.startsWith('Bearer ') ? authHeader.substring(7) : '';
        
        // You should store your API key in a Cloudflare Worker secret
        // This is accessed via env.API_KEY
        if (!apiKey || apiKey !== env.API_KEY) {
          return new Response(JSON.stringify({ error: "Unauthorized" }), {
            status: 401,
            headers: corsHeaders
          });
        }
        
        // Parse the SMS data
        const smsData = await request.json();
        
        // Required fields
        if (!smsData.sender || !smsData.message) {
          return new Response(JSON.stringify({ error: "Missing required fields" }), {
            status: 400,
            headers: corsHeaders
          });
        }
        
        // Add timestamp if not provided
        if (!smsData.timestamp) {
          smsData.timestamp = new Date().toISOString();
        }
        
        // Insert into D1 database as TEXT
        // First, create the table if it doesn't exist
        try {
          await env.DB.prepare(`
            CREATE TABLE IF NOT EXISTS sms_messages (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              sms_text TEXT NOT NULL,
              sender TEXT NOT NULL,
              received_at TEXT NOT NULL
            )
          `).run();
        } catch (e) {
          console.error("Error creating table:", e);
        }
        
        // Prepare SMS text - combine all data into one TEXT field
        const smsText = JSON.stringify(smsData);
        
        // Insert the SMS as a text record
        const result = await env.DB.prepare(
          "INSERT INTO sms_messages (sms_text, sender, received_at) VALUES (?, ?, ?)"
        )
        .bind(smsText, smsData.sender, smsData.timestamp)
        .run();
        
        return new Response(JSON.stringify({ 
          success: true, 
          smsId: result.meta?.last_row_id || null,
          message: "SMS stored successfully in geoprasidh-db database"
        }), {
          status: 200,
          headers: corsHeaders
        });
      } catch (err) {
        return new Response(JSON.stringify({ error: err.message }), {
          status: 500,
          headers: corsHeaders
        });
      }
    }
    
    // Default response for other routes
    return new Response("Not found", { status: 404, headers: corsHeaders });
  }
};

// CORS headers for cross-origin requests
const corsHeaders = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type",
  "Content-Type": "application/json"
};

function handleCORS() {
  return new Response(null, {
    status: 204,
    headers: corsHeaders
  });
}
