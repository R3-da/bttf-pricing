# Back to the Future Pricing Engine

An advanced pricing engine API for the "Back to the Future" DVD saga, built with Python, FastAPI, and Clean Architecture principles.

## Features

- **Pricing Logic**:
  - One BTTF DVD: 15€
  - Two *distinct* BTTF DVDs: 10% discount on BTTF items.
  - Three (or more) *distinct* BTTF DVDs: 20% discount on BTTF items.
  - Other movies: 20€ each.
- **API**: RESTful API to calculate cart prices.
- **Frontend**: Premium, dark-themed responsive UI.
- **Architecture**: Modular, testable, and maintainable codebase.

## Quick Start

### Prerequisites

- Python 3.10+
- Make (optional, for dev commands)

### Installation

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

### Running Locally

Start the server:
```bash
uvicorn src.main:app --reload
```

Visit [http://localhost:8000](http://localhost:8000) to use the web interface.
Visit [http://localhost:8000/docs](http://localhost:8000/docs) for the API Swagger UI.

### Run Tests

```bash
pytest
```

## Docker

Build and run with Docker:

```bash
docker build -t bttf-pricing .
docker run -p 8000:8000 bttf-pricing
```

## Project Structure

```
.
├── src/
│   ├── api/          # API endpoints and routing
│   ├── core/         # Business logic & strategies
│   ├── domain/       # Domain models (Cart, Movie)
│   └── main.py       # Application entry point
├── static/           # Frontend assets (HTML, CSS, JS)
├── tests/            # Unit and Integration tests
├── Dockerfile        # Docker commands
└── pyproject.toml    # Project configuration
```

## Design Decisions

- **Clean Architecture**: Disconnected domain logic from API framework for better testability.
- **Strategy Pattern**: Pricing rules are encapsulated in strategies, allowing easy addition of new rules (e.g., Star Wars implementation).
- **TDD**: Implementation was driven by tests based on the user-provided examples.
- **FastAPI**: Chosen for performance, type safety, and automatic documentation.

---
"Your future hasn't been written yet. No one's has. Your future is whatever you make it. So make it a good one." - Doc Brown
