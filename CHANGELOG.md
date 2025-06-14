# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Upcoming Changes

Stay tuned for exciting new features and improvements!

## [1.1.0] - 2025-06-13

### Added

- **Gemini as Default LLM Provider**: Integrated **Gemini** as the primary Large Language Model, enhancing the AI's understanding and generation capabilities.
- **Experimental v2 Get Messages Endpoint**: Introduced an experimental new version of the `get messages` endpoint, designed for improved performance and flexibility in retrieving conversation history.

## [1.0.1] - 2025-02-19

### 🔧 Documentation

- Renamed repository from `dsa-rag` to `algo-ai` (no impact on functionality).

## [1.0.0] - 2025-02-08

### Added

- **Initial Release of AlgoAI**: The foundational release of the AlgoAI system, built with **FastAPI**, **LangChain**, **Datastax Astra DB**, and **Postgres**.
- **API Endpoints**:
  - **auth endpoint**: Admin login functionality to manage access securely.
  - **chat endpoint**: The core interaction point for users to engage with the RAG system.
  - **health endpoint**: A simple health check to monitor the system's status.
  - **info endpoint**: Provides detailed information about the API.
  - **document endpoint**: Allows for the creation or deletion of data sources.
  - **message endpoints**: Enables fetching and deletion of messages, offering more control over interactions.
