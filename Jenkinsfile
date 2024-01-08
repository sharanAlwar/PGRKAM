pipeline {
    agent any
    environment {
        SSH_CREDENTIALS = credentials('big-docker-server')
        remoteHost = 'ubuntu@ip-172-31-27-160' // Define the remote server address
    }
    stages {
        stage('Clean Workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout from Git') {
            steps {
                git branch: 'main', url: 'https://github.com/sharanAlwar/PGRKAM.git'
            }
        }

        stage('Testing') {
            steps {
                script {
                    echo "This is the testing phase ${SSH_CREDENTIALS_PSW}"
                    sshCommand remote: remoteHost, credentials: 'SSH_CREDENTIALS', command: 'docker-compose up --build'
                }
            }
        }
    }
}
