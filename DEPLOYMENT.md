# 🚀 Phone Agent Deployment Guide

Schritt-für-Schritt Anleitung für Coolify Deployment

---

## 📋 Voraussetzungen

- [ ] GitHub Account
- [ ] Coolify Zugang
- [ ] n8n bereits deployed (n8n.theaigency.ch)
- [ ] VAPI Account

---

## 🔧 Schritt 1: GitHub Repository erstellen

```bash
# Lokal im phone-agent-api Ordner:
cd /Users/macbookpro/Desktop/CascadeProjects/windsurf-project/phone-agent-api

# Git initialisieren
git init

# .gitignore prüfen (bereits vorhanden)
cat .gitignore

# Alle Files hinzufügen
git add .

# Commit
git commit -m "Initial commit: Phone Agent API"

# GitHub Repo erstellen (im Browser):
# https://github.com/new
# Name: phone-agent-api
# Private Repository

# Remote hinzufügen
git remote add origin https://github.com/DEIN-USERNAME/phone-agent-api.git

# Push
git branch -M main
git push -u origin main
```

---

## 📦 Schritt 2: n8n Workflow importieren

```bash
# 1. Gehe zu n8n UI: https://n8n.theaigency.ch

# 2. Workflows → Import from File

# 3. Wähle: phone-agent-n8n-workflow.json

# 4. Konfiguriere Config-Node:
#    - google_sheet_id: DEINE_SHEET_ID
#    - hubspot_api_key: DEIN_HUBSPOT_KEY
#    - alert_email: vertrieb@yourcompany.ch

# 5. Verbinde Gmail Credentials

# 6. Aktiviere Workflow

# 7. Kopiere Webhook-URL:
#    https://n8n.theaigency.ch/webhook/vapi-call
```

---

## 🌐 Schritt 3: Coolify Deployment

### 3.1 Neues Resource erstellen

```
1. Gehe zu Coolify
2. Projekt: "Agents-Automations"
3. Environment: "Production"
4. "+ New" → "GitHub Repository"
```

### 3.2 Repository verbinden

```
1. Source: GitHub
2. Repository: phone-agent-api
3. Branch: main
4. Build Pack: Dockerfile
```

### 3.3 Environment Variables setzen

```
N8N_WEBHOOK_URL=https://n8n.theaigency.ch/webhook/vapi-call
ENVIRONMENT=production
```

### 3.4 Domain konfigurieren

```
Domain: phone-agent.theaigency.ch
SSL: Enabled (Let's Encrypt)
```

### 3.5 Deploy!

```
1. Klicke "Deploy"
2. Warte auf Build (2-3 Min)
3. Check Logs
4. Status sollte "running" sein
```

---

## ✅ Schritt 4: Testing

### 4.1 Health Check

```bash
curl https://phone-agent.theaigency.ch/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-30T12:00:00Z",
  "version": "1.0.0",
  "n8n_configured": true
}
```

### 4.2 Test Call Endpoint

```bash
curl -X POST https://phone-agent.theaigency.ch/vapi/call-ended \
  -H "Content-Type: application/json" \
  -d '{
    "call_id": "test_123",
    "call_duration": 120,
    "call_started_at": "2025-10-30T10:00:00Z",
    "call_ended_at": "2025-10-30T10:02:00Z",
    "caller_phone": "+41791234567",
    "caller_name": "Test User",
    "call_transcript": "Test transcript",
    "call_summary": "Test call",
    "company_name": "Test AG",
    "call_purpose": "Test",
    "call_urgency": "medium",
    "should_book_meeting": false,
    "call_sentiment": "neutral"
  }'
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Call data processed successfully",
  "lead_id": "test_123",
  "meeting_booked": false,
  "meeting_url": null
}
```

### 4.3 Check n8n

```
1. Gehe zu n8n UI
2. Executions → Sollte Test-Execution sehen
3. Check Google Sheet → Test-Call sollte da sein
4. Check E-Mail → Alert sollte angekommen sein
```

---

## 🎯 Schritt 5: VAPI Integration

### 5.1 VAPI Dashboard

```
1. Gehe zu: https://vapi.ai/dashboard
2. Assistants → Wähle deinen Assistant
3. Settings → Webhooks
```

### 5.2 Webhook konfigurieren

```
End Call Webhook URL:
https://phone-agent.theaigency.ch/vapi/call-ended

Events: call.ended
```

### 5.3 Test mit echtem Call

```
1. Rufe deine VAPI-Nummer an
2. Führe Test-Gespräch
3. Beende Anruf
4. Check:
   - Phone Agent API Logs (Coolify)
   - n8n Execution
   - Google Sheet
   - E-Mail Alert
```

---

## 📊 Monitoring

### Coolify Logs

```
1. Coolify → Agents-Automations → phone-agent-api
2. Logs Tab
3. Real-time Logs aktivieren
```

### n8n Executions

```
1. n8n UI → Executions
2. Filter: "Phone Agent: VAPI Integration"
3. Check Success/Error Rate
```

---

## 🔧 Troubleshooting

### Problem: Health Check failed

```bash
# Check if service is running
curl https://phone-agent.theaigency.ch/

# Check Coolify logs
# Coolify → phone-agent-api → Logs

# Common issues:
# - Port 8001 not exposed
# - Environment variables missing
# - n8n webhook URL wrong
```

### Problem: n8n webhook not working

```bash
# Check n8n workflow is active
# Check webhook URL is correct
# Test webhook directly:
curl -X POST https://n8n.theaigency.ch/webhook/vapi-call \
  -H "Content-Type: application/json" \
  -d '{"test": "data"}'
```

### Problem: VAPI not sending data

```
# Check VAPI webhook configuration
# Check VAPI logs
# Verify webhook URL is publicly accessible
# Test with curl from external server
```

---

## 🎉 Success Checklist

- [ ] GitHub Repository erstellt & gepusht
- [ ] n8n Workflow importiert & aktiviert
- [ ] Coolify Deployment erfolgreich
- [ ] Health Check OK
- [ ] Test Call erfolgreich
- [ ] n8n Execution erfolgreich
- [ ] Google Sheet Update OK
- [ ] E-Mail Alert erhalten
- [ ] VAPI Webhook konfiguriert
- [ ] Echter Test-Call erfolgreich

---

## 📞 Support

Bei Problemen:
- Email: info@theaigency.ch
- Phone: +41 76 274 62 20

---

## 🚀 Next Steps

Nach erfolgreichem Deployment:

1. **Google Sheet erstellen:**
   - Tab: "Phone Calls"
   - Spalten: call_id, phone, first_name, last_name, organization_name, call_purpose, call_duration, call_transcript, call_summary, received_at, status

2. **Calendly Integration (optional):**
   - Calendly API Key holen
   - n8n Workflow erweitern
   - Automatisches Meeting-Booking

3. **Analytics (optional):**
   - Call-Statistiken
   - Response-Times
   - Conversion-Rates

---

**Viel Erfolg! 🚀**
