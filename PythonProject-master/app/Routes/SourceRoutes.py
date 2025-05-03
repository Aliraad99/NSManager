from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories import SourceRepos as source_repo
from app.Schemas.SourceSchema import SourceSchema
from app.Models.Source import Source
from app.database import get_db
from typing import List

router = APIRouter()

@router.get("/GetAllSources", response_model=List[SourceSchema])
async def GetAllSources(db: AsyncSession = Depends(get_db)):

    db_sources = await source_repo.GetAllSources(db)
    if not db_sources:
        raise HTTPException(status_code=404, detail="Sources not found")
    
    return db_sources

@router.get("/GetSourceById/{SourceId}", response_model=SourceSchema)
async def GetSourceById(SourceId: int, db: AsyncSession = Depends(get_db)):

    db_source = await source_repo.GetSourceById(db, SourceId)
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    return db_source

@router.post("/AddSource", response_model=SourceSchema)
async def AddSource(source: SourceSchema, db: AsyncSession = Depends(get_db)):

    db_source = await source_repo.AddSource(db, source)
    return db_source


@router.delete("/DeleteSource/{SourceId}", response_model=SourceSchema)
async def DeleteSource(SourceId: int, db: AsyncSession = Depends(get_db)):

    db_source = await source_repo.DeleteSource(db, SourceId)
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    return db_source

@router.put("/UpdateSource/{SourceId}", response_model=SourceSchema)
async def UpdateSource(SourceId: int, source: SourceSchema, db: AsyncSession = Depends(get_db)):

    db_source = await source_repo.UpdateSource(db, SourceId, source)
    if not db_source:
        raise HTTPException(status_code=404, detail="Source not found")
    return db_source