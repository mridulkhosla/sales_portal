# Sales Resource Intelligence — Local Demo

A small full-stack demo for sales workforce analytics and resource planning. It includes a FastAPI backend, a static responsive frontend, 100 synthetic employee records, transparent scoring, workload classifications, and a rule-based planning agent.

## Important
- All employee, salary, client and performance data is synthetic.
- This is a **rule-based agent demo**, not a connected LLM/production agent.
- It does not connect to your HR/CRM systems or execute assignments.
- Client budget is potential opportunity value, not recognized revenue.
- Do not use demo scores to make real employment decisions.

## Requirements
- Python 3.10+
- Internet access only if you need to install dependencies

## Run on Ubuntu / VS Code

Open a terminal in this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open the URL printed in the terminal, normally `http://127.0.0.1:8000`.

If Ubuntu says the venv module is missing:

```bash
sudo apt update
sudo apt install python3-venv
```

## API endpoints
- `GET /api/health` — health check
- `GET /api/summary` — workforce KPIs
- `GET /api/employees` — search/filter employee records
- `GET /api/employees/{employee_id}` — individual employee details
- `POST /api/plan` — transparent planning-agent recommendations

Example request:

```bash
curl -X POST http://127.0.0.1:8000/api/plan \
  -H 'Content-Type: application/json' \
  -d '{"target_weight": 40}'
```

## Demo decision logic

### Utilization
- Below 70%: Underutilized
- 70% through 100%: Balanced
- Above 100%: Overutilized

Utilization should eventually be computed from planned workload hours / available productive hours, not guessed manually.

### Performance score
The score combines:
- Target attainment (default 40%; normalized and capped for scoring)
- Conversion rate (25%)
- Customer satisfaction (20%)
- Follow-up compliance (remaining 15%)

The target-attainment weight can be adjusted from 20% to 60%; the remaining weight is rebalanced.

### Agent loop
1. **Perceive** — gather workload and performance indicators.
2. **Evaluate** — calculate score and utilization status.
3. **Plan** — suggest lead allocation, workload review, or coaching investigation.
4. **Verify** — include the triggering rule and require manager approval.

## Production roadmap
1. Replace synthetic data with a secured database and approved CRM/HR integrations.
2. Define actual utilization using workload hours, open leads, meetings/site visits and service-level deadlines.
3. Use actual closed sales, contribution margin, cancellation/refund rates, lead source and sales-cycle length.
4. Add role-based access, audit logs, encryption, data retention and access controls.
5. Add an LLM only where it adds value: summarize evidence, explain recommendations, and ask for missing data. Keep deterministic rules and human approval for consequential decisions.
6. Evaluate for bias and ensure employees can review/correct underlying data.
