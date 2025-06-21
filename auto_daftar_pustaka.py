import streamlit as st
import requests
import bibtexparser
from io import StringIO

st.title("Auto Daftar Pustaka dengan Link & Unduh Sitasi")

def get_metadata_from_doi(doi):
    url = f"https://api.crossref.org/works/{doi}"
    resp = requests.get(url)
    if resp.status_code == 200:
        return resp.json().get('message', {})
    return None

def search_metadata_by_title(title):
    url = f"https://api.crossref.org/works?query.title={title}&rows=1"
    resp = requests.get(url)
    if resp.status_code == 200:
        items = resp.json()['message']['items']
        if items:
            return items[0]
    return None

def bibtex_from_metadata(meta):
    # Simple BibTeX generator, can be improved for more robust output
    author = " and ".join([f"{a['given']} {a['family']}" for a in meta.get('author', [])])
    entry = {
        "ENTRYTYPE": "article",
        "ID": meta.get('DOI', 'unknown').replace('/', '_'),
        "author": author,
        "title": meta.get('title', [''])[0],
        "journal": meta.get('container-title', [''])[0],
        "year": str(meta.get('issued', {}).get('date-parts', [[None]])[0][0]),
        "doi": meta.get('DOI', ''),
        "url": meta.get('URL', '')
    }
    db = bibtexparser.bibdatabase.BibDatabase()
    db.entries = [entry]
    return bibtexparser.dumps(db)

st.write("Masukkan DOI atau judul artikel, lalu klik 'Cari & Tambah Daftar Pustaka'.")

input_type = st.radio("Masukkan berdasarkan:", ("DOI", "Judul"))
input_val = st.text_input("Masukkan DOI / Judul Artikel")

if "refs" not in st.session_state:
    st.session_state.refs = []

if st.button("Cari & Tambah Daftar Pustaka"):
    if input_type == "DOI":
        meta = get_metadata_from_doi(input_val.strip())
    else:
        meta = search_metadata_by_title(input_val.strip())
    if meta:
        st.session_state.refs.append(meta)
        st.success("Ditambahkan ke daftar pustaka!")
    else:
        st.error("Data tidak ditemukan.")

st.header("Daftar Pustaka")
for i, meta in enumerate(st.session_state.refs):
    authors = ", ".join([f"{a['given']} {a['family']}" for a in meta.get('author', [])])
    title = meta.get('title', [''])[0]
    journal = meta.get('container-title', [''])[0] if meta.get('container-title') else '-'
    year = meta.get('issued', {}).get('date-parts', [[None]])[0][0]
    url = meta.get('URL', '')
    st.markdown(f"{i+1}. **{title}**<br>{authors} ({year}). <i>{journal}</i>. [Link]({url})", unsafe_allow_html=True)



st.caption("Powered by CrossRef API")
