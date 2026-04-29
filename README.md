# 🌍 EPA Office of Water — Compliance Report Portal

**AI-Powered Citizen Compliance Report Submission & Automated Review System**

Citizens upload compliance documents → Amazon Bedrock (Mistral AI) checks them against **18 EPA regulations** → Color-coded risk scores → Engineers Approve / Deny / Escalate.

> **Fully self-contained `template.yaml`** — Lambda code inline, frontend auto-deployed, API URL auto-configured, CORS handled. Deploy and open.

---

## 🚀 Deployment (3 Options)

### Prerequisite (all options)

Enable **Mistral Large** in Bedrock → [Model Access Console](https://console.aws.amazon.com/bedrock/home#/modelaccess)

### Option 1: Deploy Script (Recommended)

```bash
git clone https://github.com/your-org/epa-compliance-review.git
cd epa-compliance-review
chmod +x deploy.sh
./deploy.sh us-east-1
```

### Option 2: AWS CLI

```bash
aws cloudformation deploy \
    --template-file template.yaml \
    --stack-name epa-compliance-review \
    --region us-east-1 \
    --capabilities CAPABILITY_NAMED_IAM

aws cloudformation describe-stacks --stack-name epa-compliance-review \
    --query 'Stacks[0].Outputs[*].[OutputKey,OutputValue]' --output table
```

### Option 3: AWS Console (Step-by-Step)

1. Go to [CloudFormation Console](https://console.aws.amazon.com/cloudformation)
2. **Create Stack** → **With new resources** → **Upload a template file** → pick `template.yaml`
3. Stack name: `epa-compliance-review` → leave parameters as defaults → **Next** → **Next**
4. ☑️ Check **I acknowledge that AWS CloudFormation might create IAM resources with custom names**
5. Click **Submit** → wait for **CREATE_COMPLETE** (~5-8 min)
6. Click **Outputs** tab → open **WebsiteUrl** → done!

> No S3 uploads, no zip packaging, no API URL to paste. Everything is automatic.

---

## 🧪 Testing

### Quick Test (1 file via portal)

1. Open the **WebsiteUrl** from CloudFormation Outputs
2. Fill in Name, Email, Facility → select Report Type
3. Upload any file from `sample-reports/` folder
4. Click **Submit for AI Review** → wait 30-60 seconds
5. See risk score + color-coded status + violations

### Bulk Test (30 files via S3)

Upload all sample files directly to S3 — they auto-trigger Mistral analysis:

**Via CLI:**
```bash
aws s3 cp sample-reports/ s3://epa-compliance-review-docs-YOUR_ACCOUNT_ID/uploads/ --recursive
```

**Via S3 Console:**
1. Go to [S3 Console](https://console.aws.amazon.com/s3)
2. Open **`epa-compliance-review-docs-ACCOUNT_ID`** bucket
3. Open (or create) the **`uploads/`** folder
4. Click **Upload** → **Add files** → select all 30 sample files → **Upload**

Then open the portal → **Review Dashboard** → ✅ **Auto-refresh (10s)** → watch reports appear with color-coded scores.

### 30 Sample Test Files

| Files | Expected Result | What They Test |
|:-----:|:---:|---|
| `01-07` + `21-23` | 🔴 **FLAGGED** (score >70) | Mercury violations, E. coli crisis, illegal dumping, falsified data, fuel spills, no SWPPP, cyanide discharge, biosolids near school, wetlands destruction, thermal fish kill |
| `08-13` + `24-26` | 🟠 **NEEDS REVIEW** (score 41-70) | Late DMR, incomplete monitoring, minor TMDL exceedance, outdated BMPs, expired permit, late public notice, sewer overflow, lapsed lab cert, nutrient trading discrepancy |
| `14-20` + `27-30` | 🟢 **AI APPROVED** (score ≤40) | Model WWTP, drinking water excellence, industrial pretreatment, stormwater SWPPP, SPCC plan, corrective action complete, FCE clean inspection, water reuse, watershed monitoring, emergency drill, permit renewal |

### Review Dashboard Test

1. Click **Review Dashboard** tab (auto-loads all reports)
2. Click filter buttons: 🔴 Flagged → 🟠 Review → 🟢 Approved → All
3. Click any report → see 18-checkpoint breakdown with evidence
4. Enter reviewer name + notes → **✅ Approve**, **❌ Deny**, or **⚠️ Escalate**

---

## 🏗️ Architecture (33 Resources)

```
  Portal Upload          Bulk S3 Upload
       │                      │
       ▼                      ▼
  ┌──────────┐    ┌─────────────────────┐
  │CloudFront│    │ S3 Docs Bucket      │
  │→ S3 Web  │    │ uploads/ → trigger  │
  └────┬─────┘    └──────────┬──────────┘
       │                     │
       ▼                     ▼
  ┌─────────────┐    ┌──────────────┐
  │ API Gateway │    │ AutoAnalyze  │
  │ /upload     │    │ Lambda       │
  │ /analyze    │    │ (S3 trigger) │
  │ /review     │    └──────┬───────┘
  └──┬──┬──┬────┘           │
     │  │  │                │
     ▼  ▼  ▼                ▼
  ┌──────┐ ┌───────┐  ┌──────────┐
  │Upload│ │Analyze│  │ Bedrock  │
  │Lambda│ │Lambda │  │ Mistral  │
  └──┬───┘ └──┬────┘  └──────────┘
     │        │
     ▼        ▼
  ┌──────┐ ┌──────────┐
  │S3 Put│ │ DynamoDB  │
  │Docs  │ │ Reports   │
  └──────┘ └──────────┘
```

### Key Features in the Template

| Feature | How |
|---------|-----|
| Lambda code inline | `ZipFile` — no external S3 bucket needed |
| Frontend auto-deployed | Custom Resource writes HTML to S3 |
| API URL auto-configured | Injected into HTML during deployment |
| CORS properly handled | OPTIONS methods use MOCK integration (not Lambda) |
| S3 bulk upload trigger | `AutoAnalyzeFunction` triggered by S3 events on `uploads/` |
| Auto-refresh dashboard | 10-second polling toggle on Review tab |
| Color-coded risk scores | 🔴 >70 / 🟠 41-70 / 🟢 ≤40 |

---

## 🔍 18 EPA Compliance Checks

Based on [EPA Compliance Monitoring](https://www.epa.gov/compliance/monitoring-compliance):

| Category | Checks |
|----------|--------|
| **Clean Water Act** | NPDES Permits, Water Quality, Discharge Reporting, Pretreatment |
| **Safe Drinking Water Act** | Max Contaminant Levels, Monitoring & Reporting, Treatment Techniques |
| **Effluent & Discharge** | Effluent Limitations, TMDL Compliance, Stormwater Management |
| **Facility & Operations** | Record Keeping, Self-Monitoring, Spill Prevention, Best Practices |
| **Reporting & Transparency** | Timely Reporting, Data Accuracy, Public Notification, Corrective Actions |

---

## 📁 Project Structure

```
epa-compliance-review/
├── template.yaml           # Self-contained CFN (33 resources, all code inline)
├── deploy.sh               # One-command deploy
├── README.md               # This file
├── TESTING-GUIDE.md        # Detailed testing walkthrough + flagging logic
├── .gitignore
├── sample-reports/          # 30 test documents
│   ├── 01-FLAGGED-*.txt    # 10 high-risk files (score >70)
│   ├── 08-REVIEW-*.txt     # 9 medium-risk files (score 41-70)
│   └── 14-COMPLIANT-*.txt  # 11 low-risk files (score ≤40)
├── lambda/                 # Readable source copies (deployed code is inline)
│   ├── upload.py
│   ├── analyze.py
│   └── review.py
└── frontend/               # Readable source copies (deployed via Custom Resource)
    ├── index.html
    ├── index-compact.html
    └── error.html
```

---

## 🗑️ Cleanup

```bash
STACK_NAME="epa-compliance-review"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
aws s3 rm s3://${STACK_NAME}-docs-${ACCOUNT_ID} --recursive
aws s3 rm s3://${STACK_NAME}-web-${ACCOUNT_ID} --recursive
aws cloudformation delete-stack --stack-name "$STACK_NAME"
```

---

## 📤 Upload to GitHub

```bash
# 1. Create a new repo on GitHub (don't initialize with README)

# 2. In your local project folder:
cd epa-compliance-system
git init
git add .
git commit -m "EPA Compliance Report Portal - Bedrock Mistral AI Review System"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/epa-compliance-review.git
git push -u origin main
```

Or via **GitHub Desktop**: File → Add Local Repository → select the folder → Publish.

---

## ⚠️ Demo Notes

- Enable **Mistral Large** in Bedrock before first use
- CloudFront takes 3-5 min to deploy — wait if URL gives error
- For production: add Cognito auth, WAF, VPC, tighter CORS
- Two upload paths: portal form (citizens) + S3 direct (bulk)

## 📜 License

Demo project. EPA rules from [EPA Compliance Monitoring](https://www.epa.gov/compliance/monitoring-compliance).
