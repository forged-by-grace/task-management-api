pipeline {
    agent any
    tools {
        jdk 'jdk17'
    }

    environment {
        SCANNER_HOME = tool 'sonarqube-scanner'
        APP_NAME = "task-management-api"
        RELEASE = "1.0.0"
        DOCKER_USER = "conano"
        DOCKER_PASS = 'dockerhub'
        IMAGE_NAME = "${DOCKER_USER}" + "/" + "${APP_NAME}"
        IMAGE_TAG = "${RELEASE}-${BUILD_NUMBER}"
        JENKINS_API_TOKEN = credentials("JENKINS_API_TOKEN")
    }

    stages {
        stage('clean workspace') {
            steps {
                cleanWs()
            }
        }

        stage('Checkout from Git') {
            steps {
                git branch: 'main', url: 'https://github.com/forged-by-grace/task-management-api.git'
            }
        }

        stage("Sonarqube Analysis") {
            steps {
                withSonarQubeEnv('SonarQube-Server') {
                    sh "$SCANNER_HOME/bin/sonar-scanner -Dsonar.projectName=${APP_NAME} -Dsonar.projectKey=${APP_NAME}"
                }
            }
        }

        stage("Quality Gate") {
            steps {
                script {
                    waitForQualityGate abortPipeline: false, credentialsId: 'SonarQube-Token'
                }
            }
        }
       
        stage('TRIVY FS SCAN') {
             steps {
                 sh "trivy fs . > trivyfs.txt"
             }
         }

        stage ('TEST') {
           steps {
               script {
                    sh "pytest"
               }
          }
       }

         stage("Docker Build & Push"){
             steps{
                 script{
                   withDockerRegistry(credentialsId: 'dockerhub', toolName: 'docker'){   
                      sh "docker build -t ${APP_NAME} ."
                      sh "docker tag ${APP_NAME} ${IMAGE_NAME}:latest "
                      sh "docker tag ${APP_NAME} ${IMAGE_NAME}:${IMAGE_TAG} "
                      sh "docker push ${IMAGE_NAME}:latest "
                      sh "docker push ${IMAGE_NAME}:${IMAGE_TAG} "
                    }
                }
            }
        }

        stage("TRIVY Image Scan"){
            steps{
                sh "trivy image ${IMAGE_NAME}:latest > trivyimage.txt" 
            }
        }
        stage ('Cleanup Artifacts') {
           steps {
               script {
                    sh "docker rmi ${IMAGE_NAME}:${IMAGE_TAG}"
                    sh "docker rmi ${IMAGE_NAME}:latest"
               }
          }
       }

       stage("Trigger CD Pipeline") {
            steps {
                script {
                    sh "curl -v -k --user conano-admin:${JENKINS_API_TOKEN} -X POST -H 'cache-control: no-cache' -H 'content-type: application/x-www-form-urlencoded' --data 'IMAGE_TAG=${IMAGE_TAG}' 'ec2-52-66-44-148.ap-south-1.compute.amazonaws.com:8080/job/${APP_NAME}-cd/buildWithParameters?token=gitops-token'"
                }
            }
       }         
    }  
    
    post {
     always {
        emailext attachLog: true,
            subject: "'${currentBuild.result}'",
            body: "Project: ${env.JOB_NAME}<br/>" +
                "Build Number: ${env.BUILD_NUMBER}<br/>" +
                "URL: ${env.BUILD_URL}<br/>",
            to: 'nornubariconfidence@gmail.com',                              
            attachmentsPattern: 'trivyfs.txt,trivyimage.txt'
        }
    }
}