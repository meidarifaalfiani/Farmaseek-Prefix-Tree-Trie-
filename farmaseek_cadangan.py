import tkinter as tk
from tkinter import ttk, messagebox
import networkx as nx
import matplotlib.pyplot as plt
import csv

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.nama_obat_list = []

class Trie:
    def __init__(self):
        self.root = TrieNode()
        self.detail_map = {}

    def insert(self, key, obat_name, detail=None):
        node = self.root
        for huruf in key.lower():
            if huruf not in node.children:
                node.children[huruf] = TrieNode()
            node = node.children[huruf]
            node.nama_obat_list.append(obat_name)
        node.is_end = True
        if detail:
            self.detail_map[obat_name] = detail

    def cari_awalan_obat(self, prefix):
        node = self.root
        for huruf in prefix.lower():
            if huruf not in node.children:
                return []
            node = node.children[huruf]
        return sorted(set(node.nama_obat_list))

    def get_detail(self, obat_name):
        return self.detail_map.get(obat_name)

def muat_data_csv(nama_file):
    trie_nama = Trie()
    trie_gejala = Trie()
    with open(nama_file, newline='', encoding='utf-8') as file:
        next(file)
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            nama = row['Nama Obat'].strip()
            if not nama:
                continue
            detail = {
                "Golongan": row.get('Golongan', '').strip(),
                "Kategori": row.get('Kategori', '').strip(),
                "Manfaat": row.get('Manfaat', '').strip(),
                "Pengguna": row.get('Pengguna', '').strip(),
                "Bentuk": row.get('Bentuk obat', '').strip(),
                "Gangguan": row.get('Gangguan', '').strip(),
            }
            trie_nama.insert(nama, nama, detail)
            gangguan = detail["Gangguan"].lower().strip(",.-")
            if gangguan:
                trie_gejala.insert(gangguan, nama)
    return trie_nama, trie_gejala

def build_graph_from_trie(trie_root, prefix=""):
    G = nx.DiGraph()

    def add_edges(node, current_prefix):
        for char, child in node.children.items():
            new_prefix = current_prefix + char
            G.add_edge(current_prefix, new_prefix)
            add_edges(child, new_prefix)

    node = trie_root
    for char in prefix.lower():
        if char in node.children:
            node = node.children[char]
        else:
            print(f"Prefix '{prefix}' tidak ditemukan.")
            return None

    add_edges(node, prefix)
    return G

