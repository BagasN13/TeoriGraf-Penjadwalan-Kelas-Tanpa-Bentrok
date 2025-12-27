import streamlit as st
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import io
import matplotlib.colors as mcolors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors as rl_colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfbase import pdfmetrics

# ----------------------------
# PENGATURAN HALAMAN
# ----------------------------
st.set_page_config(page_title="Penjadwalan Kelas", layout="centered")
st.title("🎓 Penjadwalan Kelas Tanpa Bentrok")
st.write("Setiap kelas dapat memiliki hingga empat mata kuliah (1 wajib + 3 opsional).")

# ----------------------------
# SESSION STATE
# ----------------------------
if "kelas" not in st.session_state:
    st.session_state.kelas = []

if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

if "matkul_list" not in st.session_state:
    st.session_state.matkul_list = []

# Validasi edit index
if (
    st.session_state.edit_index is not None 
    and (st.session_state.edit_index < 0 
    or st.session_state.edit_index >= len(st.session_state.kelas))
):
    st.session_state.edit_index = None


# ----------------------------
# HELPER: konversi warna matplotlib/hex -> reportlab
# ----------------------------
def to_reportlab_color(color_name):
    try:
        rgb = mcolors.to_rgb(color_name)
        return rl_colors.Color(rgb[0], rgb[1], rgb[2])
    except Exception:
        return rl_colors.black


# ----------------------------
# GENERATE PDF
# ----------------------------
def generate_pdf(df, slot_colors):
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    # Register font untuk Unicode (jika tersedia di environment)
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
    except Exception:
        pass

    styles = getSampleStyleSheet()

    # Header tabel
    data = [["Kelas", "Mata Kuliah", "Hari", "Jam"]]

    # Mapping slot → jadwal
    hari_list = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
    jam_list = ["08:00 - 10:00", "10:00 - 12:00", "13:00 - 15:00", "15:00 - 17:00"]

    for _, row in df.iterrows():
        # Slot Waktu format: 'Slot X'
        try:
            slot = int(str(row["Slot Waktu"]).split()[1]) - 1
        except Exception:
            slot = 0
        hari = hari_list[slot % len(hari_list)]
        jam = jam_list[slot % len(jam_list)]
        data.append([row["Kelas"], row["Mata Kuliah"], hari, jam])

    table = Table(data, colWidths=[120, 220, 80, 100])

    # Table styling
    table_style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), rl_colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), rl_colors.black),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, rl_colors.black),
    ])

    # Tambahkan warna background untuk kolom JAM (sesuai slot)
    for i in range(1, len(data)):
        kelas = data[i][0]
        # cari slot dari df berdasarkan kelas
        try:
            slot = int(df[df["Kelas"] == kelas]["Slot Waktu"].values[0].split()[1]) - 1
        except Exception:
            slot = 0
        color_name = slot_colors.get(slot, "black")
        rl_color = to_reportlab_color(color_name)
        table_style.add("BACKGROUND", (3, i), (3, i), rl_color)

    table.setStyle(table_style)
    pdf.build([table])

    buffer.seek(0)
    return buffer


# ----------------------------
# INPUT DATA KELAS (FORM)
# ----------------------------
st.header("Tambah / Edit Data Kelas")

# Ambil default value jika sedang edit
if st.session_state.edit_index is not None:
    data_edit = st.session_state.kelas[st.session_state.edit_index]
    default_kelas = data_edit["kelas"]
    # ensure list of 4 values
    default_mk = data_edit.get("matkuls", [])
    default_mk = default_mk + [""] * (4 - len(default_mk))
else:
    default_kelas = ""
    default_mk = ["", "", "", ""]


with st.form("form_kelas", clear_on_submit=False):

    nama_kelas = st.text_input("Nama Kelas", value=default_kelas)

    st.subheader("Mata Kuliah (1 Wajib, 3 Opsional)")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        mk1 = st.text_input("Matkul 1 (Wajib)", value=default_mk[0])

    with col2:
        mk2 = st.text_input("Matkul 2 (Opsional)", value=default_mk[1])

    with col3:
        mk3 = st.text_input("Matkul 3 (Opsional)", value=default_mk[2])

    with col4:
        mk4 = st.text_input("Matkul 4 (Opsional)", value=default_mk[3])

    submit = st.form_submit_button("Simpan Data Kelas")

    if submit:
        if not mk1.strip() or not nama_kelas.strip():
            st.error("Nama kelas dan Matkul 1 wajib diisi!")
        else:
            # Proses daftar matkul
            daftar_mk = [mk.strip().title() for mk in [mk1, mk2, mk3, mk4] if mk.strip()]

            # Simpan ke session state
            data_baru = {
                "kelas": nama_kelas.strip().title(),
                "matkuls": daftar_mk
            }

            if st.session_state.edit_index is None:
                st.session_state.kelas.append(data_baru)
                st.success("Data kelas berhasil ditambahkan!")
            else:
                st.session_state.kelas[st.session_state.edit_index] = data_baru
                st.session_state.edit_index = None
                st.success("Data kelas berhasil diperbarui!")

            st.rerun()


