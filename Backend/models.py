from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, PickleType, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()


class Service(Base):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    number = Column(String, unique=True)
    name = Column(String)
    service_url = Column(String)
    appointments = relationship('Appointment', back_populates='service')

    def __repr__(self):
        return f"<Service(number={self.number}, name={self.name})>"


class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    service_number = Column(String, ForeignKey('services.number'))
    status = Column(Boolean)
    additional_info = Column(PickleType)
    last_checked = Column(DateTime)
    appointment_date = Column(DateTime)

    service = relationship('Service', back_populates='appointments')

    def __repr__(self):
        return f"<Appointment(service_number={self.service_number}, status={self.status}, appointment_date={self.appointment_date})>"


DATABASE_URL = "sqlite:///appointments.db"

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()
