from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.Models.Stream import Stream
from app.Schemas.StreamSchema import StreamSchema
from sqlalchemy.future import select


async def GetAllStreams(db: AsyncSession):
    result = await db.execute(select(Stream))
    return result.scalars().all()

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

    