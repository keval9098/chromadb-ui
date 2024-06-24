from flask import Flask, render_template,request,redirect,url_for
import os
import sqlite3
import requests
import chromadb
from chromadb.config import Settings
settins = Settings(anonymized_telemetry=False)
client = chromadb.PersistentClient(path="./chroma_data",settings=settins)

con = sqlite3.connect("./chroma_data/chroma.sqlite3", check_same_thread=False)

app = Flask(__name__, static_url_path='/static')

def query(sql):
    cur = con.cursor()
    res = cur.execute(sql)
    response = res.fetchall()
    cur.close()
    return response
    
@app.route("/")
def index():
    databases = query("SELECT name FROM databases")
    collections = client.list_collections()
    return render_template("index.html", databases=databases, collections=collections)

@app.route("/delete/<name>", methods=['GET'])
def delete_collection(name):
    client.delete_collection(name)
    return redirect("/")

@app.route("/delete_document/<name>/<id>", methods=["GET"])
def delete_document(name, id):
    col = client.get_collection(name=name)
    col.delete(ids=[id])
    return redirect(url_for("collection", name=name, id=col.id))


@app.route("/add", methods=['POST'])
def add_collection():
    name = request.form.get("name")
    try:
        col = client.create_collection(name)
        message = {"msg":"Collection created!", "status":"success"}
    except Exception as e:
        message={"msg":e, "status":"error"}
    databases = query("SELECT name FROM databases")
    collections = client.list_collections()
    return render_template("index.html", databases=databases, collections=collections, message=message)

@app.route("/collection/<name>/<id>", methods=['GET'])
def collection(name,id):
    col = client.get_collection(name=name)
    total = col.count()
    data = query("SELECT embeddings.embedding_id, embedding_metadata.string_value, segments.collection FROM embeddings INNER JOIN embedding_metadata ON embedding_metadata.id=embeddings.id INNER JOIN segments ON segments.id=embeddings.segment_id WHERE embedding_metadata.key='chroma:document' AND segments.collection='{}' ORDER BY embeddings.created_at DESC LIMIT 50".format(id))
    print(data)
    return render_template("collection.html", data=data, total=total, col=col)

@app.route("/collection/<name>/<id>", methods=['POST'])
def save(name,id):
    doc = request.form.get("doc")
    docid = request.form.get("docid")
    collection = client.get_collection(name=name)
    print(docid, doc)
    collection.add(
        documents=[doc],
        metadatas=[{"source": "netapp"}],
        ids=[docid]
    )
    return redirect(url_for('collection', name=name, id=id))

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

@app.route("/api/collection/<name>/<id>", methods=['POST'])
def api_collection(name,id):
    data=request.get_json(silent=True)
    collection = client.get_collection(name=name)
    collection.add(
        documents=[data.get('doc')],
        metadatas=[data.get('metadata')],
        ids=[data.get('docid')]
    )
    return {"status":"success"}

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, port=port)