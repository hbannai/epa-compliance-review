"""
EPA Compliance Report - Review Dashboard API
Supports listing flagged reports, viewing details, and recording
human reviewer decisions (APPROVE / DENY / ESCALATE).
"""
import json
import boto3
import os
from datetime import datetime
from boto3.dynamodb.conditions import Key

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['REPORTS_TABLE'])

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,PUT,OPTIONS'
}


def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    method = event.get('httpMethod', 'GET')
    params = event.get('queryStringParameters') or {}

    try:
        # ---- GET: list reports by status ----
        if method == 'GET' and 'reportId' not in params:
            status_filter = params.get('status', 'FLAGGED_FOR_REVIEW')

            if status_filter == 'ALL':
                response = table.scan()
            else:
                response = table.query(
                    IndexName='status-submittedAt-index',
                    KeyConditionExpression=Key('status').eq(status_filter)
                )

            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps({'reports': response.get('Items', [])}, default=str)
            }

        # ---- GET: single report detail ----
        elif method == 'GET' and 'reportId' in params:
            item = table.get_item(Key={'reportId': params['reportId']}).get('Item', {})
            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps({'report': item}, default=str)
            }

        # ---- PUT: record reviewer decision ----
        elif method == 'PUT':
            body = json.loads(event['body'])
            report_id = body['reportId']
            decision = body['decision']       # APPROVED | DENIED | ESCALATED
            reviewer_notes = body.get('notes', '')
            reviewer_name = body.get('reviewerName', 'Unknown')

            table.update_item(
                Key={'reportId': report_id},
                UpdateExpression='SET #s = :s, humanReview = :hr, reviewedAt = :t',
                ExpressionAttributeNames={'#s': 'status'},
                ExpressionAttributeValues={
                    ':s': f'HUMAN_{decision}',
                    ':hr': {
                        'decision': decision,
                        'notes': reviewer_notes,
                        'reviewerName': reviewer_name,
                        'reviewedAt': datetime.utcnow().isoformat()
                    },
                    ':t': datetime.utcnow().isoformat()
                }
            )

            return {
                'statusCode': 200,
                'headers': CORS_HEADERS,
                'body': json.dumps({
                    'reportId': report_id,
                    'status': f'HUMAN_{decision}',
                    'message': f'Report {decision.lower()} by {reviewer_name}'
                })
            }

        return {
            'statusCode': 400,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': 'Invalid request'})
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
