🛰️ metrics-healthcheck-service — Cloud Native / Kubernetes Edition

<p align="center"> <img alt="banner" src="https://img.shields.io/badge/Metrics--Healthcheck-CloudNative-00d1ff?style=for-the-badge&logo=prometheus&logoColor=white"/> <img alt="k8s" src="https://img.shields.io/badge/Kubernetes-ready-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white"/> <img alt="docker" src="https://img.shields.io/badge/Docker-image-blue?style=for-the-badge&logo=docker&logoColor=white"/> <img alt="ci" src="https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white"/> </p>

Описание

metrics-healthcheck-service — лёгкий сервис, который предоставляет:

GET /metrics — метрики в формате Prometheus exposition (text/plain).

GET /health/live — liveness probe.

GET /health/ready — readiness probe.

Доп. GET /ping и POST /echo (опционально) для быстрого теста.

Идеален как sidecar / базовый сервис для микросервиса: минимальная привязка к infra, готов к Docker + Kubernetes + Prometheus.

Быстрый старт (локально)

Требования: Docker или Rust/Go/Kotlin/Java (в зависимости от реализации в src/).

1) Сборка локально (пример для Rust)
# в папке репо
cargo build --release
./target/release/metrics-healthcheck-service --port 8080
# или (если в src есть ready бинар) ./run-local.sh

2) Запуск в Docker:
# собрать образ
docker build -t metrics-healthcheck-service:local .

# запустить
docker run --rm -p 8080:8080 metrics-healthcheck-service:local

# проверить
curl http://localhost:8080/health/ready
curl http://localhost:8080/metrics

Dockerfile (рекомендуемый multi-stage)
# Stage: build
FROM rust:1.75 AS builder
WORKDIR /app
COPY . .
RUN cargo build --release

# Stage: runtime
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y ca-certificates && rm -rf /var/lib/apt/lists/*
COPY --from=builder /app/target/release/metrics-healthcheck-service /usr/local/bin/metrics-healthcheck-service
EXPOSE 8080
USER 1000:1000
ENTRYPOINT ["/usr/local/bin/metrics-healthcheck-service"]


(Если проект на Kotlin/Go — замени сборку на ./gradlew build/go build в первом этапе.)

Helm Chart (chart/)

Простой chart уже лежит в папке chart/. Основные файлы:

chart/Chart.yaml — метаданные chart.

chart/values.yaml — значения по умолчанию (image.repository, tag, ресурсы, hpa).

chart/templates/deployment.yaml — Deployment с readiness/liveness и аннотациями Prometheus.

chart/templates/service.yaml — Service.

chart/templates/hpa.yaml — HPA (autoscaling/v2).

Установка (minikube / kind / cluster)
# пример: упаковка и установка локально
helm lint chart
helm upgrade --install metrics chart --namespace monitoring --create-namespace
# проверяем
kubectl get pods -n monitoring
kubectl port-forward svc/metrics 8080:8080 -n monitoring
curl http://localhost:8080/health/ready

Prometheus / ServiceMonitor

Если используешь kube-prometheus-stack, лучше создать ServiceMonitor:

apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: metrics-healthcheck-service
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app.kubernetes.io/name: metrics-healthcheck-service
  namespaceSelector:
    matchNames:
      - monitoring
  endpoints:
    - port: http
      path: /metrics
      interval: 15s

GitHub Actions — CI (build → image → package helm)

Нужен workflow .github/workflows/ci.yaml с шагами:

checkout

setup toolchain (rust/kotlin/go)

cargo/gradle/go build release

docker build & push (GHCR/DockerHub)

helm lint & package

Примерный блок для push образа использует docker/build-push-action@v4. Не забудь добавить GHCR или DockerHub секреты.

Конфигурация (values.yaml — важно)

В chart/values.yaml укажи:

image:
  repository: ghcr.io/<your-org>/metrics-healthcheck-service
  tag: "v0.1.0"
  pullPolicy: IfNotPresent

service:
  port: 8080
  targetPort: 8080

hpa:
  enabled: true
  minReplicas: 1
  maxReplicas: 5
  cpuUtilization: 60

Рекомендации по безопасности и продакшену

Логи → stdout/stderr для централизованного логирования.

Настрой RBAC/NetworkPolicy.

Запускай контейнер непользователем root (как в Dockerfile выше).

Настрой readOnlyRootFilesystem: true, runAsNonRoot: true в pod spec при возможности.

Добавь мониторинг ресурсов (requests/limits) и метрики (latency, errors).

Полезные команды
# локально
docker build -t metrics-healthcheck-service:local .
docker run --rm -p 8080:8080 metrics-healthcheck-service:local

# helm
helm upgrade --install metrics chart -n monitoring --create-namespace

# logs
kubectl logs -l app.kubernetes.io/name=metrics-healthcheck-service -n monitoring

# port-forward для теста
kubectl port-forward svc/metrics-healthcheck-service 8080:8080 -n monitoring

CI / CD — секреты

Добавь в Settings → Secrets (репо):

CR_PAT или GHCR_TOKEN (для push в GHCR)

DOCKERHUB_USERNAME / DOCKERHUB_TOKEN если DockerHub

KUBE_CONFIG_DATA (base64 kubeconfig) — для автоматического деплоя из workflow (опционально)

Roadmap (быстрый)

ServiceMonitor (готовый манифест)

Example values for production (ingress, tls, extraEnv)

Helm chart index / GH Pages (для выдачи chart)

Canary / blue-green deployment example

Integration tests (kind + helm test)

Лицензия

MIT © rolloerro
