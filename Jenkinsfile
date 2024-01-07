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
                script {
                    echo "hello world"
                    // Define the credentials ID for SSH
                    def SSH_CREDENTIALS = credentials('big-docker-server')
                    // Use the SSH key to execute commands on the remote server
                    withCredentials([sshUserPrivateKey(credentialsId: SSH_CREDENTIALS, keyFileVariable: 'SSH_KEY')]) {
                        sh "ssh -i $SSH_KEY ubuntu@ip-172-31-27-160 'echo hello >> hello.txt'"
                    }
                }
            }
        }
    }
}
