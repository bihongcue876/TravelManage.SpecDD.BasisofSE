from typing import List, Optional
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Application, Participant, AppState
from schemas import (
    ApplicationCreate, ApplicationResponse, ApplicationDetailResponse,
    ParticipantCreate, ParticipantUpdate, ParticipantResponse,
    PaymentRequest, ParticipantsBulkRequest, CancelPreviewResponse,
    ApplicationSearchParams
)
from services import application as app_service

router = APIRouter(prefix="/api/applications", tags=["applications"])


@router.post("", response_model=ApplicationResponse, status_code=201)
def create_application(data: ApplicationCreate, db: Session = Depends(get_db)):
    try:
        application = app_service.create_application(db, data)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{application_id}", response_model=ApplicationDetailResponse)
def get_application(application_id: int, db: Session = Depends(get_db)):
    application = db.query(Application).options(
        joinedload(Application.participants),
        joinedload(Application.group)
    ).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.get("/search", response_model=List[ApplicationResponse])
def search_applications(
    code: Optional[str] = Query(None),
    departure_from: Optional[date] = Query(None),
    departure_to: Optional[date] = Query(None),
    name: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(Application).join(Application.group)

    if code:
        query = query.filter(Application.group.has(code=code))
    if departure_from:
        query = query.filter(Application.group.has(departure_date=departure_from))
    if departure_to:
        query = query.filter(Application.group.has(departure_date=departure_to))
    if name:
        query = query.filter(Application.name.like(f"%{name}%"))

    applications = query.all()
    return applications


@router.post("/{application_id}/pay-deposit", response_model=ApplicationResponse)
def pay_deposit(application_id: int, data: PaymentRequest, db: Session = Depends(get_db)):
    try:
        application = app_service.pay_deposit(db, application_id, data.amount)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{application_id}/participants", response_model=ApplicationResponse)
def add_participants(
    application_id: int,
    data: ParticipantsBulkRequest,
    db: Session = Depends(get_db)
):
    try:
        application = app_service.add_participants(db, application_id, data.participants)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{application_id}/pay-balance", response_model=ApplicationResponse)
def pay_balance(application_id: int, data: PaymentRequest, db: Session = Depends(get_db)):
    try:
        application = app_service.pay_balance(db, application_id, data.amount)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{application_id}/cancel", response_model=ApplicationResponse)
def cancel_application(
    application_id: int,
    reason: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    try:
        application, refund = app_service.cancel_application(db, application_id, reason)
        return application
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{application_id}/cancel-preview", response_model=CancelPreviewResponse)
def get_cancel_preview(application_id: int, db: Session = Depends(get_db)):
    try:
        preview = app_service.get_cancel_preview(db, application_id)
        return preview
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/participants/{participant_id}", response_model=ParticipantResponse)
def update_participant(
    participant_id: int,
    data: ParticipantUpdate,
    db: Session = Depends(get_db)
):
    try:
        participant = app_service.update_participant(db, participant_id, data)
        return participant
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{application_id}/participants", response_model=List[ParticipantResponse])
def list_participants(application_id: int, db: Session = Depends(get_db)):
    participants = db.query(Participant).filter(
        Participant.application_id == application_id
    ).all()
    return participants
