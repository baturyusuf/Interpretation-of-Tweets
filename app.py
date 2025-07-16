"""Streamlit Tweet Viewer – v6.1 (Seçim Tutarlılığı)
====================================================
* **Seçim hatası düzeltildi:** `st_aggrid` bazı sürümlerde `selected_rows`’u
  DataFrame olarak döndürüyor. Artık hem **list** hem **DataFrame** senaryosu
  işlendi ve seçilen tweet’in indeksi `int()`’e dönüştürülerek `df.loc` ile
  uyumlu hale getirildi.
* Hiçbir diğer işlev değişmedi.
"""

from __future__ import annotations
import io
import os
import re
import random
import string
from typing import Dict, List, Tuple, Union

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

st.set_page_config(page_title="Tweet Viewer", layout="wide", page_icon="🐦")
st.title("🐦 Tweet İçeriği İnceleyici")

DEFAULT_XLSX_PATH = "otomatik_kodlama_sonuclari.xlsx"

UI_LABELS: Dict[str, str] = {
    "Belge": "Belge (Sıra No.)",
    "Kodlu Bölümler": "Tweet Metni",
    "Belge grubu": "Profil / Grup",
    "Determination of Events": "Olay Türü",
    "Site Visit": "Ziyaret",
    "Kabiliyet": "Kabiliyet",
    "Tematik Analiz": "Tematik Analiz",
    "Binary": "Binary",
}

HIER_COLS = ["Determination of Events", "Tematik Analiz", "Kabiliyet"]
SITE_VISIT_COL = "Site Visit"
BINARY_META_COL = "Binary"

# ────────────────────────────── Yardımcılar ──────────────────────────

def is_missing(val) -> bool:
    if pd.isna(val):
        return True
    s = str(val).strip()
    return s == "" or s == "//" or s.lower() in {"na", "nan", "null"}


def random_word(k: int = 6) -> str:
    return "".join(random.choices(string.ascii_lowercase, k=k))


def parse_binary_field(text: str) -> List[Tuple[str, str]]:
    pairs = re.findall(r"([^:]+):\s*([01])", text)
    return [(k.strip(), "Evet" if v == "1" else "Hayır") for k, v in pairs]


def load_dataframe(uploaded_file):
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
    elif os.path.exists(DEFAULT_XLSX_PATH):
        df = pd.read_excel(DEFAULT_XLSX_PATH)
    else:
        st.error("Excel dosyası bulunamadı. Sol kenardan dosya yükleyiniz.")
        st.stop()

    for col in list(df.columns):
        if "Determination of Events" in col and col != "Determination of Events":
            df.rename(columns={col: "Determination of Events"}, inplace=True)

    for c in UI_LABELS:
        if c not in df.columns:
            df[c] = pd.NA

    df["_preview"] = df["Kodlu Bölümler"].fillna("(Boş tweet)").astype(str).str.slice(0, 150)
    return df


def hierarchy_markdown(text: str) -> str:
    parts = [p.strip() for p in text.split(">") if p.strip()]
    return "\n".join(" " * 4 * i + f"- **{p}**" for i, p in enumerate(parts))


def parse_site_visit(val: str) -> str:
    parts = [p.strip() for p in val.split(">") if p.strip()]
    return parts[-1] if parts else "Bilinmiyor"

# ───────────────────────────── Kenar Çubuğu ─────────────────────────
with st.sidebar:
    st.header("Excel Dosyası Yükle")
    uploaded_file = st.file_uploader("Tweet verisini içeren Excel dosyası", type=["xlsx"])

    # session_state içinde df yoksa mutlaka yükle
    if "df" not in st.session_state:
        st.session_state.df = load_dataframe(uploaded_file)
        st.session_state.uploaded_file = uploaded_file

    # eğer yeni bir dosya atandıysa yeniden yükle
    elif uploaded_file is not None and uploaded_file != st.session_state.uploaded_file:
        st.session_state.df = load_dataframe(uploaded_file)
        st.session_state.uploaded_file = uploaded_file

    if "df" in st.session_state:
        st.markdown("---")
        df_to_save = st.session_state.df

        # Bellekte Excel dosyasını oluştur
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="xlsxwriter") as writer:
            df_to_save.to_excel(writer, index=False, sheet_name="Sheet1")
        buffer.seek(0)

        # İndirme butonu
        st.download_button(
            label="Excel Olarak İndir",
            data=buffer,
            file_name="tweet_verisi.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )



# ─────────────────────────────── Ana Düzen ──────────────────────────
left, right = st.columns([0.38, 0.62], gap="small")

with left:
    st.subheader("Tweetler (kaydırılabilir)")
    q = st.text_input("Ara", placeholder="tweet içinde kelime…")
    view_df = st.session_state.df if not q else st.session_state.df[
        st.session_state.df["Kodlu Bölümler"].str.contains(q, case=False, na=False)]

    grid_df = view_df.reset_index(names="_idx")[["_idx", "_preview"]]
    gb = GridOptionsBuilder.from_dataframe(grid_df)
    gb.configure_column("_preview", header_name="Tweet", autoHeight=True, wrapText=True)
    gb.configure_column("_idx", hide=True)
    gb.configure_selection("single", use_checkbox=False)

    resp = AgGrid(
        grid_df,
        gridOptions=gb.build(),
        height=600,
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        data_return_mode=DataReturnMode.AS_INPUT,
    )

    sel = resp["selected_rows"]
    idx_val: Union[int, None] = None
    if isinstance(sel, list) and sel:
        idx_val = sel[0]["_idx"]
    elif isinstance(sel, pd.DataFrame) and not sel.empty:
        idx_val = sel.iloc[0]["_idx"]

    if idx_val is not None:
        st.session_state.selected_idx = int(idx_val)
    elif "selected_idx" not in st.session_state:
        st.session_state.selected_idx = None

with right:
    if st.session_state.selected_idx is None:
        st.info("Soldan bir tweet seçiniz.")
        st.stop()

    row = st.session_state.df.loc[int(st.session_state.selected_idx)]

    st.markdown("### Tweet Metni")
    st.write(row["Kodlu Bölümler"] if not is_missing(row["Kodlu Bölümler"]) else "(Boş)")

    st.markdown("---")
    st.markdown("### Tweet Bilgileri")

    for col in HIER_COLS:
        container = st.container()
        container.markdown(f"#### {UI_LABELS[col]}")
        val = row[col]
        if is_missing(val):
            btn_key = f"ai_{col}_{row.name}"
            print(st.session_state.df.head())
            if container.button("Yapay Zeka ile Üret", key=btn_key):
                generated = random_word()
                st.session_state.df.at[row.name, col] = generated
                st.rerun()

                print(st.session_state.df.head())

            val = st.session_state.df.at[row.name, col]

        if not is_missing(val):
            container.markdown(hierarchy_markdown(str(val)), unsafe_allow_html=True)

    st.markdown("#### Ziyaret")
    vsv = row[SITE_VISIT_COL]
    st.write(parse_site_visit(str(vsv)) if not is_missing(vsv) else "Bilinmiyor")

    st.markdown("#### Binary")
    vbin = row[BINARY_META_COL]
    if is_missing(vbin):
        st.write("Bilinmiyor")
    else:
        for k, yn in parse_binary_field(str(vbin)):
            st.write(f"- **{k}:** {yn}")

    for col in ["Belge", "Belge grubu"]:
        st.markdown(f"#### {UI_LABELS[col]}")
        st.write(row[col] if not is_missing(row[col]) else "Bilinmiyor")
