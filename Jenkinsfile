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
                    sshCredential: 'your-ssh-credentials', // Replace with your SSH credential ID
                    sshHost: 'your_remote_host', // Replace with your remote host
                    sshPort: '22', // Replace with your SSH port if different
                    sshUser: 'your_ssh_username', // Replace with your SSH username
                    sshCommand: '''
                        echo "hello"
                    '''
                ]])
            }
        }
    }
}
