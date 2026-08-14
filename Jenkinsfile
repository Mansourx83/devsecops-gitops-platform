pipeline {
    agent {
        kubernetes {
            yaml '''
apiVersion: v1
kind: Pod
metadata:
  namespace: jenkins
spec:
  serviceAccountName: jenkins
  containers:
  - name: jnlp
    image: jenkins/inbound-agent:latest
  - name: maven
    image: maven:3.8.4-openjdk-17
    command: ['cat']
    tty: true
    volumeMounts:
    - name: maven-cache
      mountPath: /root/.m2
  - name: kaniko
    image: gcr.io/kaniko-project/executor:v1.23.2-debug
    command: ['sleep']
    args: ['infinity']
    tty: true
    volumeMounts:
    - name: docker-config
      mountPath: /kaniko/.docker
  - name: kubectl
    image: alpine/k8s:1.29.2
    command: ['sh', '-c', 'while true; do sleep 30; done']
    tty: true
  - name: syft-grype
    image: mansour19/syft-grype:latest
    command: ['cat']
    tty: true
    volumeMounts:
    - name: grype-cache
      mountPath: /root/.cache/grype

  # ── ✅ ADDED: ZAP sidecar ─────────────────────────────────────
  - name: zap
    image: ghcr.io/zaproxy/zaproxy:stable
    command: ['sleep']
    args: ['3600']
    tty: true
    resources:
      requests:
        memory: "1Gi"
      limits:
        memory: "2Gi"
    volumeMounts:
    - name: zap-wrk
      mountPath: /zap/wrk
  # ─────────────────────────────────────────────────────────────

  volumes:
  - name: maven-cache
    persistentVolumeClaim:
      claimName: maven-cache-pvc
  - name: grype-cache
    persistentVolumeClaim:
      claimName: grype-cache-pvc
  - name: docker-config
    emptyDir: {}
  # ── ✅ ADDED: shared ZAP work directory ──────────────────────
  - name: zap-wrk
    emptyDir: {}
  # ─────────────────────────────────────────────────────────────
'''
        }
    }

    environment {
        IMAGE_NAME = 'mansour19/spring-boot-demo'
        IMAGE_TAG  = "${env.BUILD_NUMBER}"
        SONAR_HOST = 'http://sonarqube-sonarqube.sonarqube.svc.cluster.local:9000'
        NEXUS_URL  = 'http://nexus-nexus-repository-manager.nexus.svc.cluster.local:8081'
        APP_URL    = 'http://spring-boot-app-service.apps.svc.cluster.local:80'
    }

    options {
        disableConcurrentBuilds()
        buildDiscarder(logRotator(numToKeepStr: '20'))
    }

    stages {

        stage('Checkout Code') {
            steps {
                checkout scm
            }
        }

        stage('Static Code Analysis (SonarQube)') {
            steps {
                container('maven') {
                    dir('spring-boot-app') {
                        withCredentials([string(credentialsId: 'sonarqube-token', variable: 'SONAR_TOKEN')]) {
                            sh """
                                mvn sonar:sonar \
                                    -Dsonar.projectKey=spring-boot-demo \
                                    -Dsonar.host.url=${SONAR_HOST} \
                                    -Dsonar.login=\$SONAR_TOKEN
                            """
                        }
                    }
                }
            }
        }

        stage('Build and Deploy to Nexus') {
            steps {
                container('maven') {
                    dir('spring-boot-app') {
                        withCredentials([usernamePassword(credentialsId: 'nexus-cred',
                                    passwordVariable: 'NEXUS_PASSWORD',
                                    usernameVariable: 'NEXUS_USER')]) {
                            sh '''
                                cat > nexus-settings.xml <<EOF
<settings>
  <servers>
    <server>
      <id>nexus-releases</id>
      <username>${NEXUS_USER}</username>
      <password>${NEXUS_PASSWORD}</password>
    </server>
    <server>
      <id>nexus-snapshots</id>
      <username>${NEXUS_USER}</username>
      <password>${NEXUS_PASSWORD}</password>
    </server>
  </servers>
</settings>
EOF
                                mvn -s nexus-settings.xml clean deploy -DskipTests
                            '''
                        }
                    }
                }
            }
        }

        stage('Build & Push Image (Kaniko)') {
            steps {
                container('kaniko') {
                    withCredentials([usernamePassword(credentialsId: 'docker-cred',
                            passwordVariable: 'DOCKER_PASSWORD',
                            usernameVariable: 'DOCKER_USER')]) {
                        sh '''
                            AUTH=$(echo -n "$DOCKER_USER:$DOCKER_PASSWORD" | base64 | tr -d '\\n')
                            cat > /kaniko/.docker/config.json <<EOF
{
  "auths": {
    "https://index.docker.io/v1/": {
      "auth": "$AUTH"
    }
  }
}
EOF
                            /kaniko/executor \
                                --context    "$(pwd)/spring-boot-app" \
                                --dockerfile "$(pwd)/spring-boot-app/Dockerfile" \
                                --destination "${IMAGE_NAME}:${IMAGE_TAG}" \
                                --destination "${IMAGE_NAME}:latest" \
                                --cache=true
                        '''
                    }
                }
            }
        }

        stage('Security Scan (Syft & Grype)') {
            steps {
                container('syft-grype') {
                    sh '''
                        syft "${IMAGE_NAME}:${IMAGE_TAG}" \
                            --scope all-layers \
                            -o json > sbom.json

                        echo "===== Syft SBOM ====="
                        syft "${IMAGE_NAME}:${IMAGE_TAG}" \
                            --scope all-layers \
                            -o table

                        grype "${IMAGE_NAME}:${IMAGE_TAG}" -o json > grype-report.json

                        echo "===== Grype Summary ====="
                        grype "${IMAGE_NAME}:${IMAGE_TAG}" -o table
                    '''
                }
            }
        }

        stage('GitOps Update Manifests') {
            steps {
                container('kubectl') {
                    withCredentials([usernamePassword(credentialsId: 'github-cred',
                            passwordVariable: 'GH_PASSWORD',
                            usernameVariable: 'GH_USER')]) {
                        sh """
                            rm -rf /tmp/manifests
                            git clone https://\${GH_USER}:\${GH_PASSWORD}@github.com/Mansourx83/gitops-manifests.git /tmp/manifests
                            cd /tmp/manifests

                            sed -i "s|image: mansour19/spring-boot-demo:.*|image: mansour19/spring-boot-demo:${BUILD_NUMBER}|" spring-boot/deployment.yaml

                            git config user.email "jenkins@ci-cd.local"
                            git config user.name  "Jenkins CI"
                            git add spring-boot/deployment.yaml

                            if git diff --cached --quiet; then
                                echo "No changes to commit"
                            else
                                git commit -m "chore: update spring-boot image tag to ${BUILD_NUMBER}"
                                git push origin main
                                echo "Successfully pushed!"
                            fi
                        """
                    }
                }
            }
        }

        // ═══════════════════════════════════════════════════════════
        // ZAP runs as sidecar — shared emptyDir volume at /zap/wrk
        // Both scan + branding happen inside the zap container
        // because Python3 is available there (jnlp has none)
        // ═══════════════════════════════════════════════════════════
        stage('DAST Scan (OWASP ZAP)') {
            steps {
                container('zap') {
                    sh """
                        echo "=========================================="
                        echo "  OWASP ZAP Baseline Scan"
                        echo "  Target: ${APP_URL}"
                        echo "=========================================="

                        # FIX: zap-baseline.py prepends /zap/wrk/ automatically
                        # so pass filename only — NOT the full path
                        zap-baseline.py \
                            -t "${APP_URL}" \
                            -r zap-report-raw.html \
                            -I || true

                        echo "Scan complete — report size: \$(wc -c < /zap/wrk/zap-report-raw.html) bytes"

                        # Apply branding using Python3 (available in ZAP image)
                        python3 \${WORKSPACE}/brand_zap_report.py \
                            /zap/wrk/zap-report-raw.html \
                            \${WORKSPACE}/zap-report.html

                        echo "Branded report: \$(ls -lh \${WORKSPACE}/zap-report.html)"
                    """
                }
            }

            post {
                always {
                    archiveArtifacts artifacts: 'zap-report.html',
                                       fingerprint:        true,
                                       allowEmptyArchive: true
                }
            }
        }
        // ═══════════════════════════════════════════════════════════

    }

    post {
        always {
            archiveArtifacts artifacts: 'sbom.json, grype-report.json, zap-report.html',
                                     allowEmptyArchive: true
        }
        success {
            echo "✅ Pipeline succeeded: ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "❌ Pipeline failed — check the logs above."
        }
    }
}