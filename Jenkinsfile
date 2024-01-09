pipeline {
    agent any

    stages {
        
        stage('Clean Workspace') {
            steps {
                sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 ./down.sh"
            }
        }

        stage('Checkout from Git') {
            steps {
                dir('.') {
                    sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 git clone https://github.com/sharanAlwar/PGRKAM.git"
                    sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 ls"
                }
            }
        }
        
        stage('Sonarqube Analysis') {
            steps{
                sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 ./sonar.sh"
            }
        }
        
        stage('Deploying to DockerServer') {
            steps {
                sshagent(['big-docker-server']) {
                    sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 ./run.sh"
                }
            }
        }
    }
}
