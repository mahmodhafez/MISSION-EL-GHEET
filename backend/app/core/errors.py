"""One error envelope for every failure: {"error": {"code", "message", "field_paths"}}."""
from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


class ApiError(Exception):
    def __init__(self, status: int, code: str, message: str = "", field_paths: list[str] | None = None):
        super().__init__(code)
        self.status, self.code, self.message, self.field_paths = status, code, message, field_paths or []


def envelope(code: str, message: str = "", field_paths: list[str] | None = None) -> dict:
    return {"error": {"code": code, "message": message, "field_paths": field_paths or []}}


def install(app: FastAPI) -> None:
    @app.exception_handler(ApiError)
    async def _api(_: Request, e: ApiError):
        return JSONResponse(envelope(e.code, e.message, e.field_paths), status_code=e.status)

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, e: RequestValidationError):
        paths = [".".join(str(p) for p in err.get("loc", ())) for err in e.errors()]
        return JSONResponse(envelope("invalid_request", "Request does not match the schema.", paths), status_code=422)
