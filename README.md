Penjadwalan Kelas Tanpa Bentrok
Aplikasi berbasis Streamlit untuk menyusun jadwal kelas otomatis tanpa bentrok menggunakan pendekatan Graph Coloring. Konflik ditentukan berdasarkan mata kuliah yang sama antar kelas.

Fitur
•	Input data kelas dan mata kuliah
•	Edit dan hapus data kelas
•	Penjadwalan otomatis tanpa bentrok
•	Visualisasi graf konflik mata kuliah
•	Ekspor jadwal ke PDF

Teknologi
Aplikasi ini dikembangkan dan diuji menggunakan versi library berikut:
•	Python 3.x
•	Streamlit 1.50.0
•	Pandas 2.2.2
•	NetworkX 3.3
•	Matplotlib 3.9.0
•	ReportLab 4.4.4

Instalasi
Pastikan Python sudah terpasang, kemudian jalankan:
pip install streamlit pandas networkx matplotlib reportlab

Menjalankan Aplikasi
streamlit run app.py
Aplikasi dapat diakses melalui browser pada alamat:
http://localhost:8501

Cara Penggunaan
1.	Masukkan nama kelas dan minimal satu mata kuliah (wajib)
2.	Tambahkan mata kuliah opsional jika diperlukan
3.	Klik tombol Jalankan Penjadwalan
4.	Sistem akan menghasilkan jadwal dan graf konflik
5.	Jadwal dapat diunduh dalam format PDF

Konsep Dasar
•	Node: Kelas
•	Edge: Konflik mata kuliah yang sama
•	Warna / Slot: Waktu perkuliahan
Penjadwalan dilakukan menggunakan algoritma Greedy Graph Coloring dari library NetworkX.

Output
•	Tabel jadwal kelas
•	Visualisasi graf konflik mata kuliah
•	File jadwal dalam format PDF

Catatan
•	Data disimpan sementara menggunakan session state
•	Slot waktu bertambah otomatis sesuai jumlah konflik
•	Algoritma greedy bersifat heuristik dan efisien

