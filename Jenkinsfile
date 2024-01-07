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

        stage('Deploying') {
            steps {
                echo "This is the deploying phase"

                // SSH2Easy: Execute multiple SSH Commands
                ssh2Easy([sshServer: [
                    sshCredential: 'big-docker-server~~ubuntu~~18.207.144.22',
                    sshHost: 'ubuntu@ip-172-31-27-160',
                    sshPort: '22',
                    sshUser: 'ubuntu',
                    sshCommand: '''
                        echo "hello" >> hello.txt
                    '''
                ]])
            }
        }
    }
}
