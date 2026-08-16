from typing import Annotated
from fastapi import APIRouter, Depends, File, Form, UploadFile, HTTPException, status
from models.models import AddCertificateRequestModel, AddTemplateRequestModel, RevokeCertificateRequestModel, AddBadgeTemplateRequestModel, AddBadgeRequestModel
from services.database import add_badge, add_badge_template, add_certificate, add_template, get_all_templates, get_all_certificates, revoke_certificate, get_all_badge_templates
from services.storage import upload_template, upload_badge
from utils.auth import verify_admin

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
    dependencies=[Depends(verify_admin)]
)


@router.post("/add/template")
async def admin_add_template(
    template: Annotated[UploadFile, File(...)],
    font_size: Annotated[str, Form(...)],
    font_color: Annotated[str, Form(pattern=r'^#(?:[0-9a-fA-F]{3}){1,2}$')],
    name_x_pos: Annotated[int, Form(...)],
    name_y_pos: Annotated[int, Form(...)],
    template_name: Annotated[str | None, Form()] = None,
    template_for: Annotated[str | None, Form()] = None,
    event_name: Annotated[str | None, Form()] = None,
    issuer_name: Annotated[str | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
):
    ALLOWED_CONTENT_TYPES = ["application/pdf", "image/png", "image/jpeg"]
    if template.content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Invalid template file type. Allowed types: {', '.join(ALLOWED_CONTENT_TYPES)}"
        )

    request_data = AddTemplateRequestModel(
        font_size=font_size,
        font_color=font_color,
        name_x_pos=name_x_pos,
        name_y_pos=name_y_pos,
        template_name=template_name,
        template_for=template_for,
        event_name=event_name,
        issuer_name=issuer_name,
        notes=notes,
    )
    upload_result = await upload_template(template)
    db_record = add_template(upload_result["public_url"], request_data)

    return {
        "ok": True,
        "message": "Template added successfully",
        "upload": upload_result,
        "template": db_record,
        "data": request_data.model_dump(),
    }


@router.post("/add/certificate")
def admin_add_certificate(request: AddCertificateRequestModel):
    certificate = add_certificate(request)

    return {
        "ok": True,
        "message": "Certificate added successfully",
        "certificate": certificate,
    }

@router.get("/templates")
def admin_get_templates():
    templates = get_all_templates()
    return {
        "ok": True,
        "message": "Templates fetched successfully",
        "templates": templates,
    }

@router.get("/certificates")
def admin_get_certificates(
    template_id: int | None = None,
    recipient_email: str | None = None
):
    certificates = get_all_certificates(template_id, recipient_email)
    return {
        "ok": True,
        "message": "Certificates fetched successfully",
        "certificates": certificates,
    }

@router.get("/badge-templates")
def get_all_badges_templates() -> dict:
    badge_templates = get_all_badge_templates()
    return {
        "ok": True,
        "message": "Badge templates fetched successfully",
        "badge_templates": badge_templates
    }

@router.post("/certificates/{certificate_id}/revoke")
def admin_revoke_certificate(certificate_id: str, request: RevokeCertificateRequestModel):
    try:
        certificate = revoke_certificate(certificate_id, request)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return {
        "ok": True,
        "message": "Certificate revoked successfully" if request.revoked else "Certificate revocation reverted",
        "certificate": certificate,
    }

  @router.post("/add/badge-template")
async def admin_add_badge_template(
    template: Annotated[UploadFile, File(...)],
    template_name: Annotated[str, Form(...)],
    template_for: Annotated[str | None, Form()] = None,
    event_name: Annotated[str | None, Form()] = None,
    issuer_name: Annotated[str | None, Form()] = None,
    notes: Annotated[str | None, Form()] = None,
):
    request_data = AddBadgeTemplateRequestModel(
        template_name=template_name,
        template_for=template_for,
        event_name=event_name,
        issuer_name=issuer_name,
        notes=notes,
    )

    upload_result = await upload_badge(template)
    db_record = add_badge_template(upload_result["public_url"], request_data)

    return {
        "ok": True,
        "message": "Badge template added successfully",
        "badge_template": db_record,
    }


@router.post("/add/badge")
def admin_add_badge(request: AddBadgeRequestModel):
    try:
        badge = add_badge(request)

    except ValueError as e:
        if "not found" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str(e),
            )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error",
        )

    return {
        "ok": True,
        "message": "Badge issued successfully",
        "badge": badge,
    }
