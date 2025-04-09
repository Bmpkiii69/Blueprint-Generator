**User Guide: Blueprint Generator Pro (Enhanced Context)**

**Daftar Isi:**

1.  Pendahuluan
2.  Persyaratan Sistem
3.  Menjalankan Aplikasi
4.  Memahami Antarmuka Pengguna
5.  Langkah-langkah Penggunaan
    *   5.1 Mengisi Tab "1. Project Setup"
    *   5.2 Mengisi Panel Opsi Kanan (Design, AI, Generation)
    *   5.3 Mengelola Tab "2. Modules"
    *   5.4 Menggunakan Tab "3. Preview & Generate"
6.  Menyimpan & Memuat Konfigurasi
7.  Memahami File Output
8.  Tips untuk Hasil Terbaik
9.  Catatan Penting & Troubleshooting

---

**1. Pendahuluan**

Blueprint Generator Pro adalah alat bantu untuk memulai proyek perangkat lunak baru. Aplikasi ini membantu Anda mendefinisikan detail proyek, konteks bisnis, pilihan teknologi, dan batasan desain secara terstruktur. Kemudian, menggunakan model AI (OpenAI GPT atau Google Gemini), aplikasi ini menghasilkan file-file blueprint awal:

*   `.cursorrules`: Aturan dan prompt sistem untuk AI coding assistant (seperti di editor Cursor).
*   `architecture.md`: Dokumentasi arsitektur perangkat lunak.
*   `project_plan.md`: Rencana pengembangan proyek berbasis tugas.
*   `README.md` (Opsional): File README dasar.
*   `.gitignore` (Opsional): File untuk mengabaikan file/folder dari Git.

Tujuan utamanya adalah memberikan **konteks yang kaya** kepada AI coding assistant yang akan Anda gunakan selanjutnya untuk membangun kode aplikasi, sehingga AI tersebut dapat bekerja lebih efektif dan sesuai arahan.

**2. Persyaratan Sistem**

*   **Python:** Versi 3.7 atau lebih baru.
*   **Library Python:** Instal library yang diperlukan menggunakan pip:
    ```bash
    pip install openai google-generativeai tk
    ```
    *(Catatan: `tk` biasanya sudah termasuk dalam instalasi Python standar di banyak sistem operasi).*
*   **Git (Opsional):** Diperlukan jika Anda ingin menggunakan fitur "Initialize Git Repository". Pastikan `git` terinstal dan dapat diakses dari terminal/command prompt Anda.
*   **API Keys:** Anda memerlukan API key yang valid dari OpenAI dan/atau Google (untuk Gemini) agar dapat menggunakan fitur generasi AI.

**3. Menjalankan Aplikasi**

1.  Simpan kode aplikasi sebagai file Python (misalnya, `blueprint_pro.py`).
2.  Buka terminal atau command prompt Anda.
3.  Navigasi ke direktori tempat Anda menyimpan file tersebut.
4.  Jalankan aplikasi menggunakan perintah:
    ```bash
    python blueprint_pro.py
    ```

**4. Memahami Antarmuka Pengguna**

Jendela utama aplikasi dibagi menjadi dua panel utama (menggunakan `PanedWindow`), yang dapat Anda ubah ukurannya dengan menyeret pembatas di tengah:

*   **Panel Kiri:** Berisi `Notebook` (tab) utama:
    *   **Tab 1. Project Setup:** Tempat Anda memasukkan informasi inti proyek dan detail teknis utama. Tab ini bisa di-scroll jika isinya panjang.
    *   **Tab 2. Modules:** Tempat Anda mendefinisikan modul-modul spesifik aplikasi.
    *   **Tab 3. Preview & Generate:** Tempat Anda melihat pratinjau output, menjalankan generasi file, dan menyimpan/memuat konfigurasi.
