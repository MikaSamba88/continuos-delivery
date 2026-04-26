# Continuous Delivery Project

A Python-based FastAPI application demonstrating a complete Continuous Deployment pipeline using Docker and GitLab CI/CD (migrated to GitHub).

## 📂 Project Structure

* **`src/`**: Application source code (FastAPI).
* **`tests/`**: Unit and integration tests with Pytest.
* **`scripts/`**: Automation scripts for deployment and cleanup.
* **`Dockerfile`**: Multi-stage build for production and testing.

## 🚀 Getting Started

### Local Development
1. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # macOS/Linux
   # or .venv\Scripts\activate on Windows
