from fastapi import FastAPI, Query
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI(title="Sales Resource Intelligence Demo", version="1.0.0")
app.mount("/static", StaticFiles(directory="static"), name="static")

FIRST_NAMES = ["Aarav", "Priya", "Rahul", "Neha", "Vikram", "Ananya", "Rohan", "Ishita", "Arjun", "Simran"]
LAST_NAMES = ["Sharma", "Verma", "Mehta", "Kapoor", "Singh", "Gupta", "Malhotra", "Jain", "Patel", "Kaur"]
SALARIES = [32000, 38000, 45000, 52000, 60000, 70000, 85000]
UTILIZATIONS = [48, 62, 74, 88, 96, 108, 121, 82, 68, 103, 91, 77]
ATTAINMENT = [42, 58, 66, 78, 92, 105, 118, 84, 72, 96, 110, 63]
CONVERSIONS = [8, 12, 15, 18, 22, 25, 30, 17, 14, 27]
SATISFACTIONS = [3.2, 3.6, 3.9, 4.1, 4.4, 4.7, 4.9, 3.8, 4.2, 4.5]
BUDGETS = [2500000, 4000000, 6000000, 8000000, 10000000, 15000000, 20000000, 5000000, 12000000, 3000000]
FOLLOW_UP = [62, 70, 76, 82, 88, 93, 97, 79, 85, 90]

def make_employee(i: int) -> dict:
    # Synthetic, deterministic demo data. Not real employee records.
    salary = SALARIES[i % len(SALARIES)]
    utilization = UTILIZATIONS[(i * 7 + i % 5) % len(UTILIZATIONS)]
    attainment = ATTAINMENT[(i * 3 + i % 4) % len(ATTAINMENT)]
    conversion = CONVERSIONS[(i * 5 + i % 3) % len(CONVERSIONS)]
    satisfaction = SATISFACTIONS[(i * 2 + i % 3) % len(SATISFACTIONS)]
    budget = BUDGETS[(i * 3 + i % 7) % len(BUDGETS)]
    closed_value = round(budget * attainment / 100)
    follow_up = FOLLOW_UP[(i * 7 + i % 2) % len(FOLLOW_UP)]
    status = "Underutilized" if utilization < 70 else ("Overutilized" if utilization > 100 else "Balanced")
    return {
        "id": i + 1,
        "name": f"{FIRST_NAMES[i % 10]} {LAST_NAMES[i % 10]}" + (f" {i // 10 + 1}" if i >= 10 else ""),
        "role": "Senior Sales Executive" if i % 9 == 0 else "Sales Executive",
        "salary": salary,
        "client": f"Client {1001 + i}",
        "client_budget": budget,
        "closed_value": closed_value,
        "utilization": utilization,
        "target_attainment": attainment,
        "conversion_rate": conversion,
        "satisfaction": satisfaction,
        "follow_up_compliance": follow_up,
        "status": status,
    }

EMPLOYEES = [make_employee(i) for i in range(100)]

def performance_score(e: dict, target_weight: int = 40) -> int:
    # Weights sum to 100: target attainment, conversion, satisfaction, follow-up.
    # Normalize attainment to a 0-100 range for scoring.
    target = min(e["target_attainment"], 120) / 120 * 100
    conversion = min(e["conversion_rate"], 30) / 30 * 100
    satisfaction = e["satisfaction"] / 5 * 100
    follow_weight = 55 - target_weight
    return round(target * (target_weight / 100) + conversion * .25 + satisfaction * .20 + e["follow_up_compliance"] * (follow_weight / 100))

def employee_view(e: dict, target_weight: int = 40) -> dict:
    result = dict(e)
    result["performance_score"] = performance_score(e, target_weight)
    return result

class PlanRequest(BaseModel):
    target_weight: int = Field(default=40, ge=20, le=60)

@app.get("/")
def index():
    return FileResponse("static/index.html")

@app.get("/api/health")
def health():
    return {"status": "ok", "mode": "demo", "employee_count": len(EMPLOYEES)}

@app.get("/api/summary")
def summary(target_weight: int = Query(default=40, ge=20, le=60)):
    rows = [employee_view(e, target_weight) for e in EMPLOYEES]
    under = sum(e["status"] == "Underutilized" for e in rows)
    over = sum(e["status"] == "Overutilized" for e in rows)
    return {
        "employee_count": len(rows),
        "average_performance": round(sum(e["performance_score"] for e in rows) / len(rows)),
        "average_utilization": round(sum(e["utilization"] for e in rows) / len(rows)),
        "underutilized": under,
        "balanced": len(rows) - under - over,
        "overutilized": over,
        "monthly_salary_total": sum(e["salary"] for e in rows),
        "demo_data": True,
    }

