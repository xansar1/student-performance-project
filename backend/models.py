from sqlalchemy import Column, Integer, String, Float
from database import Base


class Student(Base):
    _tablename_ = "students"

    id = Column(Integer, primary_key=True)
    student_name = Column(String)
    university = Column(String)
    program = Column(String)
    total_score = Column(Float)
    placement_probability = Column(Float)
