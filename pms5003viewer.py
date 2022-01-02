import base64
import os
import sqlite3
from io import BytesIO

from flask import Flask, g
from matplotlib.figure import Figure

app = Flask(__name__)

DATABASE = os.environ["LOGGER_DB"]


def get_measurements(conn):
    timestamps, values = zip(
        *conn.execute(
            """
        select
            timestamp,
            avg(value) over (
                partition by name
                order by timestamp
                rows between 30 preceding and current row
            ) as value_30min_avg
        from measurements
        where timestamp >= datetime('now', '-24 hours')
            and name = 'PM2.5'
        order by timestamp
    """
        )
    )
    return timestamps, values


def plot(timestamps, values):
    fig = Figure()  # not using pyplot because of memory leaks
    ax = fig.subplots()
    ax.plot(timestamps, values)
    ax.set_xlabel("Timestamp")
    ax.set_ylabel("30 min mean PM2.5 (10^-6 g/m^3)")
    return fig


def get_conn():
    conn = getattr(g, "_database", None)
    if conn is None:
        conn = g._database = sqlite3.connect(
            DATABASE, detect_types=sqlite3.PARSE_DECLTYPES
        )
    return conn


@app.teardown_appcontext
def close_connection(exception):
    conn = getattr(g, "_database", None)
    if conn is not None:
        conn.close()


@app.route("/")
def serve():
    conn = get_conn()
    timestamps, values = get_measurements(conn)
    fig = plot(timestamps, values)

    buf = BytesIO()
    fig.savefig(buf, format="png")
    data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return f"<img src='data:image/png;base64,{data}'/>"
