import pandas as pd
import numpy as np

DEFAULT_FILE_PATH = "hornos_mecanica_tiempos.xlsx"


COL_ACERO = "RH-Acero"
COL_HORNO = "RH- Horno"

COL_ELONG_MEAN = "elong_mean"
COL_ELONG_STD  = "elong_std"

COL_RES_MEAN   = "res_mean"
COL_RES_STD    = "res_std"

COL_CED_MEAN   = "ced_mean"
COL_CED_STD    = "ced_std"

COL_T_MEAN     = "t_neto_mean"



def safe_ratio(mean, std):
    #medias/stds
    mean = mean.astype(float)
    std = std.astype(float)
    ratio = mean / std.replace(0, np.nan)
    return ratio


def minmax_normalize(series):
    s = series.astype(float)
    min_val = s.min()
    max_val = s.max()
    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        return pd.Series(0.5, index=s.index)
    return (s - min_val) / (max_val - min_val)



def load_hornos_data(file_path=DEFAULT_FILE_PATH):

    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()  # por si hay espacios raros


    required_cols = [
        COL_ACERO, COL_HORNO,
        COL_ELONG_MEAN, COL_ELONG_STD,
        COL_RES_MEAN,   COL_RES_STD,
        COL_CED_MEAN,   COL_CED_STD,
        COL_T_MEAN
    ]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan estas columnas en el Excel: {missing}")

    return df


def compute_scores(
    df,
    w_elong=0.4,
    w_res=0.3,
    w_ced=0.1,
    w_time=0.2,
):


    df = df.copy()

    # mean / std
    df["elong_perf_raw"] = safe_ratio(df[COL_ELONG_MEAN], df[COL_ELONG_STD])
    df["res_perf_raw"]   = safe_ratio(df[COL_RES_MEAN],   df[COL_RES_STD])
    df["ced_perf_raw"]   = safe_ratio(df[COL_CED_MEAN],   df[COL_CED_STD])

    for col in ["elong_perf_raw", "res_perf_raw", "ced_perf_raw"]:
        df[col] = df[col].fillna(df[col].median())

#normalizacion
    df["elong_norm"] = minmax_normalize(df["elong_perf_raw"])
    df["res_norm"]   = minmax_normalize(df["res_perf_raw"])
    df["ced_norm"]   = minmax_normalize(df["ced_perf_raw"])


    t_norm = minmax_normalize(df[COL_T_MEAN])
    df["time_norm"] = 1.0 - t_norm

    df["score"] = (
        w_elong * df["elong_norm"]
        + w_res * df["res_norm"]
        + w_ced * df["ced_norm"]
        + w_time * df["time_norm"]
    )

    return df



def best_oven_per_steel(df_scores):

    idx_best = df_scores.groupby(COL_ACERO)["score"].idxmax()

    best = df_scores.loc[idx_best].copy()

    best = best.sort_values(COL_ACERO).reset_index(drop=True)

    return best




if __name__ == "__main__":

    df_raw = load_hornos_data()

#calculo scores
    df_scores = compute_scores(
        df_raw,
        w_elong=0.4,
        w_res=0.3,
        w_ced=0.1,
        w_time=0.2,
    )

    df_best = best_oven_per_steel(df_scores)

    df_scores_sorted = df_scores.sort_values(
        by=[COL_ACERO, "score"],
        ascending=[True, False]
    )

    print("Tabla completa (primeras filas):")
    print(df_scores_sorted.head(10))

    print("\nMejor horno por acero:")
    print(df_best)


