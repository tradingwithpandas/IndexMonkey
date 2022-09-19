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


class DBMFHoldings(Base):
    __tablename__ = 'dbmf_holdings'
    hdate = Column(Date, nullable=False, primary_key=True)
    cusip = Column(String, primary_key=True)
    ticker = Column(String, primary_key=True)
    description = Column(String)
    shares = Column(Float, nullable=False)
    mv = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)


class ManagedFuturesHoldings(Base):
    __tablename__ = 'mgd_futures_etfs'
    hdate = Column(Date, nullable=False, primary_key=True)
    etf = Column(String, nullable=False, primary_key=True)
    cusip = Column(String, primary_key=True)
    ticker = Column(String, primary_key=True)
    description = Column(String, nullable=False)
    asset = Column(String, nullable=False)
    expiry = Column(Date)
    shares = Column(Float, nullable=False)
    mv = Column(Float, nullable=False)
    weight = Column(Float, nullable=False)


class ETFStats(Base):
    __tablename__ = 'etf_stats'
    sdate = Column(Date, nullable=False, primary_key=True)
    ticker = Column(String, primary_key=True)
    nav = Column(Float)
    shares_outstanding = Column(Float)
    aum = Column(Float)
