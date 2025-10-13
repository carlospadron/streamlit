"""
Database utility library for Streamlit pages.
Provides a function to create a SQLAlchemy engine using environment variables.
"""

import os

import pandas as pd
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.engine.url import URL


def _create_database_engine() -> Engine:
    """
    Create and return a SQLAlchemy Engine for the PostgreSQL database using environment variables.
    
    Raises:
        EnvironmentError: If any required environment variable is missing.
        ConnectionError: If the engine cannot be created or connected.
    
    Returns:
        Engine: SQLAlchemy Engine instance connected to the database.
    """
    try:
        user: str = os.environ["DB_USER"]
        password: str = os.environ["DB_PASSWORD"]
        host: str = os.environ["DB_HOST"]
        port: str = os.environ.get("DB_PORT", "5432")
        db: str = os.environ["DB_NAME"]
    except KeyError as e:
        raise EnvironmentError(f"Missing required environment variable: {e}")

    try:
        # Build connection URL safely with proper escaping
        connection_url = URL.create(
            drivername="postgresql",
            username=user,
            password=password,
            host=host,
            port=int(port),
            database=db,
        )
        
        engine = create_engine(
            connection_url,
            pool_pre_ping=True,  # Verify connections before using
            pool_size=5,  # Connection pool size
            max_overflow=10,  # Max connections beyond pool_size
        )
        
        # Test connection to fail fast if credentials/host are invalid
        # pool_pre_ping ensures connections are valid but does not test initial connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            
        return engine
    except Exception as e:
        raise ConnectionError(f"Failed to create database engine: {e}")


@st.cache_resource
def get_database_engine() -> Engine:
    """
    Get a cached SQLAlchemy engine for the PostgreSQL database.
    
    This function is cached using Streamlit's @st.cache_resource decorator,
    ensuring that the database connection is reused across all pages and reruns.
    
    Raises:
        EnvironmentError: If any required environment variable is missing.
        ConnectionError: If the engine cannot be created or connected.
    
    Returns:
        Engine: Cached SQLAlchemy Engine instance connected to the database.
    """
    return _create_database_engine()


@st.cache_data(ttl=600)
def load_data(sql: str) -> pd.DataFrame:
    """
    Load data from the database using a SQL query.
    
    This function is cached using Streamlit's @st.cache_data decorator with a 10-minute TTL.
    The cache is invalidated based on the SQL query string, so different queries are cached separately.
    
    Args:
        sql: SQL query string to execute.
    
    Returns:
        DataFrame containing the query results.
    
    Raises:
        Exception: If the query execution fails.
    """
    engine = get_database_engine()
    return pd.read_sql(sql, engine)
