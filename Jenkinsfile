pipeline {
    agent any

    environment {
        SONAR_TOKEN = 'sonartoken'
    }

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
                withSonarQubeEnv("${SONAR_TOKEN}", envOnly: true) {
                    sh '''ubuntu/bin/sonar-scanner -Dsonar.projectKey=testing-sonar \
                    -Dsonar.sources=. \
                    -Dsonar.host.url=http://54.87.215.11:9000 \
                    -Dsonar.login=sqp_26bf4ddbc9b0e86678d9eaa71da44f2410163c29'''
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
