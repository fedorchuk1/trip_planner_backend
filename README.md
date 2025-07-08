# TripSyncAI Backend

TripSyncAI is an AI-powered service designed to help groups collaboratively plan trips. It leverages advanced language models, multi-agent orchestration, and real-time data sources to generate personalized itineraries, flight and hotel options, and more. The frontend for the app can be found [here](https://github.com/terpiljenya/pack-trip)


## Overview

TripSyncAI provides a RESTful API for intelligent, group-based travel planning. Users submit their preferences, dates, and destinations, and the backend coordinates a team of AI agents to:

- Propose preliminary trip variations based on group consensus and preferences
- Generate detailed, day-by-day itineraries with activities, restaurants, and events
- Search and recommend flights and hotels using real-time data
- Refine plans based on user feedback

The system is built on the Agno multi-agent framework, which enables complex workflows by coordinating specialized AI agents ("crews") for different planning tasks.


## LLM Models & AI Agents

### Language Models Used

- **OpenAI GPT-4.1**: Used for high-quality, context-aware reasoning and planning.
- **Groq+Meta Llama-3.3-70b**: Used for cost-effective, high-throughput tasks such as summarization and web search.
- **Groq+Meta Llama-4-Scout-17b**: Used for content summarization and extraction from web sources.

### Agent Crews

TripSyncAI organizes its logic into "crews"—teams of specialized agents, each with a distinct role:

- **Preliminary Variations Crew**: Proposes multiple trip options based on group preferences and available dates, optionally generating a visual summary for each plan.
- **Itinerary Crew**: Builds a detailed, day-by-day itinerary, researching events, attractions, and restaurants for each city using web search, Google Maps, and weather data.
- **Flights Crew**: Searches for optimal flight routes between cities using real-time flight data.
- **Hotels Crew**: Finds and recommends hotel or Airbnb options for each city and date range.

Each crew is orchestrated using the Agno library, which provides abstractions for agents, teams, tools, and multi-step workflows.

### The Agno Library

Agno is a multi-agent orchestration framework that enables:

- Modular agent and team definitions
- Tool integration (web search, Google Maps, flight/hotel APIs)
- Response model validation (via Pydantic)
- Flexible LLM backend selection


## API Endpoints

The backend exposes the following main endpoints (see `deploy/api.py`):

- `POST /plan_itinerary`: Generate a detailed itinerary from user input
- `POST /refine_itinerary`: Refine an existing itinerary based on feedback
- `POST /flights`: Get flight options for a given itinerary
- `POST /hotels`: Get hotel options for a given itinerary
- `POST /get_hotels_and_flights`: Get both hotels and flights for a trip
- `POST /preliminary_plan`: Propose preliminary trip plans for group consensus

All endpoints accept and return structured Pydantic models for robust validation.


## Local Development & Startup

### 1. Install Dependencies

This project uses `uv` for environment and dependency management. To install all required and optional dependencies, run:

```bash
uv sync --all-groups --all-extras
```

### 2. Environment Variables

Sensitive API keys and configuration are managed via a `.env` file. To set up your environment:

1. Copy the example file:
   ```bash
   cp .env.example .env
   ```
2. Fill in the required API keys (OpenAI, SerpAPI, Google Maps, GetIMG, etc.) in `.env`.

### 3. Start the API Server

You can start the FastAPI server (for example, using Uvicorn):

```bash
uv run uvicorn deploy.api:app --reload --env-file .env
```


## Project Structure

- `src/trip_planner/`
  - `itinerary_crew.py`: Orchestrates itinerary planning agents
  - `flights_crew.py`: Handles flight search logic
  - `hotels_crew.py`: Handles hotel search logic
  - `preliminary_variations_crew.py`: Generates preliminary trip options
  - `models/`: Pydantic models for all data structures
  - `tools/`: Integrations for flights, hotels, web search, image generation, etc.
  - `prompts/`: Prompt templates and instructions for agents

- `deploy/`
  - `api.py`: FastAPI application and endpoint definitions
  - `models/api.py`: API request/response models


## Requirements

- uv
- Python 3.10+
- API keys for:
  - OpenAI
  - SerpAPI
  - Google Maps
  - GetIMG (for image generation)
  - (Optional) Airbnb MCP server
