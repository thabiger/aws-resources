
# AWS Resources Report
**Period:** 2025-10-01 — 2025-10-31

## Amazon CloudFront — $0.05

### Summary
- **total_distributions**: 3
- **enabled**: 1
- **disabled**: 2

## Amazon DocumentDB (with MongoDB compatibility) — $420.12

### Summary
- **total_clusters**: 2
- **total_nodes**: 5
- **by_instance_class**:
  - db.t3.micro: 3
  - db.t3.small: 4
  - db.t3.medium: 4
  - db.m5.xlarge: 1
  - db.m6g.2xlarge: 1
  - db.r5.xlarge: 1
  - db.t3.xlarge: 1
  - db.r5.large: 1
- **total_vCPU**: 44
- **total_memory_mib**: 142,336
- **by_instance_type**:
  - t3.micro:
    - **count**: 3
    - **vCPU_each**: 2
    - **memory_mib_each**: 1,024
    - **vCPU_total**: 6
    - **memory_mib_total**: 3,072
  - t3.small:
    - **count**: 4
    - **vCPU_each**: 2
    - **memory_mib_each**: 2,048
    - **vCPU_total**: 8
    - **memory_mib_total**: 8,192
  - t3.medium:
    - **count**: 4
    - **vCPU_each**: 2
    - **memory_mib_each**: 4,096
    - **vCPU_total**: 8
    - **memory_mib_total**: 16,384
  - m5.xlarge:
    - **count**: 1
    - **vCPU_each**: 4
    - **memory_mib_each**: 16,384
    - **vCPU_total**: 4
    - **memory_mib_total**: 16,384
  - m6g.2xlarge:
    - **count**: 1
    - **vCPU_each**: 8
    - **memory_mib_each**: 32,768
    - **vCPU_total**: 8
    - **memory_mib_total**: 32,768
  - r5.xlarge:
    - **count**: 1
    - **vCPU_each**: 4
    - **memory_mib_each**: 32,768
    - **vCPU_total**: 4
    - **memory_mib_total**: 32,768
  - t3.xlarge:
    - **count**: 1
    - **vCPU_each**: 4
    - **memory_mib_each**: 16,384
    - **vCPU_total**: 4
    - **memory_mib_total**: 16,384
  - r5.large:
    - **count**: 1
    - **vCPU_each**: 2
    - **memory_mib_each**: 16,384
    - **vCPU_total**: 2
    - **memory_mib_total**: 16,384

## Amazon DynamoDB — $0.02

### Summary
- **total_tables**: 12
- **by_billing_mode**:
  - unknown: 12

## Amazon EC2 Container Registry (ECR) — $150.00

### Summary
- **total_repositories**: 120

## Amazon Elastic Compute Cloud - Compute — $4,200.50

### Summary
- **total_instances**: 160
- **total_vCPU**: 480
- **total_memory_mib**: 1,800,000
- **total_spot**: 40
- **total_on_demand**: 120
- **spot**:
  - vCPU: 140
  - memory_mib: 520,000
- **ondemand**:
  - vCPU: 340
  - memory_mib: 1,280,000
- **architecture**:
  - x86:
    - **count**: 70
    - **vCPU**: 200
    - **memory_mib**: 800,000
  - arm:
    - **count**: 90
    - **vCPU**: 280
    - **memory_mib**: 1,000,000
- **lifecycle_by_architecture**:
  - x86:
    - **spot_count**: 20
    - **on_demand_count**: 50
    - **spot_vCPU**: 80
    - **spot_memory_mib**: 320,000
    - **on_demand_vCPU**: 120
    - **on_demand_memory_mib**: 480,000
  - arm:
    - **spot_count**: 20
    - **on_demand_count**: 70
    - **spot_vCPU**: 60
    - **spot_memory_mib**: 200,000
    - **on_demand_vCPU**: 220
    - **on_demand_memory_mib**: 800,000

## Amazon Elastic Container Service — $0.00

### Summary
- **total_clusters**: 8

## Amazon Elastic Container Service for Kubernetes — $90.50

### Summary
- **total_clusters**: 2

## Amazon Elastic File System — $70.12

### Summary
- **total_file_systems**: 15
- **by_throughput_mode**:
  - bursting:
    - **count**: 15
    - **total_size_bytes**: 200,000,000,000

## Amazon Elastic Load Balancing — $300.10

### Summary
- **classic**: 0
- **alb_nlb**: 6
- **total**: 6

## Amazon ElastiCache — $900.25

### Summary
- **total_clusters**: 80
- **by_engine**:
  - redis: 60
  - valkey: 20
