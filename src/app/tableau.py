
import shutil
from typing import List
from pathlib import Path
from . import schemas, models
from fastapi_cache import caches
from sqlalchemy.orm import Session
from tempfile import NamedTemporaryFile
from app.utils import handle_csv_import
from tableauhyperapi import HyperProcess
from .database import SessionLocal, engine
from fastapi import APIRouter, status, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from app.common_tags import HYPER_PROCESS_CACHE_KEY

router = APIRouter()

# Dependency
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()

@router.get("/data/", response_model=List[schemas.Notes], status_code=status.HTTP_200_OK)
def data(take: int = 20, db: Session = Depends(get_db)):
    """
    Pulls data from a postgres database
    and packages it in a csv file
    """
    data = []
    query = db.query(models.Notes).limit(take)
    for note in query.all():
        data.append({
            'user': f"{note.username}",
            'display': f"{note.display}",
            'story': f"{note.text}"
        })
    return JSONResponse(content=data)

@router.post("/import", tags=["Form"])
def import_data_from_csv(
        id_string: str,
        csv_file: UploadFile = File(...)):
    """
    Imports CSV data into a hyper file & creates the hyper file if
    it does not exist.
    """
    process: HyperProcess = caches.get(
        HYPER_PROCESS_CACHE_KEY)
    imported_rows = 0
    suffix = Path(csv_file.filename).suffix
    csv_file.file.seek(0)
    with NamedTemporaryFile(delete=False, suffix=suffix) as tmp_upload:
        shutil.copyfileobj(csv_file.file, tmp_upload)
        tmp_upload.flush()
        imported_rows = handle_csv_import(
            file_identifier=id_string, csv_path=Path(tmp_upload.name), process=process, publish=True)
    return {'imported_rows': imported_rows}

@router.get("/schema/", status_code = status.HTTP_200_OK)
def schema():
    schema = ["id", "user", "display", "story"]
    return JSONResponse(content=schema)