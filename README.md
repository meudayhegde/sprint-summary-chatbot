# Sprint Summary Chatbot 🚀

An intelligent AI-powered chatbot for analyzing sprint data with interactive visualizations. Built with FastAPI, LangChain, and Plotly, supporting multiple LLM providers (OpenAI GPT, Google Gemini, Anthropic Claude).

## Features ✨

- **Interactive Chatbot Interface**: Beautiful, modern UI for natural conversations about sprint data
- **Multi-LLM Support**: Seamlessly switch between OpenAI GPT-4, Google Gemini, or Anthropic Claude
- **Intelligent Data Analysis**: LangChain-powered agent that understands context and provides precise answers
- **Interactive Visualizations**: Automatic chart generation with Plotly for better insights
- **RESTful API**: Well-documented endpoints for programmatic access
- **Real-time Analytics**: Sprint velocity, team performance, bug analysis, and more

## Architecture 🏗️

The application follows best practices and design patterns:

- **MVC Pattern**: Clear separation between data (analyzer), business logic (agent), and presentation (FastAPI)
- **Repository Pattern**: Data access abstracted through SprintDataAnalyzer class
- **Strategy Pattern**: Pluggable LLM providers (OpenAI, Gemini, Claude)
- **Factory Pattern**: Dynamic LLM initialization based on configuration
- **Single Responsibility**: Each module has a focused purpose

## Technology Stack 💻

- **Backend**: FastAPI (async Python web framework)
- **AI/ML**: LangChain, OpenAI GPT-4, Google Gemini, Anthropic Claude
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly
- **Configuration**: Pydantic Settings with .env support

## Project Structure 📁

```
sprint-summary/
├── app.py                              # FastAPI application with routes and UI
├── agent.py                            # LangChain agent for intelligent query processing
├── data_analyzer.py                    # Data analysis utilities
├── chart_generator.py                  # Plotly chart generation
├── config.py                           # Configuration management
├── requirements.txt                    # Python dependencies
├── .env.example                        # Environment variables template
├── sprint_synthetic_data(Tickets).csv  # Sprint data
└── README.md                           # This file
```

## Installation 🚀

### Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- An API key from at least one provider (OpenAI, Google, or Anthropic)

### Step 1: Clone or Navigate to the Project

```bash
cd /Users/udayhegde/Programming/sprint-summary
```

### Step 2: Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Environment Variables

Copy the example environment file and configure it:

```bash
cp .env.example .env
```

Edit `.env` and add your API keys:

```env
# Choose your preferred LLM provider
LLM_PROVIDER=openai  # Options: openai, gemini, anthropic

# Add your API key(s)
OPENAI_API_KEY=sk-your-openai-api-key-here
GOOGLE_API_KEY=your-google-api-key-here
ANTHROPIC_API_KEY=your-anthropic-api-key-here

# Optional: Customize model names
OPENAI_MODEL=gpt-4-turbo-preview
GEMINI_MODEL=gemini-pro
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022

# Application Settings
APP_HOST=0.0.0.0
APP_PORT=8000
DEBUG=True
```

### Step 5: Run the Application

```bash
python app.py
```

Or using uvicorn directly:

```bash
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
```

The application will be available at: **http://localhost:8000**

## Usage 💡

### Web Interface

1. Open your browser and navigate to `http://localhost:8000`
2. You'll see an attractive chat interface with suggested questions
3. Type your question or click a suggestion chip
4. The AI will analyze your data and provide insights with visualizations

### Example Questions

- "Show me overall sprint summary"
- "How is the team performing?"
- "What's the status of bugs in Sprint 1?"
- "Create a velocity chart for all sprints"
- "Who has the most completed story points?"
- "Show me all high priority tickets that are in progress"
- "What's the completion rate for SPR-002?"

### API Endpoints

#### Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "Show me sprint summary"}'
```

#### Health Check
```bash
curl "http://localhost:8000/health"
```

#### Get Data Summary
```bash
curl "http://localhost:8000/api/summary"
```

#### Get Sprint Details
```bash
curl "http://localhost:8000/api/sprint/SPR-001"
```

#### Get Team Performance
```bash
curl "http://localhost:8000/api/team-performance"
```

#### Get Bug Analysis
```bash
curl "http://localhost:8000/api/bugs"
```

## Switching Between LLM Providers 🔄

To switch between different AI models, simply update the `LLM_PROVIDER` in your `.env` file:

### For OpenAI GPT-4/GPT-5:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your-key-here
OPENAI_MODEL=gpt-4-turbo-preview  # or gpt-4, gpt-3.5-turbo
```

