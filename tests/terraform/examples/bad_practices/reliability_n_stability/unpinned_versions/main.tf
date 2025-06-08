# versions.tf (Bad Practice)
terraform {
  required_providers {
    # Floating provider versions
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"  # Too broad - allows any 4.x version
    }
    
    # Completely unpinned provider
    azurerm = {
      source  = "hashicorp/azurerm"
      # No version specified!
    }
  }

  # Unpinned Terraform version
  required_version = ">= 1.0"  # Allows any 1.x version
}

# main.tf
provider "aws" {
  region = "us-east-1"
}

provider "azurerm" {
  features {}
}

# Module with floating version
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 3.0"  # Accepts any 3.x version

  name = "my-vpc"
  cidr = "10.0.0.0/16"
  
  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]
}

# Module from GitHub main branch (always changing)
module "unstable_module" {
  source = "github.com/example/terraform-azure-frontdoor?ref=main"
  
  resource_group_name = "frontdoor-rg"
}

# Resource using provider with potential breaking changes
resource "aws_s3_bucket" "data" {
  bucket = "my-unique-bucket-name-12345"  # Change to globally unique name
}

# Resource depending on Azure provider's latest changes
resource "azurerm_storage_account" "example" {
  name                     = "examplestorageacc"
  resource_group_name      = "example-resources"
  location                 = "West Europe"
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

# Using new provider feature without version constraint
resource "aws_iam_user" "new_feature_user" {
  name = "user"
  
  # This tags argument was added in aws provider v4.7.0
  tags = {
    CreatedBy = "Terraform"
  }
}