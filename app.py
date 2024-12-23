import streamlit as st
import pandas as pd
from pyvis.network import Network
import random
import datetime

# Mengatur mode tampilan default menjadi light mode
st.set_page_config(page_title="Network Graph Analysis", layout="wide")

# Membuat data transaksi SNA dengan rekening dan ekosistem
random.seed(42)

# Membuat daftar rekening sumber dan tujuan
accounts = [f"ACC{random.randint(1000, 9999)}" for _ in range(20)]
ecosystems = ['ECO 1', 'ECO 2', 'ECO 3', 'ECO 4', 'ECO 5']
types = ['Transfer', 'Pembelian', 'Pembayaran']
channels = ['ATM', 'Mobile Banking', 'Internet Banking', 'Teller']

# Membuat transaksi dengan data yang lebih besar
data = []
for _ in range(100):
    source_account = random.choice(accounts)
    destination_account = random.choice([acc for acc in accounts if acc != source_account])
    ecosystem = random.choice(ecosystems)
    amount = random.randint(1000, 50000)
    tgltrx = datetime.datetime.now() - datetime.timedelta(days=random.randint(1, 30))
    type_ = random.choice(types)  # Jenis transaksi
    channel = random.choice(channels)  # Saluran transaksi
    data.append([tgltrx.strftime('%Y-%m-%d'), source_account, destination_account, ecosystem, amount, type_, channel])

# Membuat DataFrame dari data transaksi
df = pd.DataFrame(data, columns=['tgltrx', 'source', 'target', 'ecosystem', 'amount', 'type', 'channel'])

# Menambahkan kolom frequency dan weight
df['frequency'] = df.groupby(['source', 'target', 'ecosystem'])['amount'].transform('count')
df['weight'] = df['amount'] * df['frequency']

# Normalisasi Min-Max untuk menghitung Weight dalam bentuk persentase
min_weight = df['weight'].min()
max_weight = df['weight'].max()
df['weight_percentage'] = (df['weight'] - min_weight) / (max_weight - min_weight) * 100

# Streamlit UI untuk menampilkan network graph
st.title("Network Graph Analysis with Streamlit and PyVis")

# Pilih node dari dropdown untuk menampilkan properti
selected_node = st.selectbox("Pilih Node untuk Melihat Propertinya", ['All'] + df['source'].unique().tolist())

# Membuat Network Graph menggunakan PyVis
net = Network(height="600px", width="100%", notebook=True, directed=True)

if selected_node == "All":
    # Menampilkan seluruh network graph
    for index, row in df.iterrows():
        net.add_node(row['source'], label=row['source'], title=row['source'], shape="dot", size=20)
        net.add_node(row['target'], label=row['target'], title=row['target'], shape="dot", size=20)
        
        # Menambahkan edge dengan informasi Amount, Frequency, dan Weight yang dinormalisasi (persentase)
        net.add_edge(
            row['source'], 
            row['target'], 
            value=row['weight'], 
            title=f"Amount: {row['amount']}\nFrequency: {row['frequency']}\nWeight: {row['weight_percentage']:.2f}%"
        )

    # Menambahkan panah pada edge dan menonaktifkan fisika
    net.set_options("""
    var options = {
        "physics": {
            "enabled": false
        },
        "nodes": {
            "size": 20,
            "font": {
                "size": 16
            }
        },
        "edges": {
            "smooth": {
                "type": "continuous"
            },
            "arrows": {
                "to": { "enabled": true, "scaleFactor": 1.5 }
            }
        }
    }
    """)
else:
    # Filter data untuk hanya menampilkan node yang terhubung dengan node yang dipilih
    connected_nodes = df[(df['source'] == selected_node) | (df['target'] == selected_node)]
    
    # Menentukan node yang terhubung
    connected_nodes_sources = connected_nodes['source'].unique().tolist()
    connected_nodes_targets = connected_nodes['target'].unique().tolist()
    all_connected_nodes = list(set(connected_nodes_sources + connected_nodes_targets))
    
    # Menambahkan node dan edge yang terhubung saja
    for index, row in connected_nodes.iterrows():
        # Menetapkan warna hijau terang untuk node yang terhubung
        if row['source'] == selected_node:
            net.add_node(row['source'], label=row['source'], title=row['source'], shape="dot", size=30, color='deepskyblue')  # Node yang dipilih lebih besar dan biru
        else:
            net.add_node(row['source'], label=row['source'], title=row['source'], shape="dot", size=20, color='lightgreen')  # Node lain hijau muda

        if row['target'] == selected_node:
            net.add_node(row['target'], label=row['target'], title=row['target'], shape="dot", size=30, color='deepskyblue')  # Node yang dipilih lebih besar dan biru
        else:
            net.add_node(row['target'], label=row['target'], title=row['target'], shape="dot", size=20, color='lightgreen')  # Node lain hijau muda

        # Menambahkan edge dengan informasi yang lebih sederhana (Amount, Frequency, dan Weight yang dinormalisasi)
        net.add_edge(
            row['source'], 
            row['target'], 
            value=row['weight'], 
            title=f"Amount: {row['amount']}\nFrequency: {row['frequency']}\nWeight: {row['weight_percentage']:.2f}%"
        )

    # Menandai node yang dipilih dengan warna merah
    net.get_node(selected_node)['color'] = 'deepskyblue'

    # Menambahkan panah pada edge dan menonaktifkan fisika
    net.set_options("""
    var options = {
        "physics": {
            "enabled": false
        },
        "nodes": {
            "size": 20,
            "font": {
                "size": 16
            }
        },
        "edges": {
            "smooth": {
                "type": "continuous"
            },
            "arrows": {
                "to": { "enabled": true, "scaleFactor": 1.5 }
            }
        }
    }
    """)

# Menyimpan jaringan sebagai file HTML
net.show("network.html")

# Layout untuk menampilkan properti node di samping grafik
col1, col2 = st.columns([2, 1])  # Membuat dua kolom

with col1:
    # Menampilkan network graph
    st.components.v1.html(open("network.html", "r").read(), height=600)

with col2:
    # Menampilkan properti node yang dipilih
    if selected_node != "All":
        node_data = df[(df['source'] == selected_node) | (df['target'] == selected_node)]

        st.subheader(f"Properties of Node {selected_node}:")

        # Menampilkan jumlah edges (hubungan) untuk node tersebut
        edges_count = len(node_data)
        st.write(f"Jumlah Edges: {edges_count}")
        
        # Menampilkan jumlah total weight untuk node tersebut
        total_weight = node_data['weight'].sum()
        st.write(f"Jumlah Total Weight: {total_weight}")
        
        # Menampilkan tipe hubungan
        relationship_types = node_data['type'].unique()
        st.write(f"Jenis Hubungan: {', '.join(relationship_types)}")
        
        # Menampilkan saluran transaksi
        transaction_channels = node_data['channel'].unique()
        st.write(f"Saluran Transaksi: {', '.join(transaction_channels)}")
        
        # Menampilkan data lengkap properti node
        st.write("Detail Properti Node:")
        st.write(node_data)