*   **Panel Kanan:** Berisi opsi dan konfigurasi tambahan yang relevan dengan proses generasi. Panel ini bisa di-scroll secara vertikal.
    *   **Design & Constraints:** Prinsip desain, NFR, catatan tambahan.
    *   **AI Configuration:** Pilihan provider AI, model, dan input API Key.
    *   **Generation Options:** Pilihan untuk menyertakan tes, README, .gitignore, dan inisialisasi Git.
*   **Status Bar:** Di bagian bawah jendela, menampilkan status operasi saat ini (misalnya, "Ready", "Fetching models...", "Generating file...").

**5. Langkah-langkah Penggunaan**

**5.1 Mengisi Tab "1. Project Setup"**

Ini adalah langkah paling penting untuk memberikan konteks pada AI. Isi selengkap dan sejelas mungkin.

1.  **Core Information:**
    *   **Project Name:** Nama proyek Anda.
    *   **Purpose/Goal:** Jelaskan tujuan utama aplikasi, masalah yang dipecahkan, atau nilai yang diberikan. Ini sangat penting untuk `system` prompt AI.
    *   **Target Users:** Siapa pengguna utama aplikasi ini? (Misal: "Admin gudang", "Pelajar SMA", "Developer lain").
    *   **Main Workflow:** Gambarkan alur kerja utama pengguna secara singkat. (Misal: "User login -> Search product -> Add to cart -> Checkout").
    *   **Core Entities:** Sebutkan objek data inti aplikasi (Misal: "User, Post, Comment, Like").
2.  **Features:**
    *   **Key Features:** Tulis fitur-fitur utama yang dapat dilihat pengguna atau fungsionalitas inti dalam poin-poin atau deskripsi singkat.
3.  **Technical Stack:**
    *   **Application Type:** Pilih jenis aplikasi yang paling sesuai (Web, Mobile, API, dll.). Pilihan ini akan memfilter daftar bahasa pemrograman.
    *   **Programming Languages:** **Pilih satu atau lebih** bahasa yang akan digunakan. Gunakan `Ctrl+Klik` (atau `Cmd+Klik` di Mac) untuk memilih beberapa item satu per satu, atau `Shift+Klik` untuk memilih rentang. Pilihan bahasa akan memfilter opsi Framework dan UI Library.
    *   **Web Framework, UI Library/Framework, State Management:** Pilih opsi yang relevan dari combobox. Daftar ini akan diperbarui secara dinamis berdasarkan bahasa yang dipilih. Pilih "None" jika tidak relevan atau tidak menggunakan.
    *   **Database:** Pilih database utama yang akan digunakan, atau "None".
    *   **Key Libraries/Deps:** Sebutkan library pihak ketiga penting lainnya yang Anda rencanakan untuk digunakan, dipisahkan koma (Misal: "axios, pandas, Lombok, Material-UI").

**5.2 Mengisi Panel Opsi Kanan (Design, AI, Generation)**

Panel di sebelah kanan berisi pengaturan tambahan:

1.  **Design & Constraints:**
    *   **Principles/Patterns:** Sebutkan prinsip desain (SOLID, DRY) atau pola arsitektur (Repository Pattern, MVC, MVVM) yang ingin diikuti AI.
    *   **Key NFRs:** Tulis persyaratan non-fungsional penting (kecepatan, keamanan, aksesibilitas).
    *   **Additional Notes:** Catatan lain yang relevan untuk AI.
2.  **AI Configuration:**
    *   **AI Provider:** Pilih "OpenAI" atau "Gemini".
    *   **API Key:** Masukkan API Key Anda yang valid untuk provider yang dipilih. Input disamarkan (`*`).
    *   **Fetch AI Models:** Klik tombol ini **setelah** memasukkan API Key. Aplikasi akan menghubungi API provider untuk mendapatkan daftar model yang tersedia. Tunggu hingga status bar menunjukkan proses selesai.
    *   **AI Model:** Pilih model AI yang ingin Anda gunakan untuk *menghasilkan* file blueprint dari daftar yang muncul setelah fetch berhasil.
