from sqlalchemy import create_engine
from sqlalchemy import Column, ForeignKey, BigInteger, Date, Float, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from .constants import DB_NAME

engine = create_engine('sqlite:///{}?check_same_thread=False'.format(DB_NAME), pool_pre_ping=True)
Base = declarative_base(bind=engine)
Session = scoped_session(sessionmaker(bind=engine, autoflush=False))


def session():
    s = sessionmaker(bind=engine)
    return s()


class IndexMembership(Base):
    __tablename__ = 'index_membership'
    idate = Column(Date, nullable=False, primary_key=True)
    indexname = Column(String, nullable=False, primary_key=True)
    ticker = Column(String, primary_key=True)
    sector = Column(String)
    name = Column(String, nullable=False, primary_key=True)
    shares = Column(BigInteger, primary_key=True, default=0)
    weight = Column(Float, nullable=False, default=0)


class PriceData(Base):
    __tablename__ = 'stock_prices'
    pdate = Column(Date, nullable=False, primary_key=True)
    ticker = Column(String, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    dividends = Column(Float)
    stock_splits = Column(Float)


class TechnicalIndicatorData(Base):
    __tablename__ = 'indicators'
    idate = Column(Date, nullable=False, primary_key=True)
    ticker = Column(String, primary_key=True)