def visualisasikan_prefix(trie, prefix=""):
    G = build_graph_from_trie(trie.root, prefix)
    if G is None:
        return

    pos = nx.spring_layout(G, k=0.5, iterations=100)
    plt.figure(figsize=(12, 8))
    nx.draw(G, pos, with_labels=True, node_size=1200,
            node_color="lightblue", font_size=10, arrows=True)
    plt.title(f"Visualisasi Trie dari Awalan '{prefix}'", fontsize=14)
    plt.show()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Farmaseek - Aplikasi Pencarian Obat Berbasis Trie")
        self.geometry("800x600")
        self.configure(bg="#f0f8ff")
        # Styling
        style = ttk.Style(self)
        style.theme_use('default')
        style.configure("TFrame", background="#f0f8ff")
        style.configure("TLabel", background="#f0f8ff", font=("Segoe UI", 12))
        style.configure("TButton", font=("Segoe UI", 11, "bold"), padding=6)
        style.configure("TEntry", padding=5)
        style.map("TButton",
                  background=[("active", "#4682b4"), ("!disabled", "#6495ed")],
                  foreground=[("active", "white"), ("!disabled", "white")])
        
        self.trie_nama = trie_nama
        self.trie_gejala = trie_gejala

        self.frames = {}
        for F in (HomeFrame, FrameCariObat, FrameCariGejala):
            frame = F(self)
            self.frames[F] = frame
            frame.place(relwidth=1, relheight=1)

        self.show_frame(HomeFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

class HomeFrame(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg="#f0f8ff")
        ttk.Label(self, text="Selamat Datang di Farmaseek", font=("Fredoka", 16, "bold")).pack(pady=20)
        ttk.Label(self, text="Silahkan mencari obat yang anda inginkan!", font=("Fredoka", 15, "bold")).pack(pady=10)
        ttk.Button(self, text="\U0001F50D Cari berdasarkan nama obat", command=lambda: master.show_frame(FrameCariObat)).pack(pady=10)
        ttk.Button(self, text="\U0001F4A1 Cari berdasarkan gejala", command=lambda: master.show_frame(FrameCariGejala)).pack(pady=10)

class FrameCariObat(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg="#f0f8ff")
        ttk.Label(self, text="Masukkan awalan nama obat:", font=("Segoe UI", 12)).pack(pady=10)

        self.entry = ttk.Entry(self, width=30)
        self.entry.pack(pady=5)

        # Tombol Cari dan Visualisasi
        tombol_frame = ttk.Frame(self)
        tombol_frame.pack(pady=5)

        ttk.Button(tombol_frame, text="Cari \U0001F50D", command=self.cari_obat).grid(row=0, column=0, padx=5)
        ttk.Button(tombol_frame, text="Visualisasi Trie berdasarkan Nama Obat \U0001F4C8", command=self.visualisasi_trie).grid(row=0, column=1, padx=5)

        self.listbox = tk.Listbox(self, width=80, height=15,
                                  bg="#ffffff", fg="#000080",
                                  font=("Poppins", 11),
                                  selectbackground="#f0f8ff",
                                  selectforeground="black")
        self.listbox.pack(pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.tampilkan_detail)

        ttk.Button(self, text="\u2B05 Kembali", command=lambda: master.show_frame(HomeFrame)).pack(pady=10)

    def cari_obat(self):
        keyword = self.entry.get().strip()
        self.listbox.delete(0, tk.END)
        if not keyword:
            messagebox.showwarning("Peringatan", "Masukkan awalan nama obat!")
            return
        hasil = self.master.trie_nama.cari_awalan_obat(keyword)
        if hasil:
            for h in hasil:
                self.listbox.insert(tk.END, h)
        else:
            self.listbox.insert(tk.END, f"Tidak ditemukan hasil untuk '{keyword}'")

    def visualisasi_trie(self):
        prefix = self.entry.get().strip()
        if not prefix:
            messagebox.showwarning("Peringatan", "Masukkan awalan untuk divisualisasikan!")
            return
        visualisasikan_prefix(self.master.trie_nama, prefix)

    def tampilkan_detail(self, event):
        if not self.listbox.curselection():
            return
        selected = self.listbox.get(self.listbox.curselection())
        detail = self.master.trie_nama.get_detail(selected)
        if detail:
            teks = f"Nama Obat: {selected}\n"
            for k, v in detail.items():
                teks += f"{k}: {v}\n"
            messagebox.showinfo("Detail Obat", teks)

class FrameCariGejala(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.configure(bg="#f0f8ff")
        ttk.Label(self, text="Masukkan awalan gejala/penyakit:", font=("Segoe UI", 12)).pack(pady=10)
        self.entry = ttk.Entry(self, width=30)
        self.entry.pack(pady=5)
 # Tombol Cari dan Visualisasi
        tombol_frame = ttk.Frame(self)
        tombol_frame.pack(pady=5)
        ttk.Button(tombol_frame, text="Cari \U0001F48A", command=self.cari_obat).grid(row=0, column=0, padx=5)
        ttk.Button(tombol_frame, text="Visualisasi Trie berdasarkan Gejala Penyakit \U0001F4C8", command=self.visualisasi_trie).grid(row=0, column=1, padx=5)

        self.listbox = tk.Listbox(self, width=80, height=15,
                                  bg="#ffffff", fg="#000080",
                                  font=("Poppins", 11),
                                  selectbackground="#f0f8ff",
                                  selectforeground="black")
        self.listbox.pack(pady=10)
        self.listbox.bind("<<ListboxSelect>>", self.tampilkan_detail)

        ttk.Button(self, text="\u2B05 Kembali", command=lambda: master.show_frame(HomeFrame)).pack(pady=10)

    def cari_obat(self):
        keyword = self.entry.get().strip()
        self.listbox.delete(0, tk.END)
        if not keyword:
            messagebox.showwarning("Peringatan", "Masukkan awalan gejala/penyakit!")
            return
        hasil = self.master.trie_gejala.cari_awalan_obat(keyword)
        if hasil:
            for h in hasil:
                self.listbox.insert(tk.END, h)
        else:
            self.listbox.insert(tk.END, f"Tidak ditemukan obat untuk gejala '{keyword}'")
    
    def visualisasi_trie(self):
        prefix = self.entry.get().strip()
        if not prefix:
            messagebox.showwarning("Peringatan", "Masukkan awalan untuk divisualisasikan!")
            return
        visualisasikan_prefix(self.master.trie_gejala, prefix)

    def tampilkan_detail(self, event):
        if not self.listbox.curselection():
            return
        selected = self.listbox.get(self.listbox.curselection())
        detail = self.master.trie_nama.get_detail(selected)
        if detail:
            teks = f"Nama Obat: {selected}\n"
            for k, v in detail.items():
                teks += f"{k}: {v}\n"
            messagebox.showinfo("Detail Obat", teks)


if __name__ == "__main__":
    trie_nama, trie_gejala = muat_data_csv("data cadangan.csv")
    app = App()
    app.mainloop()
