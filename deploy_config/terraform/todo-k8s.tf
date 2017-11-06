/*
 Create a repo by running the following from the same dir as this file:

 $ brew install terraform
 $ terraform apply -var "repo=master/myservice" -var "access_key=REDACTED" -var "secret_key=REDACTED" .

 Keep the resulting terraform.tfstate file somewhere safe. You'll need it in the
 unlikely event you ever want to modify/delete this repo using Terraform.
*/

variable "repo" {}
variable "region" {
    default = "us-east-1"
}
variable "prod_account" {
    default = "372615401783"
}

provider "aws" {
    region     = "${var.region}"
}

// Get the AWS account ID
data "aws_caller_identity" "current" {}

// Create ECR repository
resource "aws_ecr_repository" "repo" {
  name = "${var.repo}"
}

// Allow prod to access ECR repo
data "aws_iam_policy_document" "repo-prod" {
  statement {
    sid = "Allow ofp and ofpdev"

    principals = {
      type = "AWS"
      identifiers = [
        "arn:aws:iam::${var.prod_account}:root",
        "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
      ]
    }

    actions = [
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:BatchCheckLayerAvailability",
      "ecr:PutImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:DescribeRepositories",
      "ecr:GetRepositoryPolicy",
      "ecr:ListImages",
      "ecr:DescribeImages",
    ]
  }
}

resource "aws_ecr_repository_policy" "repo-prod" {
  repository = "${aws_ecr_repository.repo.name}"
  policy     = "${data.aws_iam_policy_document.repo-prod.json}"
}


resource "aws_dynamodb_table" "todo-k8s-dynamodb-table" {
  name           = "dev-todo-k8s-todos"
  read_capacity  = 2
  write_capacity = 2
  hash_key       = "assignee"
  range_key      = "id"

  attribute {
    name = "assignee"
    type = "N"
  }

  attribute {
    name = "id"
    type = "N"
  }

  attribute {
    name = "status"
    type = "N"
  }

  global_secondary_index {
    name               = "assignee_status_index"
    hash_key           = "assignee"
    range_key          = "status"
    write_capacity     = 2
    read_capacity      = 2
    projection_type    = "ALL"
  }

  tags {
    Name        = "dev-todo-k8s-todos"
    Environment = "dev"
  }
}
