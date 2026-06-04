pipeline {
    agent any

    environment {
        IMAGE_NAME = 'student-management-system'
        CONTAINER_NAME = 'student-management-system'
        APP_PORT = '5000'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Python Syntax Check') {
            steps {
                bat 'python -m py_compile app.py'
            }
        }

        stage('Run Unit Tests') {
            steps {
                bat 'python -m unittest discover -s tests'
            }
        }

        stage('Build Docker Image') {
            steps {
                bat 'docker build -t %IMAGE_NAME%:%BUILD_NUMBER% -t %IMAGE_NAME%:latest .'
            }
        }

        stage('Deploy Locally') {
            steps {
                bat 'docker stop %CONTAINER_NAME% || exit 0'
                bat 'docker rm %CONTAINER_NAME% || exit 0'
                bat 'docker run -d --name %CONTAINER_NAME% -p %APP_PORT%:5000 %IMAGE_NAME%:latest'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully. Application is available on port 5000.'
        }
        failure {
            echo 'Pipeline failed. Check the Jenkins console output for details.'
        }
    }
}
