from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy import Integer, String, DateTime, func


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

    def to_dict(self):
        ship_dict = {}
        ship_dict["id"] = self.id
        ship_dict["ship_id"] = self.ship_id
        ship_dict["port_id"] = self.port_id
        ship_dict["containers_onboard"] = self.containers_onboard
        ship_dict["docking_time"] = self.docking_time
        ship_dict["origin_country"] = self.origin_country
        ship_dict["date_created"] = self.date_created
        ship_dict["trace_id"] = self.trace_id

        return ship_dict


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

    def to_dict(self):
        container_dict = {}
        container_dict["id"] = self.id
        container_dict["container_id"] = self.container_id
        container_dict["processing_hub_id"] = self.processing_hub_id
        container_dict["container_weight"] = self.container_weight
        container_dict["destination"] = self.destination
        container_dict["unloading_time"] = self.unloading_time
        container_dict["date_created"] = self.date_created
        container_dict["trace_id"] = self.trace_id

        return container_dict
