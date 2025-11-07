# Vadis Media Product Placement AI Platform

## Overview

The **Vadis Media Product Placement AI Platform** is a comprehensive Streamlit-based application designed to revolutionize the movie production and product placement industry. This platform leverages cutting-edge AI technologies to generate scripts, analyze content, match actors, and forecast financial returns.

## Features

### 🎬 Core Functionality

1. **AI Script Generation**
   - Generate professional script outlines across multiple genres
   - Customizable prompt templates
   - Support for Thriller, Comedy, Children's Movies, Rom-Com, Crime, and more
   - Automatic script saving with timestamps

2. **Script Upload & Analysis**
   - Upload custom scripts or use generated ones
   - AI-powered analysis for product placement opportunities
   - Character analysis and scene breakdown
   - Market potential assessment

3. **Script Comparison**
   - Side-by-side comparison of original vs. modified scripts
   - Unified diff and inline diff views
   - Change statistics and analysis
   - Export comparison reports

4. **AI Casting Match**
   - Integration with TMDB (The Movie Database)
   - Search for actors by name, genre, and popularity
   - AI-powered casting recommendations
   - Cast list management and export

5. **Financial Revenue Forecasting**
   - ROI analysis and calculations
   - Scenario planning (best case, expected, worst case)
   - Break-even analysis
   - Market insights using AI and Tavily search

6. **API Management**
   - Centralized API configuration and testing
   - Support for OpenAI, TMDB, OMDB, and Tavily APIs
   - Data browsing and search capabilities
   - Connection status monitoring

## Technology Stack

### Core Technologies

- **Streamlit**: Web application framework
- **Python 3.11**: Programming language
- **SQLite**: Database for data persistence

### AI & Machine Learning

- **OpenAI GPT-4**: Script generation and analysis
- **LangChain**: LLM orchestration framework
- **LangGraph**: Agentic workflow management

### External APIs

- **TMDB API**: Movie and actor database
- **OMDB API**: Detailed movie information
- **Tavily API**: Real-time market research and trends

### Data Generation

- **Faker**: Synthetic data generation for testing

## Architecture

```
movies-product-placement/
├── Home.py                 # Main application entry point
├── pages/                  # Streamlit pages
│   ├── 1_AI_Script_Generation.py
│   ├── 2_Script_Upload_Analysis.py
│   ├── 3_Script_Comparison.py
│   ├── 4_AI_Casting_Match.py
│   ├── 5_Financial_Forecasting.py
│   ├── 6_API_Management.py
│   └── 10_User_Guide.py
├── utils/                  # Utility modules
│   ├── __init__.py
│   └── db_util.py         # Database operations
├── prompts/                # AI prompt templates
│   └── script_generation.txt
├── scripts/                # Generated and uploaded scripts (gitignored)
├── db/                     # Database files
│   └── vadis_media.db     # SQLite database (gitignored)
├── sql/                    # Database schema
│   └── schema.sql
├── docs/                   # Documentation
│   ├── USER_GUIDE.md
│   ├── DEPLOYMENT_SUMMARY.md
│   └── presentation_content.md
├── tests/                  # Test files
│   ├── test_api_connections.py
│   ├── test_script_generation.py
│   └── openai_test.py
├── test-results/           # Test result outputs (gitignored)
├── screenshots/            # Application screenshots (gitignored)
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (not in git)
├── .env.sample             # Environment variables template
└── README.md              # This file
```

## Installation

### Prerequisites

- Python 3.11 or higher
- pip package manager
- Git

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/predictivelabsai/movies-product-placement.git
   cd movies-product-placement
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.sample .env
   # Edit .env with your API keys
   ```

4. **Initialize database**
   ```bash
   mkdir -p db
   sqlite3 db/vadis_media.db < sql/schema.sql
   ```

   Or use the Python utility:
   ```python
   from utils.db_util import init_database
   init_database()
   ```

5. **Run the application**
   ```bash
   streamlit run Home.py
   ```

## Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
TMDB_API_KEY=your_tmdb_api_key
TMDB_API_READ_TOKEN=your_tmdb_read_token
OMDB_API_KEY=your_omdb_api_key
TAVILY_API_KEY=your_tavily_api_key
```

### API Key Sources

- **OpenAI**: [platform.openai.com](https://platform.openai.com/)
- **TMDB**: [developers.themoviedb.org](https://developers.themoviedb.org/)
- **OMDB**: [omdbapi.com](http://www.omdbapi.com/)
- **Tavily**: [tavily.com](https://tavily.com/)

## Usage

### Starting the Application

```bash
streamlit run Home.py
```

The application will open in your default browser at `http://localhost:8501`

### Navigation

Use the sidebar to navigate between different pages:

1. **Home**: Overview and quick start guide
2. **AI Script Generation**: Create new script outlines
3. **Script Upload & Analysis**: Analyze existing scripts
4. **Script Comparison**: Compare original and modified scripts
5. **AI Casting Match**: Find suitable actors
6. **Financial Forecasting**: Estimate revenue and ROI
7. **API Management**: Configure and test APIs

### Workflow Example

1. Generate a script using AI Script Generation
2. Analyze the script for product placement opportunities
3. Find suitable actors using AI Casting Match
4. Forecast potential revenue using Financial Forecasting
5. Compare original script with product-integrated version

## Database Schema

The application uses SQLite with the following main tables:

- **scripts**: Store generated and uploaded scripts
- **product_placements**: Track product placement opportunities
- **actors**: Cache actor information from TMDB
- **script_casting**: Link scripts with selected actors
- **revenue_forecasts**: Store financial forecasts

## Testing

Test files are located in the `tests/` directory. Test results are saved to `test-results/` in JSON format.

To run tests:
```bash
python tests/test_script_generation.py
python tests/test_api_connections.py
```

## Development

### Adding New Features

1. Create a new page in the `pages/` directory
2. Follow the naming convention: `N_Page_Name.py`
3. Import required dependencies
4. Implement page logic using Streamlit components

### Customizing Prompts

Edit prompt templates in the `prompts/` directory to customize AI behavior.

## Troubleshooting

### Common Issues

1. **API Connection Errors**
   - Verify API keys in `.env` file
   - Check API status in API Management page
   - Ensure internet connectivity

2. **Database Errors**
   - Reinitialize database: `sqlite3 vadis_media.db < sql/schema.sql`
   - Check file permissions

3. **Module Import Errors**
   - Reinstall dependencies: `pip install -r requirements.txt`
   - Check Python version compatibility

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is proprietary software owned by Vadis Media.

## Contact

For questions or support, visit [vadis-media.com](https://www.vadis-media.com/)

## Acknowledgments

- **Vadis Media**: Project sponsor and domain expertise
- **OpenAI**: AI technology provider
- **TMDB**: Movie and actor database
- **Streamlit**: Application framework

---

**Version**: 1.0.0  
**Last Updated**: October 2025  
**Maintainer**: Vadis Media Development Team
