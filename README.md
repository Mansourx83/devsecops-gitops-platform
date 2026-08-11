# 🛡️ DevSecOps Platform with GitOps

> A production-oriented DevSecOps platform demonstrating how multiple applications can be built, secured, and deployed through different CI platforms while sharing a centralized GitOps-based Continuous Delivery layer on Kubernetes.

![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?logo=kubernetes\&logoColor=white)
![Jenkins](https://img.shields.io/badge/Jenkins-CI-D24939?logo=jenkins\&logoColor=white)
![GitLab CI](https://img.shields.io/badge/GitLab-CI/CD-FC6D26?logo=gitlab\&logoColor=white)
![ArgoCD](https://img.shields.io/badge/ArgoCD-GitOps-EF7B4D?logo=argo\&logoColor=white)
![SonarQube](https://img.shields.io/badge/SonarQube-Code_Quality-4E9BCD?logo=sonarqube\&logoColor=white)
![Kaniko](https://img.shields.io/badge/Kaniko-Image_Build-blue)
![Docker](https://img.shields.io/badge/Docker_Hub-Registry-2496ED?logo=docker\&logoColor=white)
![Nexus](https://img.shields.io/badge/Nexus-Artifact_Repo-1B5E20)
![Syft](https://img.shields.io/badge/Syft-SBOM-8A2BE2)
![Grype](https://img.shields.io/badge/Grype-CVE_Scan-red)
![OWASP ZAP](https://img.shields.io/badge/OWASP_ZAP-DAST-black)
![Trivy](https://img.shields.io/badge/Trivy-Security-1904DA?logo=aqua\&logoColor=white)
![Gitleaks](https://img.shields.io/badge/Gitleaks-Secret_Detection-orange)

---

## 📌 Platform Overview

This platform delivers **two independent applications** through **two different CI platforms**, both converging on a **single centralized GitOps deployment layer** managed by Argo CD.

| Application     | Source Control | CI Platform | Security Tools                       |
| --------------- | -------------- | ----------- | ------------------------------------ |
| **Spring Boot** | GitHub         | Jenkins     | SonarQube, Syft, Grype, OWASP ZAP    |
| **Bootstrap 5** | GitLab         | GitLab CI   | Trivy, Gitleaks, Hadolint, CycloneDX |

Both pipelines update a **shared GitOps repository**. Argo CD watches the repository and deploys automatically — neither pipeline ever runs `kubectl` directly.

---

## 🏗️ Architecture

```text
                         DEVELOPERS
                              │
              ┌───────────────┴───────────────┐
              │                               │
              ▼                               ▼
           GitHub                           GitLab
     (Spring Boot App)                (Bootstrap App)
              │                               │
              ▼                               ▼
          Jenkins                          GitLab CI
       Kubernetes Agents               Kubernetes Runner
              │                               │
     ┌────────┴────────┐             ┌────────┴──────────┐
     │ SonarQube       │             │ Hadolint          │
     │ Maven + Nexus   │             │ Kaniko Build      │
     │ Kaniko Build    │             │ Trivy Image Scan  │
     │ Syft + Grype    │             │ Trivy Config Scan │
     │ GitOps Update   │             │ Gitleaks          │
     │ OWASP ZAP       │             │ CycloneDX SBOM    │
     └────────┬────────┘             └────────┬──────────┘
              │                               │
              └───────────────┬───────────────┘
                              │
                              ▼
                   GitOps Manifests Repository
                    (Single Source of Truth)
                              │
                              ▼
                           Argo CD
                         App of Apps
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
         spring-boot-app             bootstrap-app
                 │                         │
                 └────────────┬────────────┘
                              │
                              ▼
                     Kubernetes Cluster
                        namespace: apps
```

---

## 🔗 Related Repositories

| Repository                    | Purpose                                    | Link                                                              |
| ----------------------------- | ------------------------------------------ | ----------------------------------------------------------------- |
| **devsecops-gitops-platform** | Platform infrastructure + Spring Boot CI   | [GitHub](https://github.com/Mansourx83/devsecops-gitops-platform) |
| **bootstrap-devops-app**      | Bootstrap application + GitLab CI pipeline | [GitLab](https://gitlab.com/Mansourx83/bootstrap-devops-app)      |
| **gitops-manifests**          | Centralized GitOps manifests (SSOT)        | [GitHub](https://github.com/Mansourx83/gitops-manifests)          |

---

## 🔄 CI/CD Flow

```text
1. Developer pushes code
         │
         ▼
2. CI pipeline triggers (Jenkins or GitLab CI)
         │
         ▼
3. Build → Security Scan → Image Push to Docker Hub
         │
         ▼
4. Update image tag in GitOps manifests repository
         │
         ▼
5. Argo CD detects the Git change
         │
         ▼
6. Argo CD syncs → Kubernetes deploys the new version
         │
         ▼
7. (Jenkins only) OWASP ZAP scans the live application
```

> **No CI pipeline ever runs `kubectl apply` or deploys directly to Kubernetes.**
> Git is the only deployment trigger. Argo CD is the only deployer.

---

## 🔐 Security Layers

| Layer                | Tool             | Spring Boot | Bootstrap |
| -------------------- | ---------------- | ----------- | --------- |
| Code Quality         | SonarQube        | ✅           | —         |
| Dockerfile Lint      | Hadolint         | —           | ✅         |
| Secret Detection     | Gitleaks         | —           | ✅         |
| Rootless Image Build | Kaniko           | ✅           | ✅         |
| SBOM Generation      | Syft / CycloneDX | ✅           | ✅         |
| CVE Scanning         | Grype / Trivy    | ✅           | ✅         |
| IaC Scanning         | Trivy Config     | —           | ✅         |
| Runtime DAST         | OWASP ZAP        | ✅           | —         |

---

## 🏗️ Infrastructure

All components run on a **Kubernetes (Kind)** cluster.

| Component        | Namespace       | Installed Via    |
| ---------------- | --------------- | ---------------- |
| Jenkins          | `jenkins`       | Helm             |
| SonarQube        | `sonarqube`     | Helm             |
| Nexus Repository | `nexus`         | Helm             |
| Argo CD          | `argocd`        | Kustomize        |
| GitLab Runner    | `gitlab-runner` | Helm             |
| Spring Boot App  | `apps`          | Argo CD (GitOps) |
| Bootstrap App    | `apps`          | Argo CD (GitOps) |

---

## 📂 Repository Structure

```text
devsecops-gitops-platform/            ← This repository
├── spring-boot-app/                  ← Spring Boot source code
│   ├── src/
│   ├── pom.xml
│   └── Dockerfile
├── helm-values/                      ← Helm values (Jenkins, SonarQube, Nexus)
│   ├── jenkins-values.yaml
│   ├── sonarqube-values.yaml
│   └── nexus-values.yml
├── kustomize-manifests/              ← Kustomize (Argo CD install)
│   └── argocd/
│       └── kustomization.yaml
├── Jenkinsfile                       ← Jenkins CI pipeline
├── syft-grype.Dockerfile             ← Custom Syft + Grype image
├── jenkins-rbac.yaml                 ← Jenkins RBAC
└── README.md
```

---

## 🚀 Setup Guide

### 1. Create Namespaces

```bash
kubectl create namespace jenkins
kubectl create namespace sonarqube
kubectl create namespace nexus
kubectl create namespace argocd
kubectl create namespace gitlab-runner
kubectl create namespace apps
```

### 2. Apply RBAC

```bash
kubectl apply -f jenkins-rbac.yaml
```

### 3. Install Helm Components

```bash
helm repo add jenkins https://charts.jenkins.io
helm repo add sonarqube https://SonarSource.github.io/helm-chart-sonarqube
helm repo add sonatype https://sonatype.github.io/helm3-charts/
helm repo add gitlab https://charts.gitlab.io
helm repo update

helm install my-jenkins jenkins/jenkins -n jenkins -f helm-values/jenkins-values.yaml
helm install sonarqube sonarqube/sonarqube -n sonarqube -f helm-values/sonarqube-values.yaml
helm install nexus sonatype/nexus-repository-manager -n nexus -f helm-values/nexus-values.yml
helm install gitlab-runner gitlab/gitlab-runner -n gitlab-runner -f gitlab-runner-values.yaml
```

### 4. Install Argo CD (Kustomize)

```bash
# Use server-side apply to avoid CRD size limits
kubectl apply -k kustomize-manifests/argocd/ --server-side --force-conflicts
```

### 5. Deploy App of Apps

```bash
cd gitops-manifests
kubectl apply -f app-of-apps.yaml
```

### 6. Retrieve Credentials

```bash
# Jenkins
kubectl get secret --namespace jenkins my-jenkins \
  -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode

# Nexus
kubectl exec -it <nexus-pod> -n nexus -- cat /nexus-data/admin.password

# Argo CD
kubectl get secret --namespace argocd argocd-initial-admin-secret \
  -o jsonpath="{.data.password}" | base64 --decode
```

### 7. Port Forward

```bash
kubectl port-forward svc/my-jenkins -n jenkins 8080:8080
kubectl port-forward svc/sonarqube-sonarqube -n sonarqube 9000:9000
kubectl port-forward svc/nexus-nexus-repository-manager -n nexus 8081:8081
kubectl port-forward svc/argocd-server -n argocd 8083:443
```

---

## 🔄 Disaster Recovery

```bash
# 1. Recreate cluster
kind create cluster --config kind-config.yaml

# 2. Recreate namespaces
kubectl create namespace jenkins sonarqube nexus argocd gitlab-runner apps

# 3. Apply RBAC
kubectl apply -f jenkins-rbac.yaml

# 4. Reinstall Helm components
helm install my-jenkins jenkins/jenkins -n jenkins -f helm-values/jenkins-values.yaml
helm install sonarqube sonarqube/sonarqube -n sonarqube -f helm-values/sonarqube-values.yaml
helm install nexus sonatype/nexus-repository-manager -n nexus -f helm-values/nexus-values.yml
helm install gitlab-runner gitlab/gitlab-runner -n gitlab-runner -f gitlab-runner-values.yaml

# 5. Reinstall Argo CD
kubectl apply -k kustomize-manifests/argocd/ --server-side --force-conflicts

# 6. Deploy App of Apps
kubectl apply -f gitops-manifests/app-of-apps.yaml

# 7. Recreate Jenkins credentials (docker-cred, nexus-cred, sonarqube-token, github-cred)
# 8. Regenerate SonarQube token (My Account → Security)
# 9. Reconfigure Nexus Maven proxy (maven-central-proxy + maven-public group)
```

---

## 🚨 Troubleshooting

| Issue                                     | Cause                         | Fix                                                                                 |
| ----------------------------------------- | ----------------------------- | ----------------------------------------------------------------------------------- |
| SonarQube/Nexus pods restarting           | Probe timeouts too short      | Increase `initialDelaySeconds`, `timeoutSeconds`, `failureThreshold` in Helm values |
| Nexus PVC stuck Terminating               | Incomplete cleanup            | Force-delete namespace and reinstall                                                |
| Argo CD CRD too large for `kubectl apply` | annotation size limit (262KB) | Use `--server-side --force-conflicts`                                               |
| ZAP: directory `/zap/wrk` not mounted     | No volume for report output   | Mount `emptyDir` at `/zap/wrk` in ZAP pod spec                                      |
| `kubectl cp` fails on completed pod       | Pod already exited            | Keep container alive with `sleep 300` after scan                                    |
| Jenkins RBAC: `pods/log` forbidden        | Missing permissions           | Add `pods/log` and `pods/exec` to `jenkins-rbac.yaml`                               |
| GitLab Runner not picking up jobs         | Wrong executor or token       | Verify `runnerRegistrationToken` and `executor: kubernetes` in Helm values          |

---

## 🗺️ Roadmap

| Phase | Description                                                    | Status     |
| ----- | -------------------------------------------------------------- | ---------- |
| **1** | Jenkins CI/CD — Spring Boot                                    | ✅ Complete |
| **2** | Argo CD GitOps                                                 | ✅ Complete |
| **3** | GitLab CI — Bootstrap App                                      | ✅ Complete |
| **4** | App of Apps                                                    | ✅ Complete |


---

## 📚 References

* [Kubernetes](https://kubernetes.io/docs/)
* [Argo CD](https://argo-cd.readthedocs.io/)
* [Jenkins Kubernetes Plugin](https://plugins.jenkins.io/kubernetes/)
* [GitLab CI/CD](https://docs.gitlab.com/ee/ci/)
* [Kaniko](https://github.com/GoogleContainerTools/kaniko)
* [Syft](https://github.com/anchore/syft)
* [Grype](https://github.com/anchore/grype)
* [Trivy](https://aquasecurity.github.io/trivy/)
* [Gitleaks](https://github.com/gitleaks/gitleaks)
* [OWASP ZAP](https://www.zaproxy.org/)
* [SonarQube](https://www.sonarqube.org/)
* [Nexus Repository](https://www.sonatype.com/products/repository-oss)
* [Kustomize](https://kustomize.io/)
