from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from api import search_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# async def check_authorization(request: Request, call_next):
#     response = await call_next(request)

#     auth_token = request.headers.get("Authorization")

#     # decode the token

#     decoded_token = decode_access_token(auth_token)

#     if decoded_token is None:
#         response = {
#             "authorized": False,
#         }

#         return JSONResponse(response, status_code=401)

#     user = users_table.search(DBQuery.id == decoded_token["id"])

#     if user:

#         return response

#     else:

#         response = {
#             "authorized": False,
#         }

#         return JSONResponse(response, status_code=401)


# # static files config
# app.mount("/output", StaticFiles(directory="output"), name="output")
# app.include_router(camera_router, prefix="/api/cameras")
# app.include_router(streaming_router, prefix="/api/streams")
# app.include_router(agents_router, prefix="/api/agents")
# app.include_router(auth_router, prefix="/api/auth/users")
# app.include_router(logs_router, prefix="/api/logs")
app.include_router(search_router, prefix="/api/search")
# app.include_router(notifications_router, prefix="/api/notifications")
