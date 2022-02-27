# %%
import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
import seaborn as sns

# %%
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
# %%

def make_graph(df, filter_reason):
    #df = df[(df.date > "2021-11-18") & (df.date < "2022-02-01")]
    df_filtered = df
    if filter_reason:
        df_filtered = df[(df.reason == filter_reason)]
    df_filtered["delay"] = (df_filtered["processing_date"] - df_filtered["date"]).dt.days
    df_filtered.delay.describe()

    # %%
    # Inspired by https://stackoverflow.com/a/30305331/7483211
    sns.set_theme()
    max_days = 45
    bins = np.arange(0, max_days + 1, 1)

    fig, ax = plt.subplots(figsize=(7, 4))
    _, bins, patches = plt.hist(np.clip(df_filtered.delay, bins[0], bins[-1]), density=True, bins=bins)
    xlabels = bins[0:-1].astype(str)
    for x in range(1, len(xlabels), 2):
        xlabels[x] = "";
    xlabels[-1] += "+"

    N_labels = len(xlabels)
    plt.xlim([0, max_days])
    #ax.xaxis.set_major_locator(ticker.MultipleLocator(2))
    plt.xticks(np.arange(N_labels) + 0.5)
    ax.set_xticklabels(xlabels)

    nice_formatter = ticker.FuncFormatter(
        lambda y, _: f'{ np.format_float_positional(100*y, trim="-", precision=6).rstrip(".")}%'
    )
    ax.yaxis.set_major_formatter(nice_formatter)

    reason_string = "alle Proben"
    if filter_reason == "X":
        reason_string = "X = Grund unbekannt"
    if filter_reason == "N":
        reason_string = "N = z.B. representative Surveillance"
    if filter_reason == "Y":
        reason_string = "Y = Verdacht auf nicht spezifizierte Variante"
    if filter_reason == "A":
        reason_string = "A = Verdacht auf spezifierte Variante(n)"

    ax.set_xlabel("Verzug zwischen Probenentnahme und Sequenzierung (Tage)")
    ax.set_ylabel("Anteil der Sequenzen")
    ax.set_title(f"Verarbeitungsverzug ({reason_string})")
    plt.figtext(
        0.97,
        -0.02,
        f"Datenstand: {str(dt.date.today())}"
        + " | Datenquelle: RKI Sequenzdaten https://doi.org/10.5281/zenodo.5139363"
        + " | Analyse: @CorneliusRoemer, @LenaSchimmel",
        size=6,
        va="bottom",
        ha="right",
    )
    fig.tight_layout()
    suffix = "";
    if filter_reason:
        suffix = "_" + filter_reason
    fig.savefig(f"plots/sequencing_delay{suffix}.png", dpi=200, bbox_inches="tight", pad_inches=0.3)

make_graph(df, False)
make_graph(df, "Y")
make_graph(df, "N")
make_graph(df, "X")
make_graph(df, "A")