@app.get("/api/employees")
def list_employees(
    q: str = "",
    status: str = "All",
    target_weight: int = Query(default=40, ge=20, le=60),
    limit: int = Query(default=100, ge=1, le=100),
):
    rows = [employee_view(e, target_weight) for e in EMPLOYEES]
    q = q.strip().lower()
    if q:
        rows = [e for e in rows if q in e["name"].lower() or q in e["client"].lower() or q == str(e["id"])]
    if status != "All":
        rows = [e for e in rows if e["status"] == status]
    rows.sort(key=lambda e: e["performance_score"], reverse=True)
    return {"items": rows[:limit], "total_matching": len(rows), "demo_data": True}

@app.get("/api/employees/{employee_id}")
def get_employee(employee_id: int, target_weight: int = Query(default=40, ge=20, le=60)):
    e = next((x for x in EMPLOYEES if x["id"] == employee_id), None)
    if e is None:
        return {"error": "Employee not found"}
    return employee_view(e, target_weight)

@app.post("/api/plan")
def planning_agent(request: PlanRequest):
    """Transparent rule-based agent loop: perceive -> evaluate -> plan -> verify."""
    weight = request.target_weight
    rows = [employee_view(e, weight) for e in EMPLOYEES]

    # PERCEIVE: collect workforce capacity and performance signals.
    under = [e for e in rows if e["utilization"] < 70]
    over = [e for e in rows if e["utilization"] > 100]
    low_score = [e for e in rows if e["performance_score"] < 60]

    # EVALUATE + PLAN: apply explicit, auditable business rules.
    recommendations = []
    strong_spare_capacity = [e for e in under if e["performance_score"] >= 70]
    for e in sorted(strong_spare_capacity, key=lambda x: x["performance_score"], reverse=True)[:3]:
        recommendations.append({
            "priority": "Opportunity",
            "title": f"Review a new lead for {e['name']}",
            "employee_id": e["id"],
            "reason": f"Utilization is {e['utilization']}% and performance score is {e['performance_score']}/100.",
            "rule": "Utilization < 70% AND performance score >= 70",
            "action": "Manager reviews skills, territory, client fit and current pipeline before assigning a lead.",
        })
    for e in sorted(over, key=lambda x: x["utilization"], reverse=True)[:3]:
        recommendations.append({
            "priority": "High",
            "title": f"Review workload for {e['name']}",
            "employee_id": e["id"],
            "reason": f"Utilization is {e['utilization']}%, above the 100% planning threshold.",
            "rule": "Utilization > 100%",
            "action": "Review open leads, site visits, follow-ups and deadlines; rebalance only after manager approval.",
        })
    for e in sorted(low_score, key=lambda x: x["performance_score"])[:3]:
        recommendations.append({
            "priority": "Review",
            "title": f"Investigate support needs for {e['name']}",
            "employee_id": e["id"],
            "reason": f"Current weighted score is {e['performance_score']}/100.",
            "rule": "Performance score < 60",
            "action": "Review lead quality, training, territory, follow-up consistency and measurement period before deciding next steps.",
        })

    # VERIFY: ensure recommendations are explanatory and never execute HR actions.
    for r in recommendations:
        r["requires_human_approval"] = True
    return {
        "agent_steps": [
            {"step": "Perceive", "detail": "Read workload, target attainment, conversion, satisfaction and follow-up indicators."},
            {"step": "Evaluate", "detail": "Classify utilization and calculate a transparent weighted score."},
            {"step": "Plan", "detail": "Suggest lead allocation, workload review or coaching investigation based on explicit rules."},
            {"step": "Verify", "detail": "Attach the triggering rule and require a manager to approve any action."},
        ],
        "target_weight": weight,
        "recommendations": recommendations,
        "notes": [
            "This is a rule-based demo agent, not a connected LLM agent.",
            "Client budget is potential opportunity value, not recognized revenue.",
            "Use actual closed revenue, contribution margin, sales cycle, lead quality and time period for production decisions.",
        ],
        "demo_data": True,
    }
