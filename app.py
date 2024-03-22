from flask import Flask, render_template,request,redirect
import os
import sqlite3
import requests
import chromadb
from chromadb.config import Settings
settins = Settings(anonymized_telemetry=False)
client = chromadb.PersistentClient(path="./chroma_data",settings=settins)

con = sqlite3.connect("./chroma_data/chroma.sqlite3", check_same_thread=False)

app = Flask(__name__)

def query(sql):
    cur = con.cursor()
    res = cur.execute(sql)
    response = res.fetchall()
    cur.close()
    return response
    
@app.route("/")
def index():
    databases = query("SELECT name FROM databases")
    # print(databases)
    collections = client.list_collections()
    return render_template("index.html", databases=databases, collections=collections)

@app.route("/collection/<name>/<id>", methods=['GET'])
def collection(name,id):
    col = client.get_collection(name=name)
    total = col.count()
    data = query("SELECT embeddings.embedding_id, embedding_metadata.string_value, segments.collection FROM embeddings INNER JOIN embedding_metadata ON embedding_metadata.id=embeddings.id INNER JOIN segments ON segments.id=embeddings.segment_id WHERE embedding_metadata.key='chroma:document' AND segments.collection='{}' ORDER BY embeddings.created_at DESC LIMIT 50".format(id))
    return render_template("collection.html", data=data, total=total)

@app.route("/collection/<name>/<id>", methods=['POST'])
def save(name,id):
    doc = request.form.get("doc")
    docid = request.form.get("docid")
    collection = client.get_collection(name=name)
    collection.add(
        documents=[doc],
        metadatas=[{"source": "netapp"}],
        ids=[docid]
    )
    return redirect("/")

@app.route("/query", methods=['GET'])
def querypage():
    cols = client.list_collections()
    return render_template("query.html",cols=cols)

@app.route("/query", methods=['POST'])
def querydata():
    text = request.form.get("text")
    col = request.form.get("col")
    collection = client.get_collection(name=col)
    results = collection.query(
        query_texts=[text],
        n_results=10,
        # where={"metadata_field": "is_equal_to_this"},
        # where_document={"$contains":"search_string"}
    )
    # print(results)
    data=[]
    for i,val in enumerate(results['documents'][0]):
        data.append((val,results['ids'][0][i],results['distances'][0][i]))
    cols = client.list_collections()

    return render_template("query.html", data=data, cols=cols)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)