# ----------------------------
# TAMPILAN LIST KELAS
# ----------------------------
st.header("Daftar Kelas")

if st.session_state.kelas:
    for i, item in enumerate(st.session_state.kelas):

        col1, col2, col3 = st.columns([4, 1, 1])

        with col1:
            mk_join = ", ".join(item["matkuls"]) if item.get("matkuls") else ""
            st.write(f"**{item['kelas']}** — {mk_join}")

        with col2:
            if st.button("Edit", key=f"edit_{i}"):
                st.session_state.edit_index = i
                st.rerun()

        with col3:
            if st.button("Hapus", key=f"hapus_{i}"):
                st.session_state.kelas.pop(i)
                st.success("Data berhasil dihapus!")
                st.rerun()

else:
    st.info("Belum ada data kelas.")


# ----------------------------
# PROSES PENJADWALAN + VISUALISASI + PDF
# ----------------------------
st.header("Proses Pewarnaan Graf")

if st.button("Jalankan Penjadwalan"):

    data = st.session_state.kelas

    if not data:
        st.error("Tambahkan kelas terlebih dahulu.")
    else:
        G = nx.Graph()

        # Tambah node
        for d in data:
            G.add_node(d["kelas"], matkuls=set(d["matkuls"]))

        # Tambah edge jika ada matkul yang sama (set intersection)
        for i in range(len(data)):
            for j in range(i + 1, len(data)):
                mk_i = set(data[i]["matkuls"])
                mk_j = set(data[j]["matkuls"])

                if mk_i.intersection(mk_j):
                    G.add_edge(data[i]["kelas"], data[j]["kelas"])

        # Pewarnaan
        coloring = nx.coloring.greedy_color(G, strategy="largest_first")

        # Warna banyak
        colors = [
            "red", "green", "blue", "orange", "purple", "yellow", "cyan", "pink", "brown",
            "lime", "magenta", "teal", "gold", "navy", "salmon", "violet", "turquoise",
            "coral", "maroon", "olive", "chocolate", "plum", "orchid", "khaki", "lavender",
            "beige", "azure", "indigo", "tan", "#F5FFFA", "seagreen", "tomato", "crimson",
            "slateblue", "lightgreen", "lightblue", "greenyellow", "darkorange", "steelblue",
            "skyblue", "hotpink", "darkcyan", "darkmagenta", "darkred", "darkblue",
            "darkgreen", "chartreuse", "deeppink", "mediumpurple", "mediumvioletred",
            "cadetblue", "darkkhaki", "sandybrown", "thistle", "palegreen", "lightsalmon",
            "powderblue", "lightsteelblue", "lightcoral", "mediumseagreen", "royalblue",
            "mediumslateblue", "mediumorchid", "darksalmon", "lightskyblue", "lightseagreen",
        ]

        # Node colors berdasarkan coloring (urut sesuai node_list)
        node_list = list(G.nodes)
        node_colors = [colors[coloring[n] % len(colors)] for n in node_list]

        hasil = []
        for kelas, slot in coloring.items():
            hasil.append([kelas, ", ".join(G.nodes[kelas]["matkuls"]), f"Slot {slot + 1}"])

        df = pd.DataFrame(hasil, columns=["Kelas", "Mata Kuliah", "Slot Waktu"])

        st.success("Penjadwalan berhasil!")
        st.dataframe(df.sort_values("Slot Waktu"), use_container_width=True)

        # Visualisasi Graf
        st.subheader("Graf Konflik Mata Kuliah")

        fig, ax = plt.subplots(figsize=(8, 6))
        pos = nx.spring_layout(G, seed=42)

        nx.draw_networkx_nodes(G, pos, node_color=node_colors, node_size=2000, ax=ax)
        nx.draw_networkx_labels(G, pos, font_size=10, font_weight="bold", ax=ax)
        nx.draw_networkx_edges(G, pos, width=1.5, edge_color="black", ax=ax)

        ax.set_axis_off()
        st.pyplot(fig)

        # Mapping slot -> color (ambil warna dari node yang punya slot itu)
        slot_colors = {}
        for n_idx, n in enumerate(node_list):
            slot = coloring[n]
            if slot not in slot_colors:
                slot_colors[slot] = node_colors[n_idx]

        # Generate PDF
        pdf_file = generate_pdf(df, slot_colors)

        st.download_button(
            label="📄 Download Jadwal (PDF)",
            data=pdf_file,
            file_name="jadwal_kelas.pdf",
            mime="application/pdf"
        )

st.write("---")
st.write("Dibuat untuk penjadwalan kelas berbasis Graph Coloring.")
