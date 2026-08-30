# ItemService

A simple Flask REST API for managing items.

## Features

- CRUD operations for items
- In-memory storage
- JSON responses

## Getting Started

```bash
pip install -r requirements.txt
python -m app.main
```

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /items | List all items |
| GET | /items/<id> | Get a single item |
| POST | /items | Create a new item |
| DELETE | /items/<id> | Delete an item |

## Testing

```bash
pip install -r requirements.txt
python -m pytest tests/
```

## License

MIT
