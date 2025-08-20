from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from asgi_correlation_id import CorrelationIdMiddleware, correlation_id
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.adapters.inbound.restapi.dependencies import async_engine_dependency
from app.adapters.inbound.restapi.exceptions import APIError, InternalServerError
from app.adapters.inbound.restapi.items.routes import item_router
from app.adapters.inbound.restapi.logging import configure_logging
from app.adapters.inbound.restapi.users.routes import user_router
from app.adapters.outbound.repositories.models import Base


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None]:  # noqa: ARG001
    configure_logging()
    engine = await async_engine_dependency()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(lifespan=lifespan)

app.add_middleware(CorrelationIdMiddleware)


@app.exception_handler(APIError)
async def custom_exception_handler(request: Request, exc: APIError) -> JSONResponse:  # noqa: ARG001
    response = JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.error_code, "detail": exc.detail},
    )

    return response


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa: ARG001
    internal_error = InternalServerError()
    response = JSONResponse(
        status_code=internal_error.status_code,
        content={"error": internal_error.error_code, "detail": internal_error.detail},
    )
    cid = correlation_id.get()
    if cid:
        response.headers["x-request-id"] = cid
    return response


app.include_router(user_router)
app.include_router(item_router)
