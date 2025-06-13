# AlgoAI

Welcome to **AlgoAI**! 🚀 A powerful agentic Retrieval Augmented Generation (RAG) system designed to answer all your questions about **Data Structures** and **Algorithms**. Whether you're a student, developer, or enthusiast, this system is here to help you understand and explore DSA concepts like never before. 💡

With **LangChain** and **FastAPI** at its core, you can configure the system to use either **Gemini** or **OpenAI** or **Cohere** as the LLM provider (though I highly recommend **Gemini** for a cost-effective option). 😎

🚀 **Live Demo**: [Visit AlgoAI](https://algo-ai.api.abubeker.com/)

## Technologies

This project is powered by a blend of cutting-edge technologies:

- **Python**
- **LangChain** & **LangGraph** (for seamless integration with various LLMs)
- **Postgres** (for storing messages)
- **Astra** (for vector storage)
- **OpenAI** (LLM provider support)
- **Gemini** (LLM provider support)
- **Cohere** (LLM provider support)
- **FastAPI** (for fast API with async support)

## Features

- 🤖 **Multiple LLM Provider Support**: Choose between OpenAI and Cohere for your LLM needs, with **Cohere** being the recommended option for optimal performance.
- 📚 **Diverse Source Types**: Easily add sources like Text, URLs, and PDFs to improve the system's knowledge.
- 🔄 **Streaming Responses**: Enjoy real-time responses as you ask questions and get immediate answers!
- 💾 **Vector Storage**: With **Astra DB**, the system efficiently stores vectors to power your queries.
- 📦 **Persistent Messages**: Thanks to **Postgres**, all your interaction history is stored and easily accessible.
- ⚡ **Fast and Async**: Powered by **FastAPI**, this system handles requests quickly and efficiently, even with heavy usage.
- 🔧 **Customizable Chunking Strategies**: Configure how the system breaks down and processes data for optimal results.

## Running locally

1. **Clone the repository**:

```bash
git clone https://github.com/nchalimba/algo-ai.git
cd algo-ai
```

2. **Create and activate a virtual environment:**

# Create environment

```bash
# Create environment
python3 -m venv algo_ai_env

# Activate on Windows:
algo_ai_env\Scripts\activate
# Activate on macOS/Linux:
source algo_ai_env/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Create `.env` file** and add your environment variables. Refer to `.env.example` for guidance.

5. **Run the app**:

```bash
uvicorn src.main:app --reload
```

6. **Enjoy the app at [http://localhost:8000](http://localhost:8000)**

## Contributing

I’d love your help! If you'd like to improve the visualizations or add new algorithms, feel free to fork the repo and open a pull request.

---

## License

This project is licensed under the [MIT License](./LICENSE).
