# 🧪 EPA Compliance Portal — Testing Guide

## How AI Flagging Works

When a document is uploaded, Amazon Bedrock (Mistral AI) analyzes it against **18 EPA compliance checkpoints** and assigns:

1. **A status for each checkpoint**: `COMPLIANT` | `NON_COMPLIANT` | `NEEDS_REVIEW` | `INSUFFICIENT_DATA`
2. **A risk level for each**: `LOW` | `MEDIUM` | `HIGH` | `CRITICAL`
3. **An overall risk score**: 1–100
4. **A priority flag**: `ROUTINE` | `ELEVATED` | `URGENT` | `CRITICAL`

### Flagging Rules

| Risk Score | Priority | Result | What Happens |
|:---:|:---:|:---:|---|
| **> 70** | URGENT or CRITICAL | 🔴 **FLAGGED FOR REVIEW** | Appears in Flagged queue — engineer MUST review |
| **41 – 70** | ELEVATED | 🟠 **NEEDS REVIEW** | Appears in Needs Review queue — engineer should check |
| **≤ 40** | ROUTINE | 🟢 **AI APPROVED** | Low risk — may not need human review |

---

## The 18 Compliance Checks & What Triggers Each Flag

| # | Check | 🔴 Triggers FLAGGED | 🟠 Triggers REVIEW | 🟢 Passes as COMPLIANT |
|---|-------|---|---|---|
| 1 | **NPDES Permit** | Missing permit, major exceedances (>100%) | Minor exceedances, expired permit | All limits met, permit current |
| 2 | **Water Quality Standards** | Pollutants far exceeding criteria | Borderline exceedances | All within EPA criteria |
| 3 | **Discharge Reporting** | Missing monitoring data, no DMRs filed | Late submission, partial gaps | All DMRs on time and complete |
| 4 | **Pretreatment Standards** | Toxic discharge (cyanide, heavy metals) | Minor pretreatment gaps | All SIU limits met |
| 5 | **Max Contaminant Levels** | E. coli positive, lead exceedance | Borderline MCL results | All below MCL |
| 6 | **Monitoring & Reporting** | Months of missed monitoring | One skipped test period | All schedules followed |
| 7 | **Treatment Techniques** | Treatment system offline | Equipment maintenance overdue | Systems operational |
| 8 | **Effluent Limitations** | Industry limits exceeded by >50% | Minor ELG exceedances | Within ELG limits |
| 9 | **TMDL Compliance** | Significantly over TMDL allocation | Slight overages with explanation | Within allocation |
| 10 | **Stormwater Mgmt** | No SWPPP, active sediment discharge | Outdated SWPPP, minor gaps | Current SWPPP, BMPs in place |
| 11 | **Record Keeping** | Missing/destroyed records | Incomplete records | All records maintained |
| 12 | **Self-Monitoring** | Falsified data, missing months | Gaps in monitoring schedule | Complete and accurate |
| 13 | **Spill Prevention** | Active spill + no SPCC plan | Outdated SPCC plan | Current SPCC, zero spills |
| 14 | **Best Mgmt Practices** | Zero BMPs implemented | Some BMPs missing/outdated | All BMPs in place |
| 15 | **Timely Reporting** | Reports >60 days late | Reports 1–60 days late | All submitted on time |
| 16 | **Data Accuracy** | Falsified data, duplicate entries | Inconsistencies found | Data consistent and verified |
| 17 | **Public Notification** | No notification for health threat | Late notification | Timely or not required |
| 18 | **Corrective Actions** | No corrective action for violations | Behind schedule on actions | All actions complete |

---

## 20 Sample Test Files

### 🔴 FLAGGED FOR REVIEW (Expected Risk Score > 70) — 7 files

| File | Scenario | Key Violations |
|------|----------|---------------|
| `01-FLAGGED-mercury-discharge-violation.txt` | Mercury 641% over limit, lead 247% over, unauthorized discharge | NPDES, Water Quality, Discharge Reporting, Public Notification |
| `02-FLAGGED-drinking-water-ecoli-crisis.txt` | E. coli positive, UV system offline, no boil water advisory | MCLs, Treatment Techniques, Monitoring, Public Notification |
| `03-FLAGGED-illegal-midnight-dumping.txt` | Unpermitted discharge, dead fish, no NPDES permit | NPDES, Water Quality, Record Keeping |
| `04-FLAGGED-falsified-monitoring-data.txt` | Duplicate data, backdated records, operator admitted copying | Data Accuracy, Self-Monitoring, Record Keeping |
| `05-FLAGGED-spill-no-spcc-plan.txt` | 8,500-gal fuel spill, no SPCC plan, near drinking water | Spill Prevention, Timely Reporting, Corrective Actions |
| `06-FLAGGED-stormwater-construction-site.txt` | No SWPPP, zero erosion controls, sediment in impaired creek | Stormwater, BMPs, TMDL, Monitoring |
| `07-FLAGGED-pretreatment-violation-cyanide.txt` | Cyanide 546% over, worker safety incident, treatment offline | Pretreatment, Self-Monitoring, Corrective Actions |

### 🟠 NEEDS REVIEW (Expected Risk Score 41–70) — 6 files

