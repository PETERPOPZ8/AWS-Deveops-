# Student Management System

A complete local student management app with:

- Frontend pages for login, dashboard, students, departments, and settings
- Backend routes using Python's built-in web server
- SQLite database stored in `students.db`
- Add, edit, search, and delete student records

## Run

```powershell
python app.py
```

Open:

```text
http://127.0.0.1:5000
```

If your system Python shortcut is not working, run it with the bundled Python available on this machine:

```powershell
& 'C:\Users\AKSARA\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' app.py
```

## Files

- `app.py` contains the backend, routes, and SQLite database logic.
- `static/style.css` contains the frontend styling.
- `students.db` is created automatically when the app runs.

## DevOps Setup

This project is now prepared like a small DevOps-ready application.

### Configuration

The app supports environment variables:

```text
APP_HOST=127.0.0.1
APP_PORT=5000
DATABASE_PATH=students.db
```

For Docker, the app uses:

```text
APP_HOST=0.0.0.0
APP_PORT=5000
DATABASE_PATH=/app/data/students.db
```

### Docker Run

Build the image:

```powershell
docker build -t student-management-system .
```

Run the container:

```powershell
docker run -p 5000:5000 student-management-system
```

Open:

```text
http://127.0.0.1:5000
```

### Docker Compose

Run with persistent database storage:

```powershell
docker compose up --build
```

Stop:

```powershell
docker compose down
```

### Health Check

The app has a health endpoint:

```text
http://127.0.0.1:5000/health
```

It returns:

```text
OK
```

This can be used by Docker, load balancers, or monitoring tools.

### CI/CD

GitHub Actions workflow is available at:

```text
.github/workflows/ci.yml
```

It performs:

- Code checkout
- Python setup
- Syntax check
- Unit tests
- Docker image build

### DevOps Explanation

You can explain the DevOps part like this:

```text
I containerized the Student Management System using Docker, added Docker Compose for easier local deployment, externalized runtime configuration using environment variables, added a health check endpoint for monitoring, and created a GitHub Actions CI pipeline to validate the code and build the Docker image automatically.
```

### Deployment Flow

```text
Developer pushes code to GitHub
GitHub Actions runs tests and builds Docker image
Docker image can be deployed to a server
Application runs on port 5000
SQLite data is stored in a persistent Docker volume
Health check confirms the app is running
```

## Jenkins Pipeline

This project also includes a Jenkins pipeline:

```text
Jenkinsfile
```

The Jenkins pipeline does:

- Checkout source code
- Run Python syntax check
- Run unit tests
- Build Docker image
- Stop old container
- Remove old container
- Run the new container on port `5000`

### Jenkins Requirements

Install these on the Jenkins machine:

- Python
- Docker
- Git
- Jenkins Pipeline plugin

If Jenkins is running on Windows, the included `Jenkinsfile` uses `bat` commands.

### Jenkins Job Setup

1. Create a new Jenkins Pipeline job.
2. Connect your GitHub repository.
3. Set Pipeline script from SCM.
4. Select Git.
5. Set the script path as:

```text
Jenkinsfile
```

6. Build the job.

### Jenkins Explanation

You can explain it like this:

```text
I created a Jenkins declarative pipeline for CI/CD. The pipeline checks out the code, validates Python syntax, runs unit tests, builds a Docker image, removes the old running container, and deploys the latest version as a new Docker container.
```
