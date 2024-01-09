pipeline {
    agent any
    stages {
        stage('Clean Workspace') {
            steps {
                sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 ./down.sh"
                sh "ssh -tt -o StrictHostKeyChecking=no ubuntu@18.207.144.22 rm -rf PGRKAM " 
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

        stage('SonarQube Analysis') {
            agent any
            steps {
                withSonarQubeEnv('testing-sonar') {
                    sh 'mvn clean package sonar:sonar'
                }
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
