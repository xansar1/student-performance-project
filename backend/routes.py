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
