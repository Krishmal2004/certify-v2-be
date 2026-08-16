from fastapi import APIRouter, HTTPException, status
from services.database import get_badge_by_id

router = APIRouter(
  prefix="/badge",
  tags=["badge"],
)

@router.get(
  "/preview/{badge_id}",
  responses={
    404: {"description": "Badge not found"},
  },
)
def preview_badge(badge_id: str):
  try:
    badge = get_badge_by_id(badge_id)
  except ValueError as exc:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

  return {
    "ok": True,
    "message": "Badge verified successfully",
    "badge": badge,
  }