#%%
import datetime as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns

import requests

url_base = "https://api.github.com/repos/robert-koch-institut/SARS-CoV-2-Sequenzdaten_aus_Deutschland/commits?per_page=50&path="
files = [
     { "short": "Entwicklungslinien", "long": "SARS-CoV-2-Entwicklungslinien_Deutschland.csv.xz" },  
     { "short": "Metadaten (csv)", "long": "SARS-CoV-2-Sequenzdaten_Deutschland.csv.xz" }, 
     { "short": "Sequenzdaten (fasta)", "long": "SARS-CoV-2-Sequenzdaten_Deutschland.fasta.xz" }
]

records = []

for file in files:
    data = requests.get(url_base + file["long"]).json()
    for line in data:
        records.append({ "file": file["short"], "datetime": dt.datetime.fromisoformat(line['commit']['author']['date'][:-1])});

df = pd.DataFrame(records)

# make a new column with one date and the time from up_dt
df["time"] = df["datetime"].apply(lambda d: dt.datetime(2022, 1, 1, d.hour, d.minute, d.second, d.microsecond))
df["date"] = df["datetime"].apply(lambda d: dt.datetime(d.year, d.month, d.day))


fig, ax = plt.subplots(num=None, figsize=(6.75, 4), facecolor="w", edgecolor="k")
plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.25)


# y axis
ax.set_ylabel('Uhrzeit')
d1 = str(df.time.min().date())+' 00:00'
d2 = str(df.time.min().date() + dt.timedelta(days=1))
y_time = pd.date_range(start=d1, end=d2,freq='H')
ax.set_ylim([y_time.min(), y_time.max()])
ax.yaxis.set_major_locator(mdates.HourLocator(byhour=range(24), interval=2))
ax.yaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))

# x axis
ax.set_xlim([dt.date.today() - dt.timedelta(days=14), dt.date.today()  + dt.timedelta(days=1)])
ax.set_xlabel('Datum')
#locator = mdates.AutoDateLocator()
locator = ticker.MultipleLocator(base=1.0)
formatter = mdates.ConciseDateFormatter(locator)
ax.xaxis.set_major_locator(locator)
ax.xaxis.set_major_formatter(formatter)
ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1.0))
ax.grid(True, which="major", linewidth=0.25)
ax.grid(True, which="minor", linewidth=0.1)
ax.set_axisbelow(True)

sns.scatterplot(data=df, x="date", y="time", hue="file", style="file", markers=['<', 'D', 'v'])

filename = f"plots/commits.png"

fig.text(
    0.51,
    0.1,
    f"Datenstand: {str(dt.date.today())} | Datenquelle: RKI Sequenzdaten https://doi.org/10.5281/zenodo.5139363 | Viz: @LenaSchimmel",
    size=6,
    va="bottom",
    ha="center",
)
fig.text(
    0.51,
    0.065,
    f"Tagesaktuelle Fassung unter https://github.com/lenaschimmel/desh-data",
    size=6,
    va="bottom",
    ha="center",
)
fig.text(
    0.51,
    0.03,
    f"Name dieser Datei: {filename}",
    size=6,
    va="bottom",
    ha="center",
)

fig.savefig(filename, dpi=300)
