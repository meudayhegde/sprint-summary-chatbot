# ✅ Installation Verification Checklist

Use this checklist to verify your installation is complete and ready to use.

## 📋 Pre-Installation Checks

- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] pip installed (`pip --version`)
- [ ] Have API key from OpenAI, Google, or Anthropic

## 📦 File Structure Check

Verify all files are present:

```bash
ls -la
```

You should see:
- [ ] `app.py` - Main FastAPI application (500+ lines)
- [ ] `agent.py` - LangChain agent (350+ lines)
- [ ] `data_analyzer.py` - Data processing (200+ lines)
- [ ] `chart_generator.py` - Visualizations (250+ lines)
- [ ] `config.py` - Configuration management
- [ ] `requirements.txt` - Python dependencies
- [ ] `.env.example` - Environment template
- [ ] `.gitignore` - Git ignore rules
- [ ] `setup.sh` - Setup script (executable)
- [ ] `start.sh` - Start script (executable)
- [ ] `README.md` - Full documentation
- [ ] `EXAMPLE_QUERIES.md` - Query examples
- [ ] `PROJECT_SUMMARY.md` - Technical overview
- [ ] `QUICK_REFERENCE.md` - Quick reference
- [ ] `sprint_synthetic_data(Tickets).csv` - Data file

## 🚀 Installation Steps

### Step 1: Run Setup
```bash
./setup.sh
```

Expected output:
- ✅ Python version check passes
- ✅ Virtual environment created
- ✅ Dependencies installed
- ✅ .env file created

### Step 2: Configure Environment
```bash
nano .env  # or use your favorite editor
```

Required configuration:
- [ ] Set `LLM_PROVIDER` (openai, gemini, or anthropic)
- [ ] Set corresponding API key
- [ ] (Optional) Adjust model names
- [ ] (Optional) Adjust port if 8000 is in use

### Step 3: Verify Dependencies
```bash
source venv/bin/activate
pip list | grep -E "(fastapi|langchain|pandas|plotly)"
```

You should see:
- [ ] fastapi (0.109.0 or similar)
- [ ] langchain (0.1.6 or similar)
- [ ] pandas (2.2.0 or similar)
- [ ] plotly (5.18.0 or similar)

### Step 4: Test Python Files
```bash
python3 -m py_compile app.py agent.py data_analyzer.py chart_generator.py config.py
echo "Exit code: $?"
```

Expected:
- [ ] Exit code: 0 (no syntax errors)

## 🧪 Post-Installation Tests

### Test 1: Start Application
```bash
./start.sh
```

Expected output:
- [ ] No error messages
- [ ] Message: "Loading data from..."
- [ ] Message: "Successfully loaded X records"
- [ ] Message: "Initializing LangChain agent..."
- [ ] Message: "Application startup complete"
- [ ] Server running on http://0.0.0.0:8000

### Test 2: Health Check
Open new terminal:
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "llm_provider": "openai",
  "data_loaded": true,
  "total_tickets": 40
}
```

- [ ] Status is "healthy"
- [ ] data_loaded is true
- [ ] total_tickets is 40

### Test 3: Web Interface
Open browser:
```
http://localhost:8000
```

You should see:
- [ ] Beautiful gradient background (purple)
- [ ] Chat interface with header
- [ ] Welcome message
- [ ] 4 suggestion chips
- [ ] Input box at bottom
- [ ] Send button

### Test 4: Basic Chat
In the web interface, type:
```
Show me overall sprint summary
```

Expected:
- [ ] Message appears in chat
- [ ] Typing indicator shows
- [ ] Bot responds with summary
- [ ] Response includes data (total tickets, sprints, etc.)

### Test 5: Chart Generation
In the web interface, type:
```
Create a velocity chart
```

Expected:
- [ ] Bot responds with confirmation
- [ ] Interactive Plotly chart appears below message
- [ ] Chart shows sprint data with bars
- [ ] Chart is interactive (hover, zoom, pan)

### Test 6: API Endpoint
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "How many tickets are done?"}'
```

Expected:
- [ ] Returns JSON response
- [ ] Contains "response" field with answer
- [ ] Contains "charts" field (may be empty array)

### Test 7: Data Summary Endpoint
```bash
curl http://localhost:8000/api/summary | python3 -m json.tool
```

Expected:
- [ ] Returns formatted JSON
- [ ] Contains total_tickets: 40
- [ ] Contains list of sprints
- [ ] Contains status_distribution
- [ ] Contains ticket_types

## 🔍 Troubleshooting

### Issue: "Module not found" errors
**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "API key not configured"
**Solution:**
- Check `.env` file exists
- Verify API key is correct (no quotes, spaces)
- Ensure LLM_PROVIDER matches the key you provided

### Issue: Port 8000 already in use
**Solution:**
```bash
# Edit .env
APP_PORT=8001
# Restart application
```

### Issue: Data file not found
**Solution:**
```bash
# Verify file exists
ls -la sprint_synthetic_data\(Tickets\).csv
# If missing, check original location
```

### Issue: Charts not rendering
**Solution:**
- Check browser console for errors
- Verify Plotly CDN is accessible
- Try requesting chart explicitly: "Create a status chart"

### Issue: Slow responses
**Solution:**
- Check API key has quota/credits
- Try faster model (gpt-3.5-turbo)
- Check network connection

## ✅ Final Verification

All checks should pass:

### Application Checks
- [ ] Application starts without errors
- [ ] Health check returns healthy
- [ ] Web interface loads
- [ ] Can send messages
- [ ] Bot responds with data
- [ ] Charts generate correctly

### API Checks
- [ ] POST /chat works
- [ ] GET /health works
- [ ] GET /api/summary works
- [ ] API docs accessible at /docs

### Feature Checks
- [ ] Natural language queries work
- [ ] Suggestion chips clickable
- [ ] Charts are interactive
- [ ] Multiple questions in sequence work
- [ ] Different query types work (bugs, team, sprints)

## 🎉 Success Criteria

Your installation is successful if:

1. ✅ Application starts without errors
2. ✅ Web interface is accessible and beautiful
3. ✅ Can ask questions and get answers
4. ✅ Charts generate and display
5. ✅ API endpoints respond correctly
6. ✅ No error messages in console

## 📚 Next Steps

Once verified:
1. Read `EXAMPLE_QUERIES.md` for question ideas
2. Explore different types of analysis
3. Try switching LLM providers
4. Customize the data (add your own CSV)
5. Extend with new features

## 🆘 Getting Help

If verification fails:
1. Check console logs for errors
2. Review `.env` configuration
3. Verify all dependencies installed
4. Check Python version (3.9+)
5. Review error messages carefully
6. Check API key is valid and has quota

## 📝 Notes

- First startup may take longer (loading model)
- Some queries may take 5-10 seconds (normal)
- Charts require browser with JavaScript enabled
- API rate limits apply based on your provider

---

**If all checks pass, you're ready to go! 🚀**

Happy analyzing! 📊✨