3.  **Generation Options:**
    *   Centang opsi sesuai kebutuhan:
        *   `Include unit tests`: Menambahkan instruksi dan tugas terkait testing di blueprint.
        *   `Generate README.md`: Menghasilkan file README.md dasar.
        *   `Generate .gitignore`: Menghasilkan file .gitignore standar.
        *   `Initialize Git Repository`: Menjalankan `git init` di folder output setelah generasi selesai (membutuhkan Git terinstal).

**5.3 Mengelola Tab "2. Modules"**

Tab ini opsional tetapi sangat disarankan untuk memecah aplikasi menjadi bagian-bagian logis.

1.  **Add Module:**
    *   Masukkan **Nama Modul** yang deskriptif (Misal: "Authentication", "Product Catalog", "Order Processing").
    *   Masukkan **Deskripsi/Tujuan** modul di area teks.
    *   Klik tombol **"+ Add Module"**. Modul akan ditambahkan ke daftar di bawah.
2.  **Remove Module:**
    *   Pilih satu atau lebih modul dari daftar "Added Modules".
    *   Klik tombol **"- Remove Selected Module"**.

Informasi modul ini akan digabungkan dengan "Key Features" saat membuat prompt untuk AI.

**5.4 Menggunakan Tab "3. Preview & Generate"**

Tab terakhir adalah pusat aksi:

1.  **Tombol Aksi:**
    *   **Generate Blueprint Files:** Tombol utama. Klik ini setelah Anda mengisi semua informasi yang relevan. Anda akan diminta memilih **folder kosong** atau folder project baru untuk menyimpan file-file blueprint. Proses generasi akan berjalan di background (lihat status bar). Tombol akan nonaktif selama proses berlangsung.
    *   **Save Project Config:** Menyimpan semua input Anda (termasuk API Keys - **HATI-HATI!**) ke dalam file `.bpgproj` (format JSON) agar bisa dimuat lagi nanti.
    *   **Load Project Config:** Memuat konfigurasi dari file `.bpgproj` yang tersimpan sebelumnya, mengisi ulang semua field.
    *   **Clear Form:** Mengosongkan semua input field dan pilihan ke kondisi awal.
2.  **Preview Area:** Setelah proses "Generate Blueprint Files" selesai, konten file yang berhasil dibuat (`.cursorrules`, `architecture.md`, `project_plan.md`, dll.) akan ditampilkan di area teks ini. Anda bisa meninjau hasilnya di sini.

**Setelah Generasi Selesai:**

*   Sebuah pesan pop-up akan muncul memberitahu status (sukses, sukses dengan error, atau gagal total) dan daftar file yang dibuat/gagal.
*   Jika generasi berhasil (setidaknya sebagian), Anda akan ditanya apakah ingin membuka folder output tempat file-file disimpan.

**6. Menyimpan & Memuat Konfigurasi**

*   Gunakan tombol **"Save Project Config"** untuk menyimpan semua input Anda ke file `.bpgproj`.
*   **PERINGATAN KEAMANAN:** File ini menyimpan API Key Anda dalam **teks biasa**. Jangan bagikan file ini atau simpan di tempat yang tidak aman (seperti repositori Git publik).
*   Gunakan tombol **"Load Project Config"** untuk memuat kembali pengaturan dari file yang tersimpan. Ini akan mengisi ulang semua field, termasuk API key (jika tersimpan). Anda mungkin perlu mengklik "Fetch AI Models" lagi setelah memuat.

**7. Memahami File Output**

File-file yang dihasilkan dirancang untuk digunakan oleh AI coding assistant Anda berikutnya:

*   **`.cursorrules`:** File konfigurasi utama (JSON) untuk AI (khususnya Cursor, tapi bisa diadaptasi). Berisi:
    *   `system`: Prompt sistem tingkat tinggi yang menjelaskan proyek, tujuan, teknologi, dan konteks lainnya ke AI.
    *   `rules`: Aturan teknis spesifik yang harus diikuti AI (keamanan, bahasa, framework, testing, dll.).
