"""JonesH/hello - the first jonesh tenant app.

Proves the shared postgres + redis wiring (roadmap Stage 3.7/3.8). It reads
DATABASE_URL / REDIS_URL, which nuk injects via the per-app creds env-file that it
appends to the ingress service's env_file. Nothing is hardcoded here.
"""

import os
import socket

import psycopg2
import redis
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

DATABASE_URL = os.environ.get("DATABASE_URL", "")
REDIS_URL = os.environ.get("REDIS_URL", "")

app = FastAPI()


@app.get("/healthz")
def healthz() -> dict:
    return {"ok": True, "host": socket.gethostname()}


@app.get("/", response_class=HTMLResponse)
def index() -> str:
    pg_status, visits = "unset", "-"
    if DATABASE_URL:
        try:
            with psycopg2.connect(DATABASE_URL) as conn, conn.cursor() as cur:
                cur.execute(
                    "CREATE TABLE IF NOT EXISTS visits "
                    "(id serial primary key, at timestamptz default now())"
                )
                cur.execute("INSERT INTO visits DEFAULT VALUES")
                cur.execute("SELECT count(*) FROM visits")
                visits = cur.fetchone()[0]
            pg_status = "ok"
        except Exception as exc:  # noqa: BLE001  # surface any wiring error on the page
            pg_status = f"error: {exc}"
    redis_status = "unset"
    if REDIS_URL:
        try:
            hits = redis.from_url(REDIS_URL).incr("hello:hits")
            redis_status = f"ok (hits={hits})"
        except Exception as exc:  # noqa: BLE001
            redis_status = f"error: {exc}"
    return (
        "<!doctype html><html><head><title>hello.jonesh.de</title></head>"
        '<body style="font-family:sans-serif;max-width:40rem;margin:3rem auto">'
        "<h1>hello from jonesh</h1>"
        f"<p>host <code>{socket.gethostname()}</code></p><ul>"
        f"<li>postgres: <b>{pg_status}</b> &mdash; visits so far: <b>{visits}</b></li>"
        f"<li>redis: <b>{redis_status}</b></li>"
        "</ul><p>JonesH/hello &mdash; the first jonesh app (Stage 3.8).</p>"
        "</body></html>"
    )
