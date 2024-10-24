pipeline {
    agent any
    
    environment {
        IMAGE_NAME = 'bac_calculator'
        REGISTRY_CREDENTIALS = 'your_registry_credentials_id'
        DOCKER_REGISTRY = 'your_docker_registry_url'
    }
    
    stages {
        stage('Checkout') {
            steps {
                git 'https://github.com/StevoMc/BAC_Calculator.git'
            }
        }
        
        stage('Build') {
            steps {
                script {
                    docker.build("${IMAGE_NAME}:latest")
                }
            }
        }
        
        stage('Test') {
            steps {
                script {
                    docker.image("${IMAGE_NAME}:latest").inside {
                        sh 'pytest tests/'
                    }
                }
            }
        }
        
        stage('Push') {
            steps {
                script {
                    docker.withRegistry("${DOCKER_REGISTRY}", "${REGISTRY_CREDENTIALS}") {
                        docker.image("${IMAGE_NAME}:latest").push()
                    }
                }
            }
        }
        
        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                // Add deployment scripts/commands here
            }
        }
    }
    
    post {
        always {
            script {
                sh 'docker rmi ${IMAGE_NAME}:latest'
            }
        }
    }
}