# Terraform Bad Practices

## Security Risks

### Hardcoded Secrets
Storing passwords, API keys, or credentials directly in .tf files (instead of secrets managers like Vault or environment variables).

### Unrestricted IAM Policies
Overly permissive aws_iam_policy rules (e.g., "Resource": "*").

### Publicly Accessible Storage
Exposing Terraform state files in public S3 buckets or unencrypted storage.

### Sensitive Outputs
Printing secrets to console/outputs via output blocks without sensitive = true.

## Reliability & Stability

### Missing State Locking
Not enabling state locking (e.g., DynamoDB for S3 backends), risking state corruption.

### Fragile Dependencies
Using depends_on incorrectly or relying on implicit resource timing.

### No Lifecycle Rules
Ignoring lifecycle blocks for critical resources (e.g., prevent_destroy = true).

### Unpinned Versions
Floating provider/module versions (~> 3.0 instead of = 3.1.0), causing drift.


## Cost Efficiency

### Over-Provisioned Resources
Using oversized instances (e.g., m5.24xlarge for non-critical workloads).

### Orphaned Resources
Failing to destroy test resources or dangling volumes after terraform destroy.

### Non-Usage of Auto-Scaling
Static resource counts instead of autoscaling groups.

## Maintainability & Collaboration

### Monolithic Configurations
Giant main.tf files instead of modularized code.

### Lack of Variables/Validation
Hardcoding values (e.g., AMI IDs, regions) instead of using variables with validation.

### Poor State Management
Local state files (backend "local") hindering team collaboration.

### Undocumented Code
Missing descriptions for variables/modules/resources.

## Performance & Scalability

### Large Single State Files
Managing hundreds of resources in one state file, slowing operations.

### Unoptimized Loops/Counts
Overusing count/for_each with complex logic, increasing plan/apply times.

### No Workspace/Environment Isolation
Mixing dev/prod in one configuration without workspaces or directory separation.

## Operational Negligence

### Manual Drift Creation
Modifying resources outside Terraform (e.g., AWS Console), causing state drift.

### Disabled Plan Confirmation
Running terraform apply -auto-approve in CI/CD without manual review.

### Ignoring Plan Output
Not inspecting terraform plan before apply.