from pathlib import Path

TABLES_DIR = Path("results/tables")
THRESHOLD = 0.01
DEFAULT_CRF = {"libx264": 23, "libx265": 28}


def count_frames(method, content):
    with open(f"data/05_extracted/{method}_{content}.txt") as file:
        return len(file.readlines())


#koszt znaku, BER przy domyślnym CRF, czas na klatkę
def method_card(results):
    natural = results[~results["synthetic"]]
    marked = natural[natural["stage"] == "znak_bez_kompresji"]
    card = marked.groupby("method")[["psnr_y_db", "psnr_u_db", "vmaf"]].mean()
    for codec, crf in DEFAULT_CRF.items():
        ber = natural[(natural["codec"] == codec) & (natural["crf"] == crf)].groupby("method")["ber_voted"]
        card[f"ber_{codec}_crf{crf}_srednia"] = ber.mean()
        card[f"ber_{codec}_crf{crf}_najgorsze"] = ber.max()

    frames = [count_frames(method, content) for method, content in zip(marked["method"], marked["content"])]
    card["embed_ms_na_klatke"] = (1000 * marked["embed_s"] / frames).groupby(marked["method"]).median()
    card["extract_ms_na_klatke"] = (1000 * marked["extract_s"] / frames).groupby(marked["method"]).median()
    card.round(3).to_csv(TABLES_DIR / "method_card.csv")


#BER bez kompresji i najwyższy CRF, przy którym znak jeszcze działa
def content_table(results):
    marked = results[results["stage"] == "znak_bez_kompresji"]
    table = marked.pivot(index="content", columns="method", values="ber_voted").round(2)
    table.columns = [f"{method}_ber_bez_kompresji" for method in table.columns]
    survived = results[(results["stage"] == "po_kompresji") & (results["ber_voted"] <= THRESHOLD)]
    for codec in DEFAULT_CRF:
        best = survived[survived["codec"] == codec].pivot_table(index="content", columns="method", values="crf", aggfunc="max")
        best.columns = [f"{method}_max_crf_{codec}" for method in best.columns]
        table = table.join(best)
    table = table[sorted(table.columns)]
    table.to_csv(TABLES_DIR / "content_table.csv", na_rep="-", float_format="%g")