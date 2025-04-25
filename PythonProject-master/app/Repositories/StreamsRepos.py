from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.Models.Stream import Stream
from app.Schemas.StreamSchema import StreamSchema
from sqlalchemy.future import select
from sqlalchemy.sql import func



async def GetAllStreams(db: AsyncSession, offset: int = 0, limit: int = 10, sourceID: int = None):
    query = select(Stream)
    if sourceID is not None:
        query = query.where(Stream.sourceID == sourceID)  # Apply the sourceID filter
    query = query.offset(offset).limit(limit)  # Apply pagination after filtering
    result = await db.execute(query)
    return result.scalars().all()

async def GetStreamCount(db: AsyncSession, sourceID: int = None) -> int:
    query = select(func.count()).select_from(Stream)
    if sourceID is not None:
        query = query.filter(Stream.sourceID == sourceID)
    result = await db.scalar(query)
    return result

async def GetStreamById(db: AsyncSession, StreamId: int):
    result = await db.execute(select(Stream).filter(Stream.id == StreamId))
    return result.scalars().first()

async def GetStreamBySourceId(db: AsyncSession, SourceId: int):
    result = await db.execute(select(Stream).filter(Stream.sourceID == SourceId))
    return result.scalars().all()

async def SaveStream(db: AsyncSession, stream: StreamSchema):
    new_stream : Stream
    if stream.id == 0 or stream.id is None:
        new_stream = Stream(
            stream_name = stream.stream_name,
            stream_url = stream.stream_url,
            sourceID = stream.sourceID
        )
        db.add(new_stream)
    else:
        result = await db.execute(select(Stream).filter(Stream.id == stream.id))
        new_stream = result.scalars().first()
        if new_stream is None:
            raise HTTPException(status_code=404, detail="Stream not found")
        
        new_stream.stream_name = stream.stream_name
        new_stream.stream_url = stream.stream_url ,
        new_stream.sourceID = stream.sourceID  

    await db.commit()
    await db.refresh(new_stream)
    return new_stream

    
async def UpdateStream(db: AsyncSession, stream_id: int, updated_data: dict):
    query = select(Stream).where(Stream.id == stream_id)
    result = await db.execute(query)
    db_stream = result.scalar_one_or_none()

    if not db_stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    for key, value in updated_data.items():
        setattr(db_stream, key, value)

    db.add(db_stream)
    await db.commit()
    await db.refresh(db_stream)
    return db_stream


async def DeleteStream(db: AsyncSession, stream_id: int):
    query = select(Stream).where(Stream.id == stream_id)
    result = await db.execute(query)
    db_stream = result.scalar_one_or_none()

    if not db_stream:
        raise HTTPException(status_code=404, detail="Stream not found")

    await db.delete(db_stream)
    await db.commit()
    return {"message": f"Stream with ID {stream_id} deleted successfully"}