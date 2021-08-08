import asyncio
import typing as t

from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy.engine import Result
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import Select

Base = declarative_base()

CALLBACK_FUNCTION_TYPE = t.Callable[[t.Type[Base], int], t.Awaitable[None]]


class Alert(Base):
    __tablename__ = "alerts"
    __table_args__ = (UniqueConstraint("email", "phrase"),)

    id = Column(Integer, primary_key=True)
    email = Column(String)
    phrase = Column(String)
    interval = Column(Integer)


async def noop_callback(model: t.Type[Base], obj_id: int):
    """Nullable callback for default callback function"""
    pass


class DbConnection:
    """
    Wrapper for DB connection
    """

    def __init__(
        self,
        db_path: str,
        on_create: t.Optional[CALLBACK_FUNCTION_TYPE] = None,
        on_update: t.Optional[CALLBACK_FUNCTION_TYPE] = None,
        on_delete: t.Optional[CALLBACK_FUNCTION_TYPE] = None,
        *args,
        **kwargs,
    ):
        self._engine: AsyncEngine = create_async_engine(
            f"sqlite+aiosqlite:///{db_path}",
            future=True,
            *args,
            **kwargs,
        )
        self.session: AsyncSession = AsyncSession(
            self._engine, expire_on_commit=False, future=True
        )
        self.on_create = on_create or noop_callback
        self.on_update = on_update or noop_callback
        self.on_delete = on_delete or noop_callback

    async def init_schema(self):
        """Drops existing tables and create all tables from the metadata"""
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)

    async def bulk_create(self, entries: t.List[Base]):
        """Insert entries as bulk"""
        self.session.add_all(entries)
        await self.session.commit()

    async def create(self, obj: Base) -> Base:
        """Insert an instance to the database"""
        self.session.add(obj)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise e

        loop = asyncio.get_event_loop()
        loop.create_task(self.on_create(type(obj), obj.id))
        return obj

    async def update(self, obj: Base, **values):
        """Update the object with given values"""
        for field, value in values.items():
            setattr(obj, field, value)
        try:
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise e

        loop = asyncio.get_event_loop()
        loop.create_task(self.on_update(type(obj), obj.id))
        return obj

    async def select(self, stmt: Select) -> Result:
        """Execute select statement and returns results"""
        return await self.session.execute(stmt)

    async def delete(self, obj: Base):
        """Delete object from the database"""
        try:
            await self.session.delete(obj)
            await self.session.commit()
        except IntegrityError as e:
            await self.session.rollback()
            raise e

        loop = asyncio.get_event_loop()
        loop.create_task(self.on_delete(type(obj), obj.id))

    async def close(self):
        """Close the session and dispose the engine"""
        await self.session.close()
        await self._engine.dispose()
