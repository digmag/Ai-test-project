# Hospital Management Application

This is a Python/Tornado web application for hospital management.

## Project Structure

- **Backend:** Python with Tornado framework
- **Database:** Redis
- **Frontend:** HTML templates with Bootstrap CSS

## How to Run Locally

```bash
docker-compose up -d
```

Then visit: http://localhost:8888

## GitHub Actions Workflow

This project uses GitHub Actions for:
- Running unit tests
- Building Docker images
- Documentation deployment to GitHub Pages

## Note about GitHub Pages Deployment

GitHub Pages only supports static sites, not server-side applications like this Tornado app.
The actual application runs as a Docker container and is not directly deployable to GitHub Pages.
This page serves as documentation for the project and its CI/CD pipeline.