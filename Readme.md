# ChromaDB UI using Flask

```bash
flask --app app --debug run
```

/root/.cache/chroma/onnx_models/all-MiniLM-L6-v2/onnx.tar.gz

docker run -d -p 8000:8000 -v ./chroma_data:/code/chroma_data -v ./llm:/root/.cache/chroma/ ui:latest