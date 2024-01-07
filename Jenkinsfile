pipeline{
    agent any
    stages{
        stage('clean workspace'){
            steps{
                cleanWs()
            }
        }

        stage('Checkout from git'){
            steps{
                git branch: 'main', url: 'https://github.com/sharanAlwar/PGRKAM.git'
            }
        }

        stage('Testing'){
            steps{
                echo "this is tesing phase"
            }
        }

        stage('Deploying'){
            steps{
                echo "this is deploying phase"
            }
        }
    }
}
