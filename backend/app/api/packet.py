import uuid

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session

from app.api.schemas import BankPacketOut
from app.db.session import get_db
from app.services.packet import build_packet
from app.services.packet_render import render_packet_html

router = APIRouter(prefix="/netting-runs", tags=["bank-packet"])


@router.get("/{netting_run_id}/packet", response_model=BankPacketOut)
def get_packet(netting_run_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        packet = build_packet(db, netting_run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    db.commit()
    db.refresh(packet)
    return packet


@router.get("/{netting_run_id}/packet.html", response_class=HTMLResponse)
def get_packet_html(netting_run_id: uuid.UUID, db: Session = Depends(get_db)):
    try:
        packet = build_packet(db, netting_run_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    db.commit()
    db.refresh(packet)
    return render_packet_html(packet)
