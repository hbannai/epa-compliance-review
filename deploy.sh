#!/bin/bash
# ============================================================
# EPA Compliance Review System - Deploy Script
# ============================================================
# Usage: ./deploy.sh [aws-region] [stack-name]
# Example: ./deploy.sh us-east-1 epa-compliance-review
#
# Everything is self-contained in template.yaml:
# - Lambda code inline (ZipFile)
# - Frontend auto-deployed to S3 (Custom Resource)
# - API URL auto-injected into frontend
# - CORS handled via MOCK integration
# - S3 trigger for bulk upload auto-analysis
# ============================================================

set -e

REGION="${1:-us-east-1}"
STACK_NAME="${2:-epa-compliance-review}"

echo "=========================================="
echo "  EPA Compliance Review System - Deploy"
echo "=========================================="
echo "  Region:  $REGION"
echo "  Stack:   $STACK_NAME"
echo "=========================================="

# ---- Step 1: Deploy CloudFormation stack ----
echo ""
echo "[1/2] Deploying CloudFormation stack..."
echo "  (Creates all 33 resources + auto-deploys frontend)"
aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --capabilities CAPABILITY_NAMED_IAM \
    --parameter-overrides \
        ProjectName="$STACK_NAME" \
    --no-fail-on-empty-changeset

# ---- Step 2: Get outputs ----
echo ""
echo "[2/2] Retrieving stack outputs..."
API_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' \
    --output text)

WEBSITE_URL=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`WebsiteUrl`].OutputValue' \
    --output text)

DOCS_BUCKET=$(aws cloudformation describe-stacks \
    --stack-name "$STACK_NAME" \
    --region "$REGION" \
    --query 'Stacks[0].Outputs[?OutputKey==`DocumentsBucketName`].OutputValue' \
    --output text)

echo ""
echo "=========================================="
echo "  DEPLOYMENT COMPLETE!"
echo "=========================================="
echo ""
echo "  Portal URL:   $WEBSITE_URL"
echo "  API URL:      $API_URL (auto-configured)"
echo "  Docs Bucket:  $DOCS_BUCKET"
echo ""
echo "  Open the Portal URL - everything is ready!"
echo ""
echo "  To bulk-upload sample files for testing:"
echo "  aws s3 cp sample-reports/ s3://$DOCS_BUCKET/uploads/ --recursive"
echo ""
echo "  Prerequisite: Enable Mistral in Bedrock:"
echo "  https://console.aws.amazon.com/bedrock/home#/modelaccess"
echo ""
echo "  NOTE: CloudFront may take 3-5 min to deploy."
echo "=========================================="
