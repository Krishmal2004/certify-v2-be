import config

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import admin, certificate, badge

app = FastAPI()

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=False,
	allow_methods=["*"],
	allow_headers=["*"],
)

app.include_router(admin.router, prefix="/api")
app.include_router(certificate.router, prefix="/api")
app.include_router(badge.router, prefix="/api")