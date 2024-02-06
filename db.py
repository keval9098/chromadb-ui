import sqlite3
con = sqlite3.connect("./chroma_data/chroma.sqlite3", check_same_thread=False)

def query(sql):
    cur = con.cursor()
    res = cur.execute(sql)
    response = res.fetchall()
    cur.close()
    return response

data = query("SELECT embeddings.embedding_id, embedding_metadata.string_value, segments.collection FROM embeddings INNER JOIN embedding_metadata ON embedding_metadata.id=embeddings.id INNER JOIN segments ON segments.id=embeddings.segment_id WHERE embedding_metadata.key='chroma:document'")
print(data)