"""
EPA Compliance Report - AI Analysis Handler
Extracts text from documents via Textract, then runs compliance analysis
through Amazon Bedrock (Mistral) against 18 EPA compliance checkpoints.
"""
import json
import boto3
import os
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
bedrock = boto3.client('bedrock-runtime')
textract = boto3.client('textract')
table = dynamodb.Table(os.environ['REPORTS_TABLE'])
BUCKET = os.environ['DOCUMENTS_BUCKET']
MODEL_ID = os.environ['BEDROCK_MODEL_ID']

CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'POST,OPTIONS'
}

# ============================================================
# EPA COMPLIANCE ANALYSIS PROMPT
# Based on https://www.epa.gov/compliance/monitoring-compliance
# ============================================================
EPA_COMPLIANCE_PROMPT = """You are an EPA Office of Water compliance analyst AI.
Analyze the submitted document against EPA compliance monitoring regulations.

CHECK EACH OF THESE 18 COMPLIANCE AREAS. Rate each as:
  COMPLIANT | NON_COMPLIANT | NEEDS_REVIEW | INSUFFICIENT_DATA

=== CLEAN WATER ACT (CWA) COMPLIANCE ===
1. NPDES_PERMIT: Discharge monitoring reports (DMRs), effluent limitations, permit conditions
2. WATER_QUALITY_STANDARDS: Pollutant concentrations vs. EPA water quality criteria
3. DISCHARGE_REPORTING: Completeness of discharge monitoring data & reporting frequency
4. PRETREATMENT_STANDARDS: Industrial pretreatment program compliance

=== SAFE DRINKING WATER ACT (SDWA) COMPLIANCE ===
5. MAX_CONTAMINANT_LEVELS: Reported contaminant levels vs. EPA MCL standards
6. MONITORING_REPORTING: Required monitoring schedules & public notification
7. TREATMENT_TECHNIQUES: Compliance with required treatment technologies

=== EFFLUENT & DISCHARGE COMPLIANCE ===
8. EFFLUENT_LIMITATIONS: Industry-specific effluent limitation guidelines (ELGs)
9. TMDL_COMPLIANCE: Total Maximum Daily Load allocations
10. STORMWATER_MGMT: Stormwater pollution prevention plan (SWPPP) compliance

=== FACILITY & OPERATIONAL COMPLIANCE ===
11. RECORD_KEEPING: Required records maintained and accessible
12. SELF_MONITORING: Facility self-monitoring data completeness & accuracy
13. SPILL_PREVENTION: Spill Prevention, Control & Countermeasure (SPCC) plan
14. BEST_MGMT_PRACTICES: Implementation of required BMPs

=== REPORTING & TRANSPARENCY ===
15. TIMELY_REPORTING: Reports submitted within regulatory deadlines
16. DATA_ACCURACY: Inconsistencies, anomalies, or suspicious data patterns
17. PUBLIC_NOTIFICATION: Compliance with public notification requirements
18. CORRECTIVE_ACTIONS: Corrective action plans for prior violations

For each area provide:
  - status: COMPLIANT | NON_COMPLIANT | NEEDS_REVIEW | INSUFFICIENT_DATA
  - evidence: specific text/data from the document
  - risk_level: LOW | MEDIUM | HIGH | CRITICAL
  - recommendation: what action the reviewer should take

Also provide:
  - overall_risk_score: integer 1-100 (100 = highest risk; flag >70 for immediate review)
  - priority_flag: ROUTINE | ELEVATED | URGENT | CRITICAL
  - summary: 2-3 sentence executive summary
  - key_violations: list of specific violations found
  - recommended_actions: list of recommended next steps

RESPOND IN VALID JSON ONLY. No markdown fences.

=== DOCUMENT CONTENT ===
{document_text}
"""


def extract_text(bucket, key):
    """Extract text from uploaded document."""
    try:
        if key.lower().endswith(('.txt', '.csv')):
            obj = s3.get_object(Bucket=bucket, Key=key)
            return obj['Body'].read().decode('utf-8')
        else:
            resp = textract.detect_document_text(
                Document={'S3Object': {'Bucket': bucket, 'Name': key}}
            )
            lines = [b.get('Text', '') for b in resp.get('Blocks', []) if b['BlockType'] == 'LINE']
            return '\n'.join(lines)
    except Exception as e:
        return f"[Text extraction error: {e}]"


def invoke_mistral(document_text):
    """Send document to Mistral via Bedrock for compliance analysis."""
    prompt = EPA_COMPLIANCE_PROMPT.format(document_text=document_text[:50000])

    response = bedrock.invoke_model(
        modelId=MODEL_ID,
        contentType='application/json',
        accept='application/json',
        body=json.dumps({
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 4096,
            "temperature": 0.1
        })
    )

    result = json.loads(response['body'].read())
    content = result.get('choices', [{}])[0].get('message', {}).get('content', '')

    # Parse JSON from response
    try:
        if '```json' in content:
            content = content.split('```json')[1].split('```')[0]
        elif '```' in content:
            content = content.split('```')[1].split('```')[0]
        return json.loads(content.strip())
    except json.JSONDecodeError:
        return {"raw_analysis": content, "parse_error": True}


def handler(event, context):
    if event.get('httpMethod') == 'OPTIONS':
        return {'statusCode': 200, 'headers': CORS_HEADERS, 'body': ''}

    try:
        body = json.loads(event['body'])
        report_id = body['reportId']

        # Fetch report metadata
        report = table.get_item(Key={'reportId': report_id})['Item']

        # Mark as analyzing
        table.update_item(
            Key={'reportId': report_id},
            UpdateExpression='SET #s = :s',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={':s': 'ANALYZING'}
        )

        # Extract text from document
        document_text = extract_text(BUCKET, report['s3Key'])

        # Run Mistral compliance analysis
        ai_review = invoke_mistral(document_text)

        # Determine status from risk score
        risk_score = ai_review.get('overall_risk_score', 50)
        priority = ai_review.get('priority_flag', 'ROUTINE')

        if risk_score > 70 or priority in ('URGENT', 'CRITICAL'):
            new_status = 'FLAGGED_FOR_REVIEW'
        elif risk_score > 40 or priority == 'ELEVATED':
            new_status = 'NEEDS_REVIEW'
        else:
            new_status = 'AI_APPROVED'

        # Persist analysis results
        table.update_item(
            Key={'reportId': report_id},
            UpdateExpression='SET #s = :s, aiReview = :ai, analyzedAt = :t, riskScore = :r',
            ExpressionAttributeNames={'#s': 'status'},
            ExpressionAttributeValues={
                ':s': new_status,
                ':ai': ai_review,
                ':t': datetime.utcnow().isoformat(),
                ':r': risk_score
            }
        )

        return {
            'statusCode': 200,
            'headers': CORS_HEADERS,
            'body': json.dumps({
                'reportId': report_id,
                'status': new_status,
                'riskScore': risk_score,
                'priority': priority,
                'analysis': ai_review
            }, default=str)
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'headers': CORS_HEADERS,
            'body': json.dumps({'error': str(e)})
        }
