#%%
import datetime as dt

import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import pandas as pd
import seaborn as sns
import numpy as np

#%%
df = pd.read_csv(
    "data/meta_lineages.csv",
    index_col=0,
    parse_dates=[1, 3],
    infer_datetime_format=True,
    cache_dates=True,
    dtype={
        "SEQ_REASON": "category",
        "SENDING_LAB_PC": "category",
        "SEQUENCING_LAB_PC": "category",
        "lineage": "category",
        "scorpio_call": "category",
    },
)
#%%
df.rename(
    columns={
        "DATE_DRAW": "date",
        "PROCESSING_DATE": "processing_date",
        "SEQ_REASON": "reason",
        "SENDING_LAB_PC": "sending_pc",
        "SEQUENCING_LAB_PC": "sequencing_pc",
        "lineage": "lineage",
        "scorpio_call": "scorpio",
    },
    inplace=True,
)
#%%
def plot_omicron_share(df, reason, scale):
    lineages = ["BA.1", "BA.2", "BA.3", "BA.1.1"]

    df_date = df[df.date > "2021-11-18"]

    if reason in ["N", "Y"]:
        df_reason = df_date[df_date.reason == reason]
    elif reason == "NX":
        df_reason = df_date[df_date.reason.isin(["N", "X"])]
    else:
        df_reason = df_date

    df_filter =  df_reason.loc[df_reason['lineage'].isin(lineages)]
   
    df_matches = df_filter[["date", "lineage"]].groupby(["lineage", "date"],observed=True).size().reset_index(name='matches')
    
    daily_all = df_reason.resample("D", on="date")["lineage"].count().reset_index(name='all')


    plot_df = pd.merge(df_matches, daily_all, on="date")
    plot_df["share"] = np.clip(plot_df["matches"] / plot_df["all"], 0.0, 0.999) # 1.0 cannot be shown on logit scale
    plot_df["lineage"].cat.remove_unused_categories(inplace=True)

    fig, ax = plt.subplots(num=None, figsize=(6.75, 4), facecolor="w", edgecolor="k")
    plt.subplots_adjust(left=0.15, right=0.9, top=0.9, bottom=0.25)
    sns.scatterplot(data=plot_df, x="date", y="share", hue="lineage", size="all", sizes=(10, 100))
    
    fig.text(
        0.51,
        0.1,
        f"Datenstand: {str(dt.date.today())} | Datenquelle: RKI Sequenzdaten https://doi.org/10.5281/zenodo.5139363 | Viz: @CorneliusRoemer, @LenaSchimmel",
        size=6,
        va="bottom",
        ha="center",
    )

    if scale == "logit":
        ax.set_yscale("logit")
        ax.set_ylabel("Varianten-Anteil (Logit-Skala)")
    else:
        ax.set_ylabel("Varianten-Anteil")

    ax.set_xlabel("Proben-Datum")

    if reason in [None, "all"]:
        title = "allen Proben"
    elif reason == "N":
        title = "der repräsentativen Surveillance"
    else:
        title = f"Proben vom Typ {reason}"
    ax.set_title(f"Omikron-Varianten-Anteil in Deutschland in {title}")

    ax.get_legend().set_title("Proben-Anzahl")
    handles, labels = ax.get_legend_handles_labels()
    labels[0] = "Variante"
    labels[len(lineages)+1] = "Gesamtzahl"
    ax.legend(handles, labels)

    locator = mdates.AutoDateLocator()
    formatter = mdates.ConciseDateFormatter(locator)
    ax.xaxis.set_major_locator(locator)
    ax.xaxis.set_major_formatter(formatter)
    ax.xaxis.set_minor_locator(ticker.MultipleLocator(base=1.0))
    ax.grid(True, which="major", linewidth=0.25)
    ax.grid(True, which="minor", linewidth=0.1)
    ax.set_axisbelow(True)

    ax.yaxis.set_major_formatter(
        ticker.FuncFormatter(
            lambda y, _: f'{ np.format_float_positional(100*y, trim="-", precision=6).rstrip(".")}%'
        )
    )

    fig.savefig(f"plots/omicron_{reason}_{scale}.png", dpi=300)


#%%
plot_omicron_share(df, "N", "logit")
plot_omicron_share(df, "N", "linear")

plot_omicron_share(df, "all", "logit")
plot_omicron_share(df, "all", "linear")

plot_omicron_share(df, "NX", "logit")
plot_omicron_share(df, "NX", "linear")
