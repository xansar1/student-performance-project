from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "running"}


@router.get("/subscription/plans")
def plans():
    return {
        "starter": "₹4999/month",
        "pro": "₹14999/month",
        "enterprise": "custom pricing"
    }


@router.get("/analytics/kpis")
def get_kpis():
    return {
        "total_students": 1200,
        "avg_score": 78.5,
        "top_score": 99,
        "at_risk": 86
    }
