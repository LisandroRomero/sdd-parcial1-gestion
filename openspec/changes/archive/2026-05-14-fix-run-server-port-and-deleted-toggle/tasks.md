## 1. Fix backend port mismatch

- [x] 1.1 Change `run_server.py` port from 8000 to 8001

## 2. Fix ProductoRead schema — add deleted_at field

- [x] 2.1 Add `deleted_at: Optional[datetime] = None` to `ProductoRead` in `backend/productos/schemas.py`

## 3. Fix repository filter — skip disponible filter when include_deleted=True

- [x] 3.1 Modify `backend/productos/repository.py` so the default `disponible=True` filter is not applied when `include_deleted=True`
