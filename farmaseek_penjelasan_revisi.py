import csv

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.obat_list = []

class ObatTrie:
    def __init__(self):
        self.root = TrieNode()
        self.detail_map = {}
        self.penyakit_map = {}

    def insert(self, nama_obat, detail, penyakit):
        node = self.root
        for char in nama_obat.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
            node.obat_list.append(nama_obat)
        node.is_end = True
        self.detail_map[nama_obat] = detail
        for kata in penyakit.lower().split():
            self.penyakit_map.setdefault(kata, []).append(nama_obat)

    def cari_by_awalan(self, awalan):
        node = self.root
        for char in awalan.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return sorted(set(node.obat_list))

    def cari_by_gejala(self, keyword):
        keyword = keyword.strip().lower()
        hasil = []
        for kata, obat_list in self.penyakit_map.items():
            if keyword in kata:
                hasil.extend(obat_list)
        return sorted(set(hasil))

    def get_detail(self, nama_obat):
        return self.detail_map.get(nama_obat, None)


def muat_data_dari_csv(nama_file):
    trie = ObatTrie()
    try:
        with open(nama_file, newline='', encoding='utf-8') as file:
            next(file)  # Lewati header
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                nama = row['Nama Obat'].strip()
                gangguan = row.get('Gangguan', row.get('Manfaat', '')).strip()
                if not nama:
                    continue
                detail = {
                    "Golongan": row['Golongan'],
                    "Kategori": row['Kategori'],
                    "Manfaat": row['Manfaat'],
                    "Pengguna": row['Pengguna'],
                    "Bentuk": row['Bentuk obat'],
                    "Gangguan": gangguan,
                }
                trie.insert(nama, detail, gangguan)
    except Exception as e:
        print(f"Gagal memuat CSV: {e}")
    return trie


def tampilkan_detail(detail, nama_obat):
    if detail:
        print(f"\nDetail Obat: {nama_obat}")
        for k, v in detail.items():
            print(f"{k}: {v}")
        print()
    else:
        print("Detail obat tidak ditemukan.\n")


def main():
    print("Memuat data obat...")
    data_obat = muat_data_dari_csv("data obat baru fix.csv")
    print("Data obat berhasil dimuat.\n")

    while True:
        print("Menu:")
        print("1. Cari Obat Berdasarkan Nama")
        print("2. Cari Obat Berdasarkan Gejala")
        print("3. Keluar")

        pilihan = input("Pilih menu (1/2/3): ").strip()
        if pilihan == '1':
            awalan = input("Masukkan awalan nama obat: ").strip()
            if not awalan:
                print("Awalan tidak boleh kosong.\n")
                continue
            hasil = data_obat.cari_by_awalan(awalan)
            if not hasil:
                print(f"Tidak ditemukan obat dengan awalan '{awalan}'.\n")
                continue
            print("\nHasil pencarian:")
            for idx, obat in enumerate(hasil, 1):
                print(f"{idx}. {obat}")
            nomor = input("Pilih nomor obat untuk melihat detail (atau tekan Enter untuk kembali): ").strip()
            if nomor.isdigit():
                nomor = int(nomor)
                if 1 <= nomor <= len(hasil):
                    nama_obat = hasil[nomor - 1]
                    detail = data_obat.get_detail(nama_obat)
                    tampilkan_detail(detail, nama_obat)
                else:
                    print("Nomor tidak valid.\n")
            else:
                print()
        elif pilihan == '2':
            keyword = input("Masukkan kata kunci gejala/penyakit: ").strip()
            if not keyword:
                print("Kata kunci tidak boleh kosong.\n")
                continue
            hasil = data_obat.cari_by_gejala(keyword)
            if not hasil:
                print(f"Tidak ada obat untuk gejala '{keyword}'.\n")
                continue
            print("\nHasil pencarian:")
            for idx, obat in enumerate(hasil, 1):
                print(f"{idx}. {obat}")
            nomor = input("Pilih nomor obat untuk melihat detail (atau tekan Enter untuk kembali): ").strip()
            if nomor.isdigit():
                nomor = int(nomor)
                if 1 <= nomor <= len(hasil):
                    nama_obat = hasil[nomor - 1]
                    detail = data_obat.get_detail(nama_obat)
                    tampilkan_detail(detail, nama_obat)
                else:
                    print("Nomor tidak valid.\n")
            else:
                print()
        elif pilihan == '3':
            print("Terima kasih. Program selesai.")
            break
        else:
            print("Pilihan tidak valid, coba lagi.\n")


if __name__ == "__main__":
    main()
