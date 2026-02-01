import datetime as dt
from decimal import Decimal

from sqlalchemy import (BigInteger, String, ForeignKey, Date, Numeric, UniqueConstraint, select, Boolean)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session, selectinload
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker
from typing import List

async_session = async_sessionmaker()
class Base(DeclarativeBase, AsyncAttrs):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(25))
    rate: Mapped[None| Decimal] = mapped_column(Numeric(10), nullable=True)
    user_tips: Mapped[bool] = mapped_column(Boolean, nullable=False, server_default="false")

    work_times: Mapped[List["WorkTime"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan")

    def get_status(self) -> str:
        lines = [f"User(name={self.name},tg_id={self.tg_id!r})"]
        sum_hour = 0
        for wt in self.work_times:
            lines.append(f"|{wt.date.strftime('%d.%m.%Y')} - {wt.hour} часов")
            sum_hour += wt.hour

        lines.append(f"= в сумме: {sum_hour} часов")
        return "\n".join(lines)

class WorkTime(Base):
    __tablename__ = 'work_time'
    __table_args__ = (UniqueConstraint("user_id", "date", name="uq_user_date"),)#for unique

    id: Mapped[int] = mapped_column(primary_key=True)
    date: Mapped[dt.date] = mapped_column(Date, nullable=False)
    hour: Mapped[Decimal] = mapped_column(Numeric(6, 2), nullable=False)
    tips: Mapped[Decimal] = mapped_column(Numeric(6), nullable=False, server_default="0")

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.tg_id', ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user: Mapped["User"] = relationship(back_populates="work_times")

