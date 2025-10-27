"""Analyzers package for aws_resources

This module registers built-in analyzers on import. Additional analyzers can be
registered by calling `register_analyzer(service_token, factory)` from
`aws_resources.analyzers.registry`.
"""

from .registry import get_analyzer_for_service, register_analyzer

# Import built-in analyzers so they can be registered
from .ec2 import EC2Analyzer
from .rds import RDSAnalyzer
from .s3 import S3Analyzer
from .cloudfront import CloudFrontAnalyzer
from .dynamodb import DynamoDBAnalyzer
from .ecr import ECRAnalyzer
from .ecs import ECSAnalyzer
from .eks import EKSAnalyzer
from .efs import EFSAnalyzer
from .elb import ELBAnalyzer
from .elasticache import ElastiCacheAnalyzer
from .opensearch import OpenSearchAnalyzer
from .route53 import Route53Analyzer
from .ses import SESAnalyzer
from .sns import SNSAnalyzer
from .sqs import SQSAnalyzer
from .directconnect import DirectConnectAnalyzer
from .kms import KMSAnalyzer
from .ec2_other import EC2OtherAnalyzer
from .documentdb import DocumentDBAnalyzer

# Register EC2 analyzer for the Cost Explorer service token used by AWS
register_analyzer("Amazon Elastic Compute Cloud - Compute", lambda profile=None, region_name=None: EC2Analyzer(profile=profile, region_name=region_name))
# Register RDS analyzer
register_analyzer("Amazon Relational Database Service", lambda profile=None, region_name=None: RDSAnalyzer(profile=profile, region_name=region_name))
# Register VPC analyzers for common Cost Explorer tokens
from .vpc import VPCAnalyzer
register_analyzer("Amazon VPC", lambda profile=None, region_name=None: VPCAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon Virtual Private Cloud", lambda profile=None, region_name=None: VPCAnalyzer(profile=profile, region_name=region_name))
# Register S3
register_analyzer("Amazon Simple Storage Service", lambda profile=None, region_name=None: S3Analyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon S3", lambda profile=None, region_name=None: S3Analyzer(profile=profile, region_name=region_name))
# Register CloudFront
register_analyzer("Amazon CloudFront", lambda profile=None, region_name=None: CloudFrontAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon CloudFront (Amazon)", lambda profile=None, region_name=None: CloudFrontAnalyzer(profile=profile, region_name=region_name))
# Register DynamoDB
register_analyzer("Amazon DynamoDB", lambda profile=None, region_name=None: DynamoDBAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon DynamoDB (Amazon)", lambda profile=None, region_name=None: DynamoDBAnalyzer(profile=profile, region_name=region_name))
# Register ECR
register_analyzer("Amazon Elastic Container Registry", lambda profile=None, region_name=None: ECRAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon ECR", lambda profile=None, region_name=None: ECRAnalyzer(profile=profile, region_name=region_name))
# Some Cost Explorer reports use alternate service name variants; add them too
register_analyzer("Amazon EC2 Container Registry (ECR)", lambda profile=None, region_name=None: ECRAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon Elastic Container Registry (ECR)", lambda profile=None, region_name=None: ECRAnalyzer(profile=profile, region_name=region_name))
# Register ECS
register_analyzer("Amazon Elastic Container Service", lambda profile=None, region_name=None: ECSAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon ECS", lambda profile=None, region_name=None: ECSAnalyzer(profile=profile, region_name=region_name))
# Register EKS
register_analyzer("Amazon Elastic Kubernetes Service", lambda profile=None, region_name=None: EKSAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon EKS", lambda profile=None, region_name=None: EKSAnalyzer(profile=profile, region_name=region_name))
# Some Cost Explorer tokens label EKS differently
register_analyzer("Amazon Elastic Container Service for Kubernetes", lambda profile=None, region_name=None: EKSAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon Elastic Container Service for Kubernetes (EKS)", lambda profile=None, region_name=None: EKSAnalyzer(profile=profile, region_name=region_name))
# Register EFS
register_analyzer("Amazon Elastic File System", lambda profile=None, region_name=None: EFSAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon EFS", lambda profile=None, region_name=None: EFSAnalyzer(profile=profile, region_name=region_name))
# Register ELB/ALB/NLB
register_analyzer("Amazon Elastic Load Balancing", lambda profile=None, region_name=None: ELBAnalyzer(profile=profile, region_name=region_name))
register_analyzer("AWS Elastic Load Balancing", lambda profile=None, region_name=None: ELBAnalyzer(profile=profile, region_name=region_name))
# Register ElastiCache
register_analyzer("Amazon ElastiCache", lambda profile=None, region_name=None: ElastiCacheAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon ElastiCache (Amazon)", lambda profile=None, region_name=None: ElastiCacheAnalyzer(profile=profile, region_name=region_name))
# Register OpenSearch / Elasticsearch
register_analyzer("Amazon OpenSearch Service", lambda profile=None, region_name=None: OpenSearchAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon Elasticsearch", lambda profile=None, region_name=None: OpenSearchAnalyzer(profile=profile, region_name=region_name))
# Register Route53
register_analyzer("Amazon Route 53", lambda profile=None, region_name=None: Route53Analyzer(profile=profile, region_name=region_name))
# Register SES
register_analyzer("Amazon Simple Email Service", lambda profile=None, region_name=None: SESAnalyzer(profile=profile, region_name=region_name))
# Register SNS
register_analyzer("Amazon Simple Notification Service", lambda profile=None, region_name=None: SNSAnalyzer(profile=profile, region_name=region_name))
# Register SQS
register_analyzer("Amazon Simple Queue Service", lambda profile=None, region_name=None: SQSAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon SQS", lambda profile=None, region_name=None: SQSAnalyzer(profile=profile, region_name=region_name))
# Register Direct Connect
register_analyzer("AWS Direct Connect", lambda profile=None, region_name=None: DirectConnectAnalyzer(profile=profile, region_name=region_name))
# Register KMS
register_analyzer("AWS Key Management Service", lambda profile=None, region_name=None: KMSAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon Key Management Service", lambda profile=None, region_name=None: KMSAnalyzer(profile=profile, region_name=region_name))
# Register EC2 - Other
register_analyzer("EC2 - Other", lambda profile=None, region_name=None: EC2OtherAnalyzer(profile=profile, region_name=region_name))
register_analyzer("Amazon EC2 - Other", lambda profile=None, region_name=None: EC2OtherAnalyzer(profile=profile, region_name=region_name))

# Register DocumentDB (cost explorer shows the long service name in some reports)
# This one I coment out because it overlaps with RDS analyzer
#register_analyzer("Amazon DocumentDB (with MongoDB compatibility)", lambda profile=None, region_name=None: DocumentDBAnalyzer(profile=profile, region_name=region_name))
#register_analyzer("Amazon DocumentDB", lambda profile=None, region_name=None: DocumentDBAnalyzer(profile=profile, region_name=region_name))

# Import the module named `lambda` using importlib because `lambda` is a
# Python keyword and `from .lambda import ...` is a syntax error. We import the
# module dynamically and extract `LambdaAnalyzer`.
import importlib
_lambda_mod = importlib.import_module(f"{__name__}.lambda")
LambdaAnalyzer = getattr(_lambda_mod, "LambdaAnalyzer")
register_analyzer("AWS Lambda", lambda profile=None, region_name=None: LambdaAnalyzer(profile=profile, region_name=region_name))
register_analyzer("AWS Lambda (Amazon)", lambda profile=None, region_name=None: LambdaAnalyzer(profile=profile, region_name=region_name))

__all__ = ["get_analyzer_for_service", "register_analyzer"]
