import uvicorn
from async_fastapi_jwt_auth.exceptions import AuthJWTException
from fastapi import FastAPI
from fastapi import Request, status
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from fastapi.staticfiles import StaticFiles

from api.v1 import users
from core.config import settings


app = FastAPI(
    description='Mock Сервис по авторизации и аутентификации пользователей',
    version='1.0.0',
    title=settings.PROJECT_NAME,
    docs_url='/auth/api/openapi',
    openapi_url='/auth/api/openapi.json',
    default_response_class=JSONResponse,
)


# @app.middleware('http')
# async def before_request(request: Request, call_next):
#     response = await call_next(request)
#     request_id = request.headers.get('X-Request-Id')
#     if not request_id:
#         return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={'detail': 'X-Request-Id is required'})
#     return response


app.include_router(users.router, prefix='/auth/api/v1/users', tags=['users'])

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.exception_handler(AuthJWTException)
def authjwt_exception_handler(request: Request, exc: AuthJWTException):
    """Exception handler for authjwt."""
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})


app.add_middleware(SessionMiddleware, secret_key="secret-string")


if __name__ == '__main__':
    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        port=8000,
        reload=True
    )
