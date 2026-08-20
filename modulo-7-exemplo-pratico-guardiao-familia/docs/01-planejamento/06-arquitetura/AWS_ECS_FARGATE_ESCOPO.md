# AWS ECS Fargate ? escopo alvo

## Componentes

- VPC simplificada com subnets privadas/publicas.
- ALB para entrada HTTP/HTTPS.
- ECS Fargate para API e workloads auxiliares.
- ECR para imagens.
- RDS PostgreSQL para dados transacionais.
- ElastiCache Redis para cache e sessoes.
- S3 para assets e anexos.
- Secrets Manager para segredos.
- CloudWatch para logs e metricas.

## Motivo de Fargate

- Menor custo cognitivo e operacional que EKS.
- Menos carga de manutencao de cluster.
- Ajuste melhor ao tamanho da equipe e ao objetivo de release em 6 meses.
- Mantem opcao futura de migrar para uma plataforma mais sofisticada se o produto escalar.

## Fora do escopo

- Service mesh.
- Multi-region.
- EKS/Kubernetes.
- Microservicos novos so por criterio tecnologico.
