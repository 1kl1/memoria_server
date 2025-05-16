# Memoria Server

A FastAPI backend service for managing notes and collections with AI capabilities, Firebase authentication, and dual database system.

## Features

- Firebase authentication with JWT token management

- Note and collection management system

- AI capabilities with Anthropic integration

- Dual database system (SQL + Neo4j)

- Protected API routes

  

## Setup

### Prerequisites
- Python 3.x
- Firebase credentials
- Neo4j database
- SQL database
- Anthropic API key

### Environment Variables
```env
SECRET_KEY=your-secret-key
FIREBASE_API_KEY=your-firebase-api-key
FIREBASE_CREDENTIALS_PATH=path-to-firebase-credentials.json
DATABASE_URL=your-database-url
NEO4J_URL=your-neo4j-url
NEO4J_USER=your-neo4j-username
NEO4J_PASSWORD=your-neo4j-password
ANTHROPIC_API_KEY=your-anthropic-api-key
```

### Installation
```bash
pip install requirements.txt
```

### Running
```bash
docker-compose build
docker-compose up -d
```

## API Documentation
Once the server is running, visit `/docs` for the Swagger documentation.
