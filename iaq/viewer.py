import sqlite3
import sys

import matplotlib.pyplot as plt
import pandas as pd

db_file = sys.argv[1]
conn = sqlite3.connect(db_file)
measurements = pd.read_sql(
    "select timestamp, name as size, value from measurements",
    conn,
    parse_dates=["timestamp"],
)

fig, ax = plt.subplots()

measurements.pivot(index="timestamp", columns=["size"], values="value").resample(
    "15Min", closed="right", label="right"
).mean()[["PM1.0", "PM2.5", "PM10.0"]].plot(ax=ax)

ax.set_xlabel("Timestamp")
ax.set_ylabel(r"Concentration ($\mu$g/m$^3$)")
plt.show()
