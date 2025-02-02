from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func, BigInteger

class Base(DeclarativeBase):
    pass

class ShipArrivals(Base):
    __tablename__ = "ship_arrivals"
    id = mapped_column(Integer, primary_key=True)
    ship_id = mapped_column(Integer, nullable=False)
    port_id = mapped_column(Integer, nullable=False)
    containers_onboard = mapped_column(Integer, nullable=False)
    docking_time = mapped_column(DateTime, nullable=False)
    origin_country = mapped_column(String(50), nullable=False)
    date_created = mapped_column(DateTime, nullable=False, default=func.now())
    trace_id = mapped_column(String(50), nullable=False)


class ContainerProcessing(Base):
    __tablename__ = "container_processing"
    id = mapped_column(Integer, primary_key=True)
    container_id = mapped_column(Integer, nullable=False)
    processing_hub_id = mapped_column(Integer, nullable=False)
    container_weight = mapped_column(Integer, nullable=False)
    destination = mapped_column(String(50), nullable=False)
    unloading_time = mapped_column(DateTime, nullable=False)
    date_created = mapped_column(DateTime, nullable=False, default=func.now())
    trace_id = mapped_column(String(50), nullable=False)

