# 📞 Phone Agent API v2.0

**ElevenLabs Conversational AI + Qdrant Knowledge Base + Direct CRM Integration**

---

## 🎯 Overview

Phone Agent API v2.0 is a complete rewrite featuring:

- ✅ **ElevenLabs Conversational AI** - Best-in-class voice quality & lowest latency
- ✅ **Qdrant Vector Database** - Company knowledge base for intelligent responses
- ✅ **Redis Session Management** - Real-time conversation context
- ✅ **OpenAI GPT-4o** - Conversation logic & information extraction
- ✅ **Direct CRM Integration** - HubSpot + Google Sheets (no n8n needed!)
- ✅ **Automatic Call Processing** - Summary, sentiment, urgency analysis

---

## 🏗️ Architecture

```
Phone Call
↓
ElevenLabs Conversational AI (Voice)
↓
Phone Agent API (FastAPI)
├── Qdrant (Company Knowledge)
├── Redis (Session/Context)
├── OpenAI GPT-4o (AI Logic)
├── HubSpot CRM (Direct)
└── Google Sheets (Direct)
```

---

## 🚀 Features

### 1. **Intelligent Conversations**
- Real-time voice AI with ElevenLabs
- Context-aware responses using Qdrant knowledge base
- Swiss German support (Sie-Form)
- Natural, human-like conversations

### 2. **Company Knowledge Base**
- Store company information in Qdrant
- Automatic semantic search during calls
- Categories: products, services, pricing, FAQ
- Easy management via API

### 3. **Automatic Call Processing**
- Extract caller information (name, company, email)
- Identify call purpose & urgency
- Sentiment analysis (positive/neutral/negative)
- Generate call summary
- Full transcript

### 4. **CRM Integration**
- **HubSpot:** Auto-create contacts, notes, tasks
- **Google Sheets:** Store all call data
- No manual data entry required

### 5. **Session Management**
- Redis-based real-time context
- Conversation history tracking
- Fast retrieval & updates

---

## 📋 API Endpoints

### **Calls**

#### `POST /calls/start`
Start new phone call
```bash
curl -X POST "https://phone-agent.theaigency.ch/calls/start?caller_phone=+41791234567"
```

#### `POST /calls/{call_id}/message`
Process user message during call
```bash
curl -X POST "https://phone-agent.theaigency.ch/calls/call_123/message?message=Ich möchte einen Termin"
```

#### `POST /calls/{call_id}/end`
End call and process data
```bash
curl -X POST "https://phone-agent.theaigency.ch/calls/call_123/end"
```

### **Knowledge Base**

#### `POST /calls/knowledge`
Add company knowledge
```bash
curl -X POST "https://phone-agent.theaigency.ch/calls/knowledge" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Unsere Produkte",
    "content": "Wir bieten AI-powered CRM Automation...",
    "category": "products",
    "tags": ["crm", "automation"]
  }'
```

#### `GET /calls/knowledge`
Get all knowledge entries
```bash
curl "https://phone-agent.theaigency.ch/calls/knowledge"
```

#### `DELETE /calls/knowledge/{entry_id}`
Delete knowledge entry
```bash
curl -X DELETE "https://phone-agent.theaigency.ch/calls/knowledge/entry_123"
```

### **Health**

#### `GET /health`
Health check
```bash
curl "https://phone-agent.theaigency.ch/health"
```

---

## ⚙️ Configuration

### Environment Variables

See `.env.example` for all variables.

**Required:**
- `ELEVENLABS_API_KEY` - ElevenLabs API key
- `ELEVENLABS_AGENT_ID` - Your agent ID
- `OPENAI_API_KEY` - OpenAI API key
- `QDRANT_URL` - Qdrant database URL
- `REDIS_URL` - Redis URL

**Optional:**
- `HUBSPOT_API_KEY` - For CRM integration
- `GOOGLE_SHEET_ID` - For Sheets integration
- `GOOGLE_SERVICE_ACCOUNT_FILE` - Service account JSON

