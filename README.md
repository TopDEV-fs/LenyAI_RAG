# LenyAI_RAG - FastAPI Demo

This is a minimal FastAPI project with a sample router at `/items`.

## Quick Start

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the server with uvicorn:

```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000/docs to see the interactive API docs.

## Endpoints

- `GET /` - root welcome message
- `GET /items/` - list items
- `GET /items/{item_id}` - get a specific item
- `POST /items/` - create a new item (JSON body)
- `PUT /items/{item_id}` - update an existing item
- `DELETE /items/{item_id}` - delete an item

## Tests

Run tests:

```bash
pytest -q
```
