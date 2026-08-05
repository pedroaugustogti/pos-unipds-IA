provider "aws" {
  region = "us-east-1"
}

resource "aws_s3_bucket" "nexus-apollo-data" {
  bucket = "nexus-apollo-data"
}

resource "aws_s3_bucket_versioning" "nexus-apollo-data" {
  bucket = aws_s3_bucket.nexus-apollo-data.id
  versioning_configuration {
    status = "Enabled"
  }
}
