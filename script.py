import chromadb
client = chromadb.PersistentClient(path="./chroma_data")
client.list_collections()
collection = client.get_collection(name="ontap")


collection.add(
    documents=["This is a document", "This is another document"],
    metadatas=[{"source": "my source"}, {"source": "my source"}],
    ids=["1", "2"]
)

# results = collection.query(
#     query_texts=["This is a query document"],
#     n_results=2
# )
# print(results)
# print(client.list_collections()[0])