pipeline {
    agent any
    stages {
        stage('Clean Workspace') {
            steps {
                sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 rm -rf PGRKAM"
            }
        }

        stage('Checkout from Git') {
            steps {
                // Checkout the repository into a specific directory
                dir('.') {
                    sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 git clone https://github.com/sharanAlwar/PGRKAM.git"
                    sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 ls"
                }
            }
        }

        stage('SSH Agent') {
            steps {
                sshagent(['big-docker-server']) {
                    sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 cd PGRKAM && docker-compose up -d --build"
                }
            }
        }
    }
}
