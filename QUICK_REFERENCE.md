# Quick Reference Card 🚀

## Setup (First Time Only)

```bash
./setup.sh                    # Automated setup
# Edit .env and add your API key
```

## Running the Application

```bash
./start.sh                    # Quick start
# OR
python app.py                 # Direct start
```

## Access Points

- **Web UI**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## Configuration (.env)

```env
LLM_PROVIDER=openai          # Options: openai, gemini, anthropic
OPENAI_API_KEY=sk-...        # Your API key
OPENAI_MODEL=gpt-4-turbo-preview
```

## Quick API Examples

### Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Show sprint summary"}'
```

### Get Summary
```bash
curl http://localhost:8000/api/summary
```

### Health Check
```bash
curl http://localhost:8000/health
```

## Common Questions

**Q: How do I switch LLM providers?**
A: Edit `.env` and change `LLM_PROVIDER` to `openai`, `gemini`, or `anthropic`, then restart.

**Q: Charts not showing?**
A: Ask for visualization explicitly: "Create a velocity chart" or "Show me a pie chart of status"

**Q: Getting API errors?**
A: Check your API key in `.env` is correct and has credits/quota available.

**Q: Want to use GPT-4?**
A: Set `OPENAI_MODEL=gpt-4` in `.env` (requires GPT-4 access)

**Q: How to add new data?**
A: Replace `sprint_synthetic_data(Tickets).csv` with your CSV (keep same format)

## Example Questions

Try these in the chat:

```
"Show me overall sprint summary"
"How is the team performing?"
"Create a velocity chart"
"Show me bug analysis"
"What high priority tickets are in progress?"
"Who has completed the most story points?"
```

See EXAMPLE_QUERIES.md for 100+ more examples!

## Project Structure

```
app.py              # Main application
agent.py            # LangChain AI agent
data_analyzer.py    # Data processing
chart_generator.py  # Visualizations
config.py           # Configuration
requirements.txt    # Dependencies
.env               # Your secrets (don't commit!)
```

## Troubleshooting

**Problem**: Module not found
```bash
pip install -r requirements.txt
```

**Problem**: Port 8000 already in use
```bash
# Edit .env and change APP_PORT=8001
```

**Problem**: Permission denied on scripts
```bash
chmod +x setup.sh start.sh
```

**Problem**: Data file not found
```bash
# Ensure sprint_synthetic_data(Tickets).csv is in project root
```

## Development

**Check errors in real-time**:
```bash
tail -f app.log  # If you add file logging
```

**Run with auto-reload**:
```bash
uvicorn app:app --reload
```

**Test API with curl**:
```bash
# See examples above
```

**View interactive API docs**:
- Visit http://localhost:8000/docs (Swagger UI)
- Visit http://localhost:8000/redoc (ReDoc)

## Key Files to Edit

- `.env` - Configuration and API keys
- `app.py` - Add new endpoints
- `agent.py` - Add new analysis tools
- `data_analyzer.py` - Add new data operations
- `chart_generator.py` - Add new chart types

## Tips

1. **Start Simple**: Try basic questions first
2. **Be Specific**: Use exact sprint IDs (SPR-001)
3. **Request Charts**: Ask for visualizations explicitly
4. **Follow Up**: Ask follow-up questions for deeper analysis
5. **Check Logs**: Console shows what the agent is doing
6. **Read Docs**: README.md and EXAMPLE_QUERIES.md have tons of info

## Support

- Check README.md for full documentation
- See EXAMPLE_QUERIES.md for question ideas
- Read PROJECT_SUMMARY.md for technical details
- Examine code - it's well-commented!

## Next Steps

1. ✅ Run `./setup.sh`
2. ✅ Configure `.env`
3. ✅ Run `./start.sh`
4. ✅ Open http://localhost:8000
5. ✅ Start chatting!

---

**Have fun analyzing your sprint data! 📊✨**
