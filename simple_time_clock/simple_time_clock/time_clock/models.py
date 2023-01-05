from sqlalchemy import text, Boolean, Column, DateTime, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Employee(Base):
    __tablename__ = "employee"

    employee_id = Column(
        UUID, primary_key=True, server_default=text("uuid_generate_v1mc()")
    )

    username = Column(String)
    password = Column(String)

    first_name = Column(String)
    last_name = Column(String)

    is_admin = Column(Boolean)


class ShiftData(Base):
    __tablename__ = "shift_data"

    shift_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v1mc()"))
    employee_id = Column(UUID, ForeignKey(Employee.employee_id))

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    is_active = Column(Boolean)
    on_lunch = Column(Boolean)
    on_break = Column(Boolean)


class LunchData(Base):
    __tablename__ = "lunch_data"

    lunch_break_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v1mc()"))
    shift_data_id = Column(UUID, ForeignKey(ShiftData.shift_id))

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    is_active = Column(Boolean)


class BreakData(Base):
    __tablename__ = "break_data"

    break_id = Column(UUID, primary_key=True, server_default=text("uuid_generate_v1mc()"))
    shift_data_id = Column(UUID, ForeignKey(ShiftData.shift_id))

    start_time = Column(DateTime)
    end_time = Column(DateTime)

    is_active = Column(Boolean)