---

## 🚀 Deployment

### Coolify

1. Push to GitHub
2. Coolify → New Resource → GitHub Repository
3. Select `phone-agent-api`
4. Set environment variables
5. Domain: `phone-agent.theaigency.ch`
6. Deploy!

### Docker Compose

```yaml
version: '3.8'

services:
  phone-agent-api:
    build: .
    ports:
      - "8001:8001"
    environment:
      - ELEVENLABS_API_KEY=${ELEVENLABS_API_KEY}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - QDRANT_URL=http://qdrant-agents:6333
      - REDIS_URL=redis://redis-agents:6379
    depends_on:
      - qdrant-agents
      - redis-agents
  
  qdrant-agents:
    image: qdrant/qdrant:latest
    ports:
      - "6333:6333"
    volumes:
      - qdrant_data:/qdrant/storage
  
  redis-agents:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

volumes:
  qdrant_data:
  redis_data:
```

---

## 📊 Knowledge Base Setup

### 1. Add Company Information

```python
import httpx

knowledge_entries = [
    {
        "title": "Unsere Produkte",
        "content": "Wir bieten AI-powered CRM Automation, Sales Agent API, Smart Inbox...",
        "category": "products",
        "tags": ["products", "services"]
    },
    {
        "title": "Preise",
        "content": "Starter: CHF 99/Monat, Professional: CHF 299/Monat, Enterprise: Custom",
        "category": "pricing",
        "tags": ["pricing", "plans"]
    },
    {
        "title": "Kontakt",
        "content": "Email: info@theaigency.ch, Phone: +41 76 274 62 20",
        "category": "contact",
        "tags": ["contact", "support"]
    }
]

for entry in knowledge_entries:
    response = httpx.post(
        "https://phone-agent.theaigency.ch/calls/knowledge",
        json=entry
    )
    print(response.json())
```

### 2. Categories

- `products` - Product information
- `services` - Service descriptions
- `pricing` - Pricing & plans
- `faq` - Frequently asked questions
- `contact` - Contact information
- `general` - General company info

---

## 🧪 Testing

### 1. Health Check
```bash
curl https://phone-agent.theaigency.ch/health
```

### 2. Start Test Call
```bash
curl -X POST "https://phone-agent.theaigency.ch/calls/start?caller_phone=+41791234567"
```

### 3. Send Test Message
```bash
curl -X POST "https://phone-agent.theaigency.ch/calls/call_123/message?message=Was sind eure Produkte?"
```

### 4. End Call
```bash
curl -X POST "https://phone-agent.theaigency.ch/calls/call_123/end"
```

---

## 📝 Call Data Flow

1. **Call Starts** → ElevenLabs creates session
2. **User Speaks** → Transcript sent to API
3. **API Processes:**
   - Search Qdrant for relevant knowledge
   - Generate AI response with OpenAI
   - Store in Redis session
4. **AI Responds** → ElevenLabs speaks response
5. **Call Ends:**
   - Extract call information
   - Generate summary
   - Save to HubSpot
   - Save to Google Sheets

---

## 🔧 Development

### Local Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Copy env file
cp .env.example .env

# Edit .env with your keys
nano .env

# Run locally
uvicorn app.main:app --reload --port 8001
```

### Project Structure

```
phone-agent-api/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models.py
│   ├── main.py
│   ├── services/
│   │   ├── elevenlabs_service.py
│   │   ├── openai_service.py
│   │   ├── qdrant_service.py
│   │   ├── redis_service.py
│   │   ├── hubspot_service.py
│   │   ├── sheets_service.py
│   │   └── call_handler.py
│   └── routes/
│       └── calls.py
├── requirements.txt
├── Dockerfile
├── .env.example
└── README.md
```

---

## 📞 Support

For issues or questions:
- Email: info@theaigency.ch
- Phone: +41 76 274 62 20

---

## 📄 License

© 2025 the aigency - All Rights Reserved
