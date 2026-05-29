"""Document storage abstraction (V4.2).

Two interchangeable backends behind one ``StorageBackend`` interface:

- **LocalStorage** (default) — writes files under ``settings.storage_dir``. It has
  no signing, so ``presigned_url`` returns the app's own authenticated download
  endpoint. Used in dev/CI.
- **MinioStorage** — S3-compatible object store (MinIO). Wired and ready; it only
  activates when ``STORAGE_BACKEND=minio`` and the ``MINIO_*`` connection vars are
  set. ``presigned_url`` returns a time-limited signed GET URL straight from MinIO.

``get_storage()`` resolves the configured backend. Keeping the surface this small
means the routers never care which backend is live.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Protocol
from uuid import uuid4

from app.core.config import settings


class StorageBackend(Protocol):
    def put(self, key: str, data: bytes, content_type: str | None = None) -> None: ...
    def get(self, key: str) -> bytes: ...
    def delete(self, key: str) -> None: ...
    def presigned_url(self, key: str, expires_seconds: int = 3600) -> str: ...


def make_key(case_id: str, filename: str) -> str:
    """A collision-free storage key that keeps the original filename readable."""
    safe = os.path.basename(filename).replace("/", "_")
    return f"onboarding/{case_id}/{uuid4().hex}_{safe}"


class LocalStorage:
    def __init__(self, base_dir: str, public_base_url: str):
        self.base = Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)
        self.public_base_url = public_base_url.rstrip("/")

    def _path(self, key: str) -> Path:
        p = (self.base / key).resolve()
        if not str(p).startswith(str(self.base.resolve())):
            raise ValueError("invalid storage key")
        return p

    def put(self, key: str, data: bytes, content_type: str | None = None) -> None:
        path = self._path(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def get(self, key: str) -> bytes:
        return self._path(key).read_bytes()

    def delete(self, key: str) -> None:
        self._path(key).unlink(missing_ok=True)

    def presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        # No signing for local files — hand back the app's download endpoint.
        return f"{self.public_base_url}/api/v1/onboarding/documents/download?key={key}"


class MinioStorage:
    def __init__(self):
        from minio import Minio  # imported lazily so it's optional in dev/CI

        self.bucket = settings.minio_bucket
        self.client = Minio(
            settings.minio_endpoint,
            access_key=settings.minio_access_key,
            secret_key=settings.minio_secret_key,
            secure=settings.minio_secure,
        )
        if not self.client.bucket_exists(self.bucket):
            self.client.make_bucket(self.bucket)

    def put(self, key: str, data: bytes, content_type: str | None = None) -> None:
        import io

        self.client.put_object(
            self.bucket,
            key,
            io.BytesIO(data),
            length=len(data),
            content_type=content_type or "application/octet-stream",
        )

    def get(self, key: str) -> bytes:
        resp = self.client.get_object(self.bucket, key)
        try:
            return resp.read()
        finally:
            resp.close()
            resp.release_conn()

    def delete(self, key: str) -> None:
        self.client.remove_object(self.bucket, key)

    def presigned_url(self, key: str, expires_seconds: int = 3600) -> str:
        from datetime import timedelta

        return self.client.presigned_get_object(
            self.bucket, key, expires=timedelta(seconds=expires_seconds)
        )


_backend: StorageBackend | None = None


def get_storage() -> StorageBackend:
    global _backend
    if _backend is None:
        if settings.storage_backend == "minio":
            _backend = MinioStorage()
        else:
            _backend = LocalStorage(settings.storage_dir, settings.public_base_url)
    return _backend
