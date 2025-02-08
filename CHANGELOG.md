# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),  
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-02-08

### Added

- **Initial Release of DSA RAG**: Core setup using FastAPI, LangChain, Datastax Astra DB, and Postgres.
- **API Endpoints**:

  - auth endpoint for admin login
  - chat endpoint for interacting with the RAG system
  - health endpoint for checking system health
  - info endpoint for getting information about the API
  - document endpoint for processing creating or deleting sources
  - message endpoints for getting and deleting messages
