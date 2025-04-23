import asyncio
import datetime
import os
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.Repositories import StreamsRepos as stream_repo
from app.Repositories import SourceRepos as source_repo
from app.Schemas.StreamSchema import StreamSchema
from app.database import get_db
from typing import List
from app.Scripts.record_stream import StreamRecorder
import logging


router = APIRouter()
logger = logging.getLogger(__name__)

@router.get("/GetAllStreams", response_model=List[StreamSchema])
async def GetAllStreams(db: AsyncSession = Depends(get_db)):

    db_streams = await stream_repo.GetAllStreams(db)
    return db_streams

@router.get("/GetStreamById/{StreamId}", response_model=StreamSchema)
async def GetStreamById(StreamId: int, db: AsyncSession = Depends(get_db)):

    db_stream = await stream_repo.GetStreamById(db, StreamId)
    if db_stream is None:
        raise HTTPException(status_code=404, detail="Stream not found")
    return db_stream

@router.get("/GetStreamBySourceId/{SourceId}", response_model=List[StreamSchema])
async def GetStreamBySourceId(SourceId: int, db: AsyncSession = Depends(get_db)):

    db_streams = await stream_repo.GetStreamBySourceId(db, SourceId)
    if not db_streams:
        raise HTTPException(status_code=404, detail="Streams not found")
    return db_streams

@router.post("/SaveStream", response_model=StreamSchema)
async def SaveStream(stream: StreamSchema, db: AsyncSession = Depends(get_db)):

    db_stream = await stream_repo.SaveStream(db, stream)
    return db_stream



@router.post("/record-streams-by-source/{SourceId}/{duration}")
async def record_streams_by_source(
    SourceId: int,
    duration: int = 15,
    db: AsyncSession = Depends(get_db)
):
    try:
        db_source = await source_repo.GetSourceById(db, SourceId)
        if not db_source:
            raise HTTPException(status_code=404, detail="Source not found")

        db_streams = await stream_repo.GetStreamBySourceId(db, SourceId)
        if not db_streams:
            raise HTTPException(status_code=404, detail="No streams found for this source")

        recorder = StreamRecorder()
        
        # Prepare directory with source name
        try:
            source_dir = await recorder._prepare_source_directory(SourceId, db_source.name)
            logger.info(f"Recording to directory: {source_dir}")
        except Exception as e:
            logger.error(f"Directory preparation failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to prepare recording directory: {str(e)}"
            )

        # Create recording tasks
        tasks = [
            recorder.record_stream(
                stream_url=stream.stream_url,
                source_name=db_source.name, 
                stream_id=stream.id,      
                duration=duration,
                stream_name=stream.stream_name,
                output_dir=source_dir
            )
            for stream in db_streams
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = []
        failed = []
        errors = []
        
        for result in results:
            if isinstance(result, Exception):
                errors.append(str(result))
            elif result.get("success"):
                successful.append(result)
            else:
                failed.append(result)

        return {
            "status": "completed",
            "source_id": SourceId,
            "source_name": db_source.name,
            "output_directory": str(source_dir),
            "success_count": len(successful),
            "failure_count": len(failed) + len(errors),
            "successful": successful,
            "failed": failed,
            "errors": errors
        }
        
    except Exception as e:
        logger.error(f"Inspection failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Inspection failed: {str(e)}"
        )



@router.get("/get-last-inspection")
async def get_last_inspection():
    """
    Returns the most recent inspection results with video file paths
    """
    recordings_dir = Path("recordings")
    
    if not recordings_dir.exists():
        return JSONResponse(
            status_code=404,
            content={
                "status": "not_found",
                "message": "No recordings directory exists",
                "successful": []
            }
        )
    
    # Find all source directories
    sources = []
    for source_dir in recordings_dir.iterdir():
        if source_dir.is_dir() and source_dir.name.startswith("source_"):
            try:
                source_id = int(source_dir.name.split("_")[1])
                mod_time = datetime.fromtimestamp(source_dir.stat().st_mtime)
                sources.append((source_id, source_dir, mod_time))
            except (ValueError, IndexError, OSError):
                continue
    
    if not sources:
        return JSONResponse(
            status_code=404,
            content={
                "status": "not_found",
                "message": "No inspection directories found",
                "successful": []
            }
        )
    
    # Sort by modification time (newest first)
    sources.sort(key=lambda x: x[2], reverse=True)
    source_id, source_dir, mod_time = sources[0]
    
    # Get all recordings from this directory
    successful = []
    for recording in source_dir.glob("*.mp4"):
        if recording.is_file():
            successful.append({
                "stream_name": recording.stem,
                "output_file": str(recording),
                "url": f"/recordings/source_{source_id}/{recording.name}",
                "file_size": f"{os.path.getsize(recording) / (1024 * 1024):.2f} MB",
                "modified_time": datetime.fromtimestamp(
                    recording.stat().st_mtime
                ).isoformat()
            })
    
    return {
        "status": "success",
        "source_id": source_id,
        "inspection_time": mod_time.isoformat(),
        "directory": str(source_dir),
        "successful": successful,
        "success_count": len(successful)
    }
