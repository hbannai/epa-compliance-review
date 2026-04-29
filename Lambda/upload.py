"""
EPA Compliance Report - Upload Handler
Generates S3 presigned URLs and creates DynamoDB tracking records.
"""
import json
import boto3
import uuid
import os
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['REPORTS_TABLE'])
BUCKET = os.environ['DOCUMENTS_BUCKET']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'POST,OPTIONS'
}


def handler(event, context):
    # Handle CORS preflight
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    try:
        body = json.loads(event['body'])
        report_id = str(uuid.uuid4())
        file_name = body.get('fileName', 'document.pdf')
        file_type = body.get('fileType', 'application/pdf')
        s3_key = f"uploads/{report_id}/{file_name}"

        # Generate presigned upload URL
        presigned_url = s3.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': BUCKET,
                'Key': s3_key,
                'ContentType': file_type
            },
            ExpiresIn=3600
        )

        # Create tracking record in DynamoDB
        table.put_item(Item={
            'reportId': report_id,
            'fileName': file_name,
            's3Key': s3_key,
            'status': 'UPLOADED',
            'submittedAt': datetime.utcnow().isoformat(),
            'submitterName': body.get('submitterName', 'Anonymous'),
            'submitterEmail': body.get('submitterEmail', ''),
            'facilityName': body.get('facilityName', ''),
            'reportType': body.get('reportType', 'general'),
            'description': body.get('description', ''),
            'aiReview': {},
            'humanReview': {}
        })

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'reportId': report_id,
                'uploadUrl': presigned_url,
                'message': 'Upload URL generated successfully.'
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
