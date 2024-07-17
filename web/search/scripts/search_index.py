import faiss
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("sentence-transformers/msmarco-distilbert-base-tas-b")

old_index = faiss.read_index("data/trained_index.index")

d = old_index.d
nlist = 15
index = faiss.index_factory(d, f'IVF{nlist},Flat', faiss.METRIC_INNER_PRODUCT)

index.copy_from(old_index)
del old_index

index.nprobe = 7
topn = 200

def search(request:str):
    vector = np.array([model.encode(request)])
    faiss.normalize_L2(vector)
    D, I = index.search(vector, topn)
    return D, I

d, i = search("NORMATİV HÜQUQİ AKTLAR")
print()
