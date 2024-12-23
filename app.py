import streamlit as st
import pandas as pd
from pyvis.network import Network

# Mengatur mode tampilan default menjadi light mode
st.set_page_config(page_title="Network Graph Analysis", layout="wide")

# Data sample untuk SNA (transaksi nasabah pada berbagai ekosistem)
data = {
    'source': ['Nasabah1', 'Nasabah2', 'Nasabah3', 'Nasabah4', 'Nasabah5', 'Nasabah6', 'Nasabah7', 'Nasabah8', 'Nasabah9', 'Nasabah10'],
    'target': ['MRT', 'TRANSJAKARTA', 'JAKPRO', 'PAM JAYA', 'MRT', 'JAKPRO', 'TRANSJAKARTA', 'PAM JAYA', 'MRT', 'JAKPRO'],
    'weight': [10, 15, 5, 20, 30, 25, 10, 5, 20, 15],
    'type': ['transaction', 'transaction', 'transaction', 'transaction', 'transaction', 'transaction', 'transaction', 'transaction', 'transaction', 'transaction']
}

# Membuat DataFrame dari data sample
df = pd.DataFrame(data)

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
        net.add_node(row['target'], label=row['target'], title=row['target'], shape="box", size=20)
        net.add_edge(row['source'], row['target'], value=row['weight'], title=row['type'])

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
        if row['source'] in all_connected_nodes and row['target'] in all_connected_nodes:
            net.add_node(row['source'], label=row['source'], title=row['source'], shape="dot", size=20)
            net.add_node(row['target'], label=row['target'], title=row['target'], shape="box", size=20)
            net.add_edge(row['source'], row['target'], value=row['weight'], title=row['type'])

    # Menandai node yang dipilih dengan warna merah
    net.get_node(selected_node)['color'] = 'red'

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
        
        # Menampilkan data lengkap properti node
        st.write("Detail Properti Node:")
        st.write(node_data)