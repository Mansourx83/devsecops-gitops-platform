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
                                --cache=true \
                                --cache-repo="mansour19/spring-boot-demo-cache"
                        '''
                    }
                }
            }
        }

       stage('Security Scan (Syft & Grype)') {
    steps {
        container('syft-grype') {
            sh '''
                set -e

                echo "=========================================="
                echo "        SECURITY SCAN"
                echo "=========================================="

                echo ""
                echo "===== Running Syft ====="

                time syft "${IMAGE_NAME}:${IMAGE_TAG}" \
                    --scope all-layers \
                    -o json > sbom.json

                echo ""
                echo "===== Syft Summary ====="

                {
                    echo -e "NAME\\tVERSION\\tTYPE\\tPATH"

                    jq -r '
                        .artifacts[] |
                        [
                            .name,
                            .version,
                            .type,
                            (.locations[0].path // "-")
                        ] |
                        @tsv
                    ' sbom.json
                } | column -t -s $'\\t'

                echo ""
                echo "===== Running Grype ====="

                time grype sbom.json \
                    -o json > grype-report.json

                echo ""
                echo "===== Grype Summary ====="

                grype sbom.json -o table

                echo ""
                echo "=========================================="
                echo "Security scan completed"
                echo "=========================================="

                echo ""
                echo "SBOM:"
                ls -lh sbom.json

                echo ""
                echo "Grype Report:"
                ls -lh grype-report.json
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
        // ═══════════════════════════════════════════════════════════
       stage('DAST Scan (OWASP ZAP)') {
            steps {
                container('zap') {
                    sh '''
                        set -e

                        echo "=========================================="
                        echo "  OWASP ZAP Baseline Scan"
                        echo "  Target: ${APP_URL}"
                        echo "=========================================="

                        zap-baseline.py \
                            -t "${APP_URL}" \
                            -r zap-report-raw.html \
                            -J zap-report.json \
                            -T 2 \
                            -I || true

                        echo ""
                        echo "Scan complete"

                        test -s /zap/wrk/zap-report-raw.html
                        test -s /zap/wrk/zap-report.json

                        cp /zap/wrk/zap-report-raw.html "${WORKSPACE}/zap-report-raw.html"
                        cp /zap/wrk/zap-report.json "${WORKSPACE}/zap-report.json"

                        echo "ZAP HTML:"
                        ls -lh "${WORKSPACE}/zap-report-raw.html"

                        echo "ZAP JSON:"
                        ls -lh "${WORKSPACE}/zap-report.json"
                    '''
                }
            }
        }

        stage('Generate Unified Security Report') {
            steps {
                container('zap') {
                    sh '''
                        set -e

                        echo "=========================================="
                        echo "  GENERATING UNIFIED SECURITY REPORT"
                        echo "=========================================="

                        test -s "${WORKSPACE}/zap-report.json"
                        test -s "${WORKSPACE}/grype-report.json"
                        test -s "${WORKSPACE}/sbom.json"
                        test -f "${WORKSPACE}/reporting/security_report.py"

                        python3 "${WORKSPACE}/reporting/security_report.py" \
                            "${WORKSPACE}/zap-report.json" \
                            "${WORKSPACE}/grype-report.json" \
                            "${WORKSPACE}/sbom.json" \
                            "${WORKSPACE}/security-report.html"

                        test -s "${WORKSPACE}/security-report.html"

                        echo ""
                        echo "Unified Security Report:"
                        ls -lh "${WORKSPACE}/security-report.html"
                    '''
                }
            }

            post {
                always {
                    publishHTML([
                        allowMissing: true,
                        alwaysLinkToLastBuild: true,
                        keepAll: true,
                        reportDir: '.',
                        reportFiles: 'security-report.html',
                        reportName: 'Al Ahly Momkn - Unified Security Assessment'
                    ])
                }
            }
        }

        // ═══════════════════════════════════════════════════════════

    }

    post {
        always {
            archiveArtifacts(
                artifacts: 'sbom.json, grype-report.json, zap-report.json, zap-report-raw.html, security-report.html',
                allowEmptyArchive: true,
                fingerprint: true
            )
        }
        success {
            echo "✅ Pipeline succeeded: ${IMAGE_NAME}:${IMAGE_TAG}"
        }
        failure {
            echo "❌ Pipeline failed — check the logs above."
        }
    }
}