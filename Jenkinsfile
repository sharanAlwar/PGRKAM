pipeline {
    agent any
    environment{
        SSH_CREDENTIALS = credentials('big-docker-server')
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
                echo "This is the testing phase"
            }
        }
        
        stage('SSH Remote Command') {
            echo "hello world ${SSH_CREDENTIALS_PSW} "
            steps {
                echo "inside steps"
                sh "ssh ubuntu@ip-172-31-27-160 'echo hello >> hello.txt'"
                sh "${SSH_CREDENTIALS_PSW}"
                sh "docker-compose up --build"
            }
        }
    }
}