### For Google Gemini:
```env
LLM_PROVIDER=gemini
GOOGLE_API_KEY=your-key-here
GEMINI_MODEL=gemini-pro
```

### For Anthropic Claude:
```env
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
ANTHROPIC_MODEL=claude-3-5-sonnet-20241022  # or claude-3-opus-20240229
```

Restart the application after changing the provider.

## Features in Detail 📊

### Data Analysis Capabilities

- **Sprint Metrics**: Total tickets, story points, velocity, completion rates
- **Team Performance**: Individual and team productivity metrics
- **Bug Analysis**: Bug counts, severity distribution, resolution status
- **Custom Queries**: Flexible pandas-based querying for complex analysis

### Visualization Types

- **Pie Charts**: Status distribution, priority breakdown
- **Bar Charts**: Sprint velocity, team performance, ticket types
- **Line Charts**: Timeline analysis, trend visualization
- **Gauge Charts**: Completion rates, progress indicators

### LangChain Agent Features

- **Contextual Understanding**: Maintains conversation context
- **Tool Selection**: Automatically chooses the right analysis tools
- **Smart Responses**: Provides insights beyond raw data
- **Error Handling**: Graceful handling of ambiguous queries

## Development 🛠️

### Code Quality

The codebase follows Python best practices:

- Type hints for better IDE support
- Comprehensive docstrings
- Error handling and logging
- Modular, testable code structure

### Adding New Features

1. **New Analysis Function**: Add to `data_analyzer.py`
2. **New Chart Type**: Add to `chart_generator.py`
3. **New Tool**: Add to `agent.py` `_create_tools()` method
4. **New Endpoint**: Add to `app.py`

### Logging

Logs are written to console with timestamps. Adjust logging level in `app.py`:

```python
logging.basicConfig(level=logging.DEBUG)  # For more verbose logs
```

## Troubleshooting 🔧

### Common Issues

**Issue**: "API key not configured"
- **Solution**: Ensure your `.env` file has the correct API key for your chosen provider

**Issue**: "Module not found"
- **Solution**: Run `pip install -r requirements.txt` in your virtual environment

**Issue**: "Data file not found"
- **Solution**: Ensure `sprint_synthetic_data(Tickets).csv` is in the project root

**Issue**: Charts not rendering
- **Solution**: Check browser console for errors; ensure Plotly CDN is accessible

**Issue**: Slow responses
- **Solution**: Consider using a faster model (e.g., gpt-3.5-turbo) or check network connection

## Performance Optimization 🚄

- Data is loaded once at startup and cached in memory
- Pandas operations are optimized for large datasets
- Charts are generated on-demand
- Async FastAPI endpoints for concurrent requests

## Security Considerations 🔒

- API keys stored in `.env` (never commit to version control)
- CORS configured (adjust for production)
- Input validation with Pydantic models
- No sensitive data exposed in logs

## Future Enhancements 🔮

Potential improvements:

- [ ] User authentication and authorization
- [ ] Database integration for persistent chat history
- [ ] Export reports to PDF/Excel
- [ ] Real-time data updates via WebSocket
- [ ] Advanced filtering and drill-down capabilities
- [ ] Integration with Jira/Azure DevOps APIs
- [ ] Multi-file analysis support
- [ ] Automated anomaly detection

## Contributing 🤝

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Follow existing code style and patterns
4. Add tests for new features
5. Update documentation
6. Submit a pull request

## License 📄

This project is provided as-is for educational and commercial use.

## Support 💬

For issues, questions, or suggestions:

- Check existing issues in the repository
- Review this README and code comments
- Create a new issue with detailed information

## Acknowledgments 🙏

Built with:
- [FastAPI](https://fastapi.tiangolo.com/)
- [LangChain](https://python.langchain.com/)
- [Plotly](https://plotly.com/python/)
- [Pandas](https://pandas.pydata.org/)
- [OpenAI](https://openai.com/)
- [Google Gemini](https://ai.google.dev/)
- [Anthropic Claude](https://www.anthropic.com/)

---

**Happy Analyzing! 📊✨**