| File | Scenario | Concerns |
|------|----------|----------|
| `08-REVIEW-late-dmr-submission.txt` | DMR submitted 64 days late, minor TSS exceedance | Timely Reporting (1 violation, data otherwise compliant) |
| `09-REVIEW-incomplete-monitoring-schedule.txt` | TTHM, HAA5, lead/copper not tested due to budget | Monitoring & Reporting (gaps but tested params are fine) |
| `10-REVIEW-minor-tmdl-exceedance.txt` | Nitrogen 5.6% over TMDL allocation due to heavy rain | TMDL Compliance (minor, with corrective plan) |
| `11-REVIEW-outdated-bmp-plan.txt` | BMP plan 10 months overdue, 2 BMPs not installed | BMPs, Record Keeping (partial compliance) |
| `12-REVIEW-permit-renewal-gap.txt` | Operating under expired permit (admin extended) | NPDES Permit (technically compliant but outdated limits) |
| `13-REVIEW-public-notification-delay.txt` | TTHM slightly over MCL, public notice 14 days late | Public Notification, MCLs (corrected quickly) |

### 🟢 AI APPROVED / COMPLIANT (Expected Risk Score ≤ 40) — 7 files

| File | Scenario | Why It Passes |
|------|----------|--------------|
| `14-COMPLIANT-model-wwtp-report.txt` | All 8 parameters well within limits, on-time DMR | Perfect compliance across all checks |
| `15-COMPLIANT-drinking-water-excellence.txt` | All contaminants below MCL, full CCR distributed | Zero violations, all monitoring complete |
| `16-COMPLIANT-industrial-pretreatment.txt` | All metals/cyanide well below limits, daily monitoring | Full pretreatment compliance, records current |
| `17-COMPLIANT-stormwater-swppp.txt` | Current SWPPP, all BMPs in place, zero spills | Comprehensive stormwater management |
| `18-COMPLIANT-spcc-plan-review.txt` | 110-120% secondary containment, zero spills in 5 years | Model SPCC plan with certified PE |
| `19-COMPLIANT-corrective-action-complete.txt` | All consent order milestones met ahead of schedule | Demonstrates successful violation correction |
| `20-COMPLIANT-full-compliance-evaluation.txt` | EPA FCE inspection — full compliance, no findings | Clean bill of health from EPA inspector |

---

## Step-by-Step Testing Procedure

### Simple Version (Quick Demo)

1. **Open** the Portal URL in your browser
2. **Paste** the API URL into the config bar → click Save
3. **Pick a test file** from the `sample-reports/` folder
4. **Fill in** Name, Email, Facility → select Report Type
5. **Upload** the file → click **Submit Report for AI Review**
6. **Wait** 30–60 seconds for Mistral AI analysis
7. **See results** — risk score, priority flag, and compliance breakdown
8. **Switch** to **Review Dashboard** tab → click **All Reports**
9. **Click** the report → review AI findings → **Approve**, **Deny**, or **Escalate**

### Detailed Version (Full Demo Walkthrough)

#### Phase 1: Upload a FLAGGED document
1. Open the portal → paste API URL → Save
2. Fill in: Name = "John Smith", Email = "john@test.com", Facility = "Riverside Chemical"
3. Report Type = "Discharge Monitoring Report (DMR)"
4. Upload `01-FLAGGED-mercury-discharge-violation.txt`
5. Click **Submit Report for AI Review**
6. **Expected result**: Risk Score > 70, Status = 🔴 FLAGGED FOR REVIEW
7. Note the key violations: Mercury 641% over, no public notification

#### Phase 2: Upload a REVIEW document
1. Fill in: Name = "Jane Doe", Facility = "Cedar Rapids WWTP"
2. Report Type = "Discharge Monitoring Report (DMR)"
3. Upload `08-REVIEW-late-dmr-submission.txt`
4. **Expected result**: Risk Score 41–70, Status = 🟠 NEEDS REVIEW
5. Note: Data is mostly compliant, but report was 64 days late

#### Phase 3: Upload a COMPLIANT document
1. Fill in: Name = "Bob Wilson", Facility = "Oakville Regional"
2. Report Type = "Discharge Monitoring Report (DMR)"
3. Upload `14-COMPLIANT-model-wwtp-report.txt`
4. **Expected result**: Risk Score ≤ 40, Status = 🟢 AI APPROVED
5. Note: All parameters well within limits, everything on time

#### Phase 4: Engineer Review
1. Click **Review Dashboard** tab
2. Click 🔴 **Flagged** button → see the mercury violation report
3. Click the report → scroll through the 18-checkpoint analysis
4. Note the risk meter (should be red/critical)
5. See the key violations and AI recommendations
6. Enter: Reviewer = "EPA Engineer", Notes = "Confirmed violations, forwarding to enforcement"
7. Click **❌ Deny** (or **⚠️ Escalate** for criminal referral)
8. Click 🟢 **AI Approved** → see the compliant report
9. Click it → verify all 18 checks show COMPLIANT
10. Click **✅ Approve**

#### Phase 5: Show All Statuses
1. Click **All Reports** to see the full queue
2. Show the different status badges: FLAGGED, NEEDS_REVIEW, AI_APPROVED, HUMAN_APPROVED, HUMAN_DENIED
3. Click **ℹ️ Compliance Rules** tab to show all 18 checks and how flagging works

---

## Demo Talking Points

- **"Every document uploaded by a citizen is automatically analyzed by AI against 18 EPA compliance rules"**
- **"The AI doesn't make final decisions — it flags and prioritizes reports for human engineers"**
- **"High-risk documents (score > 70) go straight to the top of the review queue"**
- **"Engineers see exactly which rules were violated, with evidence from the document"**
- **"Compliant documents can be fast-tracked, saving engineer time for real violations"**
- **"The system runs entirely on AWS — S3 for storage, Bedrock for AI, Lambda for processing"**