- **total_nodes**: 80
- **total_vCPU**: 160
- **total_memory_mib**: 294,912
- **by_instance_type**:
  - t3.micro:
    - **count**: 40
    - **vCPU_each**: 2
    - **memory_mib_each**: 1,024
    - **vCPU_total**: 80
    - **memory_mib_total**: 40,960
  - t3.small:
    - **count**: 20
    - **vCPU_each**: 2
    - **memory_mib_each**: 2,048
    - **vCPU_total**: 40
    - **memory_mib_total**: 40,960
  - r5.large:
    - **count**: 10
    - **vCPU_each**: 2
    - **memory_mib_each**: 16,384
    - **vCPU_total**: 20
    - **memory_mib_total**: 163,840
  - t3.medium:
    - **count**: 8
    - **vCPU_each**: 2
    - **memory_mib_each**: 4,096
    - **vCPU_total**: 16
    - **memory_mib_total**: 32,768
  - m5.large:
    - **count**: 2
    - **vCPU_each**: 2
    - **memory_mib_each**: 8,192
    - **vCPU_total**: 4
    - **memory_mib_total**: 16,384

## Amazon OpenSearch Service — $120.50

### Summary
- **total_domains**: 4
- **total_nodes**: 6
- **total_vCPU**: 12
- **total_memory_mib**: 20,000
- **by_instance_type**:
  - t3.small:
    - **count**: 2
    - **vCPU_each**: 2
    - **memory_mib_each**: 2,048
    - **vCPU_total**: 4
    - **memory_mib_total**: 4,096
  - t3.medium:
    - **count**: 4
    - **vCPU_each**: 2
    - **memory_mib_each**: 4,096
    - **vCPU_total**: 8
    - **memory_mib_total**: 16,384

## Amazon Relational Database Service — $950.75

### Summary
- **total_instances**: 10
- **total_allocated_storage_gib**: 4,000
- **total_vCPU**: 30
- **total_memory_mib**: 100,000
- **by_engine**:
  - mysql: 4
  - postgres: 4
  - docdb: 2
- **by_class**:
  - db.t4g.micro: 2
  - db.t4g.small: 3
  - db.t4g.medium: 2
  - db.m8g.xlarge: 1
  - db.m6g.2xlarge: 1
  - db.r8g.xlarge: 1
  - db.t4g.xlarge: 0
  - db.r5.large: 0
  - db.t3.medium: 1

## Amazon Route 53 — $12.34

### Summary
- **total_hosted_zones**: 10
- **by_type**:
  - public: 7
  - private: 3

## Amazon Simple Email Service — $8.50

### Summary
- **total_identities**: 6

## Amazon Simple Notification Service — $2.10

### Summary
- **total_topics**: 6

## Amazon Simple Queue Service — $1.50

### Summary
- **total_queues**: 10

## Amazon Simple Storage Service — $420.00

### Summary
- **total_buckets**: 60

## Amazon Virtual Private Cloud — $120.00

### Summary
- **total_vpcs**: 3
- **total_subnets**: 100
- **total_nat_gateways**: 2
- **total_internet_gateways**: 3
- **total_route_tables**: 30
- **total_vpc_endpoints**: 5
- **total_security_groups**: 400

## AmazonCloudWatch — $45.00
- Note: In-depth analysis not supported yet

## AWS Backup — $0.20
- Note: In-depth analysis not supported yet

## AWS CloudTrail — $0.00
- Note: In-depth analysis not supported yet

## AWS Cost Explorer — $0.01
- Note: In-depth analysis not supported yet

## AWS Direct Connect — $15.00

### Summary
- **total_connections**: 1

## AWS Glue — $0.00
- Note: In-depth analysis not supported yet

## AWS Key Management Service — $5.00

### Summary
- **total_keys**: 12

## AWS Lambda — $25.00

### Summary
- **total_functions**: 12
- **total_memory_mb**: 1,600
- **by_runtime**:
  - python3.11: 2
  - nodejs18.x: 4
  - nodejs16.x: 1
  - python3.10: 2
  - go1.x: 1
  - java11: 2
- **by_memory_mb**:
  - 128: 8
  - 256: 4

## AWS Secrets Manager — $0.00
- Note: In-depth analysis not supported yet

## AWS Support (Business) — $200.00
- Note: In-depth analysis not supported yet

## AWS Systems Manager — $0.00
- Note: In-depth analysis not supported yet

## AWS X-Ray — $0.00
- Note: In-depth analysis not supported yet

## CloudWatch Events — $0.00
- Note: In-depth analysis not supported yet

## EC2 - Other — $1,100.00

### Summary
- **total_volumes**: 120
- **total_snapshots**: 3,000
- **total_volume_gib**: 800

## Savings Plans for AWS Compute usage — $300.00
- Note: In-depth analysis not supported yet

