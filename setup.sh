#!/bin/bash

echo "Starting DSA RAG setup..."

# Check Python version
python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$python_version < 3.8" | bc -l) )); then
    echo "Error: Python 3.8 or higher is required"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv dsa_rag_env

# Activate virtual environment
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    source dsa_rag_env/Scripts/activate
else
    source dsa_rag_env/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "Creating project directories..."
mkdir -p data/documents

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
OPENAI_API_KEY=your_openai_key_here
COHERE_API_KEY=your_cohere_key_here
ASTRA_DB_APPLICATION_TOKEN=your_astra_token_here
ASTRA_DB_ID=your_astra_db_id
ASTRA_DB_KEYSPACE=your_keyspace

LLM_PROVIDER=COHERE
EOF
    echo "Please update the .env file with your API keys"
fi

echo "Setup complete! To get started:"
echo "1. Update your API keys in .env file"
echo "2. Activate the virtual environment:"
echo "   source dsa_rag_env/bin/activate  # On macOS/Linux"
echo "   dsa_rag_env\\Scripts\\activate    # On Windows"
echo "3. Run the application:"
echo "   uvicorn main:app --reload"
