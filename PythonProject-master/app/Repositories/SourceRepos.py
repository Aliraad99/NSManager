from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.Models.Source import Source
from app.Schemas.SourceSchema import SourceSchema
from sqlalchemy.future import select


async def GetAllSources(db: AsyncSession):
    result = await db.execute(select(Source))
    return result.scalars().all()

async def GetSourceById(db: AsyncSession, SourceId: int):
    result = await db.execute(select(Source).filter(Source.id == SourceId))
    return result.scalars().first()
    
async def AddSource(db: AsyncSession, source: SourceSchema):
    new_source : Source
    if source.id == 0 or source.id is None:
        new_source = Source(
            name=source.name
        )
        db.add(new_source)
    else:
        result = await db.execute(select(Source).filter(Source.id == source.id))
        new_source = result.scalars().first()
        if new_source is None:
            raise HTTPException(status_code=404, detail="Source not found")
        
        new_source.name = source.name

    await db.commit()
    await db.refresh(new_source)
    return new_source