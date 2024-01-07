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

        stage('Testing') {
            steps {
                echo "This is the testing phase"
            }
        }
        
        stage('SSH Remote Command') {
            steps {
                withCredentials([sshUserPrivateKey(credentialsId: 'big-docker-server')]) {
                    script {
                        echo "hello world"
                        sh "ssh ubuntu@ip-172-31-27-160 'echo hello >> hello.txt'"
                    }
                }
            }
        }
    }
}
