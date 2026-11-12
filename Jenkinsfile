pipeline {
  agent any
  environment {
    IMAGE = 'robinsishodia/gitops-demo'
    TAG   = "${env.BUILD_NUMBER}"
  }
  stages {
    stage('Build image') {
      steps {
        sh 'docker build -t $IMAGE:$TAG app/'
      }
    }
    stage('Push image') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh 'echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin'
          sh 'docker push $IMAGE:$TAG'
        }
      }
    }
    stage('Update manifest') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'github', usernameVariable: 'GH_USER', passwordVariable: 'GH_PASS')]) {
          sh '''
            sed -i "s#image: .*#image: $IMAGE:$TAG#" k8s/deployment.yaml
            git config user.name "jenkins"
            git config user.email "jenkins@localhost"
            git add k8s/deployment.yaml
            git commit -m "ci: deploy $IMAGE:$TAG [skip ci]" || exit 0
            git push https://$GH_USER:$GH_PASS@github.com/RobinSishodia/aws-eks-gitops-argocd.git HEAD:main
          '''
        }
      }
    }
  }
}
