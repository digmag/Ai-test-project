# Hospital Management Application

This is a Python/Tornado web application for hospital management.

## Project Structure

- **Backend:** Python with Tornado framework
- **Database:** Redis
- **Frontend:** HTML templates with Bootstrap CSS

## Features

- Hospital management
- Doctor management
- Patient management
- Diagnosis tracking
- Doctor-patient relationships

## Running the Application

### Prerequisites

- Docker
- Docker Compose

### Running with Docker

```bash
docker-compose up -d
```

The application will be available at: http://localhost:8888

### Running Locally (without Docker)

1. Install Python 3.9
2. Install dependencies: `pip install -r requirements.txt`
3. Install and run Redis server
4. Run the application: `python main.py`
5. Visit: http://localhost:8888

## Testing

Run unit tests with:

```bash
python -m unittest test_app.py -v
```

## CI/CD Pipeline

This project uses GitHub Actions for:
- Running unit tests
- Building Docker images
- Testing application functionality
- Deploying documentation to GitHub Pages

## GitHub Actions Workflow

The workflow is defined in `.github/workflows/ci-cd.yml` and includes:
- Test job: Runs unit tests
- Build job: Builds and tests Docker image
- Deploy job: Creates and deploys documentation to GitHub Pages

## Note about GitHub Pages Deployment

GitHub Pages only supports static sites, not server-side applications like this Tornado app.
The actual application runs as a Docker container and is not directly deployable to GitHub Pages.
The GitHub Pages site serves as documentation for the project and its CI/CD pipeline.