from fastapi import FastAPI
from routes.route import router_resumes
from routes.route import router_payslips
from routes.route import router_uploads
from routes.route import router_experience_letters
from routes.route import router_certificates
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Your React app URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router_resumes)
app.include_router(router_experience_letters)
app.include_router(router_uploads)
app.include_router(router_payslips)
app.include_router(router_certificates)