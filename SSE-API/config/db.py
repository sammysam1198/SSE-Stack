import os
from typing import Any

import psycopg2
from psycopg2.extras import RealDictCursor


def get_db_conn():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")

    return psycopg2.connect(
        database_url,
        cursor_factory=RealDictCursor
    )


def fetch_one(query: str, params: tuple[Any, ...] = ()):
    conn = get_db_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
    finally:
        conn.close()


def fetch_all(query: str, params: tuple[Any, ...] = ()):
    conn = get_db_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchall()
    finally:
        conn.close()


def execute_write(query: str, params: tuple[Any, ...] = ()):
    conn = get_db_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(query, params)
    finally:
        conn.close()


def execute_returning_one(query: str, params: tuple[Any, ...] = ()):
    conn = get_db_conn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(query, params)
            return cur.fetchone()
    finally:
        conn.close()4w