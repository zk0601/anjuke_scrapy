from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, VARCHAR, INTEGER, TEXT, DATETIME, DECIMAL


Base = declarative_base()


class AjkErshou(Base):
    __tablename__ = 'dataRepository_ajkershou'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    city = Column(VARCHAR(255), nullable=False)
    ext_url = Column(VARCHAR(255), nullable=False)


class TempPhone(Base):
    __tablename__ = 'temp_phone'

    id = Column(INTEGER, primary_key=True, autoincrement=True)
    ext_code = Column(VARCHAR(255), nullable=False)
    phone = Column(VARCHAR(255), nullable=False)