*   **`architecture.md`:** Dokumen Markdown yang menjelaskan struktur folder, komponen utama, aliran data (konseptual), dan justifikasi desain. Berfungsi sebagai referensi arsitektur untuk AI.
*   **`project_plan.md`:** Dokumen Markdown berisi rencana pengembangan bertahap dengan checklist tugas yang dapat ditindaklanjuti. Memandu AI tentang urutan implementasi.
*   **`README.md` (jika dipilih):** File perkenalan standar untuk proyek.
*   **`.gitignore` (jika dipilih):** Mengkonfigurasi Git untuk mengabaikan file/folder yang tidak perlu.

**Cara Menggunakan Output:**

1.  Buka folder output di editor kode Anda (misalnya, VS Code dengan ekstensi Cursor, atau editor lain).
2.  Jika menggunakan Cursor, ia secara otomatis akan membaca `.cursorrules`. AI chat akan memiliki konteks proyek dari `system` prompt dan mencoba mengikuti `rules`.
3.  Gunakan chat AI atau fitur "Generate Code" dengan merujuk pada `architecture.md` dan `project_plan.md` (@architecture.md, @project_plan.md di Cursor). Misalnya: "Implement task 1 from project_plan.md for the Authentication module described in architecture.md".

**8. Tips untuk Hasil Terbaik**

*   **Isi Input Selengkap Mungkin:** Semakin detail konteks yang Anda berikan (Purpose, Users, Workflow, Entities, NFRs, Principles, Modules), semakin baik AI dapat memahami dan menghasilkan blueprint yang relevan.
*   **Gunakan Bahasa yang Jelas:** Tulis deskripsi dan catatan dalam bahasa Inggris (karena prompt internal dalam bahasa Inggris) yang jelas dan tidak ambigu.
*   **Pilih Teknologi yang Relevan:** Manfaatkan pemfilteran dinamis untuk memilih bahasa, framework, dan library yang benar-benar akan Anda gunakan.
*   **Definisikan Modul:** Memecah proyek menjadi modul membantu AI memahami struktur dan menghasilkan rencana yang lebih terorganisir.
*   **Tinjau Output:** Selalu periksa file blueprint yang dihasilkan. AI mungkin membuat interpretasi yang sedikit berbeda. Sesuaikan blueprint jika perlu sebelum mulai coding.
*   **Iterasi:** Jika hasil generasi awal kurang memuaskan, coba sesuaikan input (terutama Purpose, Workflow, Entities, Notes) dan generate ulang.

**9. Catatan Penting & Troubleshooting**

*   **Keamanan API Key:** Sekali lagi, berhati-hatilah saat menyimpan/berbagi file `.bpgproj` karena berisi API key Anda.
*   **Error Fetch Models:** Pastikan API key benar, aktif, dan memiliki izin yang cukup. Cek koneksi internet Anda.
*   **Error Generate:** Bisa disebabkan oleh API key salah, model tidak valid, masalah koneksi, kuota API habis, atau prompt yang secara tidak sengaja memicu filter keamanan AI (terutama Gemini). Pesan error biasanya memberikan petunjuk.
*   **Blok Keamanan Gemini:** Jika generasi gagal dengan pesan "SAFETY" atau "blocked", coba ubah kata-kata dalam input Anda (terutama Purpose, Features, Notes) agar tidak terlalu ambigu atau berpotensi melanggar kebijakan konten, lalu generate ulang.
*   **`git init` Gagal:** Pastikan Git terinstal dan ada di PATH sistem Anda.
*   **Performa:** Proses fetch model dan generasi AI memerlukan waktu tergantung pada koneksi internet dan beban server AI. Harap bersabar dan perhatikan status bar.

---

Semoga petunjuk ini membantu Anda menggunakan Blueprint Generator Pro secara efektif!
