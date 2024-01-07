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
            environment {
                // Define the credentials ID for SSH
                SSH_CREDENTIALS = credentials('big-docker-server')
            }
            steps {
                // Use the SSH key to execute commands on the remote server
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    sh "ssh ubuntu@ip-172-31-27-160 'echo hello >> hello.txt'"
                }
            }
        }

        stage('Deploying') {
            steps {
                echo "This is the deploying phase"

                // SSH2Easy: Execute multiple SSH Commands
                ssh2Easy(sshServer: [
                    sshCredential: 'big-docker-server~~ubuntu~~18.207.144.22',
                    sshHost: '18.207.144.22', // Replace with the correct hostname or IP
                    sshPort: '22', // Replace with your SSH port if different
                    sshUser: 'ubuntu', // Replace with your SSH username
                    sshCommand: '''
                        echo "hello" >> hello.txt
                    '''
                ])
            }
        }
    }
}
