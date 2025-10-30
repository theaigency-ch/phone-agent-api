# 📞 Phone Agent API

VAPI to n8n Integration for Phone Agent

## 🎯 Purpose

This API acts as a bridge between VAPI (Voice AI) and n8n workflows:

1. **VAPI** handles phone calls and conversations
2. **Phone Agent API** receives call data from VAPI
3. **n8n** processes the data (CRM updates, meeting booking, etc.)

---

## 🏗️ Architecture

```
Phone Call → VAPI (Voice AI) → Phone Agent API → n8n Workflows
                                       ↓
                                 Google Sheets
                                 HubSpot CRM
                                 Calendly
                                 Gmail
```

---

## 🚀 Deployment

### Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Edit .env with your settings
nano .env

# Run locally
uvicorn app.main:app --reload --port 8001
```

### Coolify Deployment

1. Push code to GitHub
2. In Coolify: New Resource → GitHub Repository
3. Select repository: `phone-agent-api`
4. Set environment variables:
   - `N8N_WEBHOOK_URL=https://n8n.theaigency.ch/webhook/vapi-call`
5. Domain: `phone-agent.theaigency.ch`
6. Deploy!

---

## 📋 API Endpoints

### `GET /`
Root endpoint - API info

### `GET /health`
Health check - returns API and n8n status

### `POST /vapi/call-ended`
Main endpoint - receives VAPI call data after call ends

**Request Body:**
```json
{
  "call_id": "call_abc123",
  "call_duration": 180,
  "caller_phone": "+41791234567",
  "caller_name": "Max Muster",
  "call_transcript": "Full transcript...",
  "call_summary": "AI summary...",
  "company_name": "TechStartup AG",
  "call_purpose": "Demo-Termin",
  "should_book_meeting": true,
  "preferred_time": "Montag 10-12 Uhr"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Call data processed",
  "lead_id": "lead_123",
  "meeting_booked": true,
  "meeting_url": "https://calendly.com/..."
}
```

### `POST /vapi/function-call`
Function calls during conversation (optional)

---

## ⚙️ Configuration

### Environment Variables

```bash
# n8n Webhook URL (required)
N8N_WEBHOOK_URL=https://n8n.theaigency.ch/webhook/vapi-call

# VAPI API Key (optional - for calling VAPI back)
VAPI_API_KEY=your-vapi-api-key

# Environment
ENVIRONMENT=production
```

---

## 🔗 VAPI Configuration

In VAPI Dashboard, configure webhook:

```
End Call Webhook: https://phone-agent.theaigency.ch/vapi/call-ended
```

---

## 📊 n8n Workflow

The n8n workflow should:

1. Receive webhook from Phone Agent API
2. Parse call data
3. Save to Google Sheets
4. Create/Update HubSpot contact
5. Book Calendly meeting (if requested)
6. Send email notification
7. Return response

---

## 🧪 Testing

```bash
# Health check
curl https://phone-agent.theaigency.ch/health

# Test call endpoint
curl -X POST https://phone-agent.theaigency.ch/vapi/call-ended \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test_123",
    "call_duration": 60,
    "caller_phone": "+41791234567",
    "caller_name": "Test User",
    "call_transcript": "Test transcript",
    "call_purpose": "Test",
    "should_book_meeting": false
  }'
```

---

## 📝 Logs

Logs are available in Coolify:
- Application logs
- Error logs
- Request logs

---

## 🔧 Troubleshooting

### n8n webhook not working
- Check `N8N_WEBHOOK_URL` is correct
- Verify n8n workflow is active
- Check n8n logs

### VAPI not sending data
- Verify webhook URL in VAPI dashboard
- Check VAPI logs
- Test with curl

---

## 📞 Support

For issues or questions:
- Email: info@theaigency.ch
- Phone: +41 76 274 62 20

---

## 📄 License

© 2025 the aigency - All Rights Reserved
