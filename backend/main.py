from fastapi import FastAPI
from sqlalchemy.exc import IntegrityError

from auth.views import auth_router
from exc_handlers.base import value_error_handler, related_errors_handler
from views.cargo import cargo_router
from views.insurance import insurance_router
from views.rates import rates_router

app = FastAPI(title="Test smit app")

exc_handlers = {
    ValueError: value_error_handler,
    IntegrityError: related_errors_handler,
}
routers = {
    "/auth": auth_router,
    "/cargo": cargo_router,
    "/insurance": insurance_router,
    "/rates": rates_router,
}

for exception, handler in exc_handlers.items():
    app.add_exception_handler(exception, handler)

for prefix, router in routers.items():
    app.include_router(router, prefix=prefix)
