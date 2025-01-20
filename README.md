# DSA RAG

A Retrieval Augmented Generation (RAG) system for answering questions about Data Structures and Algorithms. The system uses LangChain, FastAPI, and can be configured to use either OpenAI or Cohere as the LLM provider.

## Features

- 🤖 Multiple LLM provider support (OpenAI/Cohere)
- 📚 Process various input types (Text, URLs, PDFs)
- 🔄 Streaming responses
- 💾 Vector storage using Datastax Astra DB
- ⚡ Fast API with async support
- 🔧 Configurable chunking strategies

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- API keys for:
  - OpenAI or Cohere
  - Datastax Astra DB

## Installation

### Option 1: Using Setup Script (Recommended)

1. Clone the repository:

```bash
git clone https://github.com/nchalimba/dsa_rag.git
cd dsa_rag
```

2. Make the setup script executable and run it:

```bash
chmod +x setup.sh
./setup.sh
```

3. Update the `.env` file with your API keys.

### Option 2: Manual Setup

1. Clone the repository:

```bash
git clone https://github.com/nchalimba/dsa_rag.git
cd dsa_rag
```

2. Create and activate virtual environment:

```bash
# Create environment
python3 -m venv dsa_rag_env

# Activate on Windows:
dsa_rag_env\Scripts\activate
# Activate on macOS/Linux:
source dsa_rag_env/bin/activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create `.env` file and add your API keys:

```
OPENAI_API_KEY=your_openai_key_here
COHERE_API_KEY=your_cohere_key_here
ASTRA_DB_APPLICATION_TOKEN=your_astra_token_here
ASTRA_DB_ID=your_astra_db_id
ASTRA_DB_KEYSPACE=your_keyspace

LLM_PROVIDER=COHERE
```

## Usage

1. Start the server:

```bash
uvicorn main:app --reload
```

2. The API will be available at:

- API: http://localhost:8000
- Documentation: http://localhost:8000/docs

### Available Endpoints

- `POST /process/text` - Process text input
- `POST /process/url` - Process content from URL
- `POST /process/pdf` - Process PDF file
- `GET /message`- Get all messages for a given user id
- `DELETE /message` - Delete all messages for a given user id
- `POST /ask` - Ask questions (streaming response)
- `GET /health` - Health check

## Configuration

You can configure various aspects of the system through environment variables and the config files:

- LLM Provider: Set `LLM_PROVIDER` in `.env` to either `OPENAI` or `COHERE`
- Model Settings: Adjust in `src/config/ml_config.py`
- Chunking Strategies: Configure in `src/config/ml_config.py`

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**

   - Ensure virtual environment is activated
   - Verify all dependencies are installed: `pip install -r requirements.txt`

2. **API Key Errors**

   - Check `.env` file exists
   - Verify API keys are correct
   - Ensure environment variables are loaded

3. **Connection Errors**
   - Verify Astra DB connection details
   - Check internet connection
   - Verify API service status

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
