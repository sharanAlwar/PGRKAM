pipeline {
    agent any
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

        stage('ssh-agent') {
            steps {
                sshagent(['big-docker-server']) {
                    sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 docker-compose up --build"
                }
            }
        }
    }
}
