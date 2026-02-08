# Firebase Functions Python entry point
from firebase_functions import https_fn, options
from firebase_admin import initialize_app

# Import the FastAPI app
from api_server import app as fastapi_app

# Initialize Firebase Admin
initialize_app()

# Set function options for more memory and timeout
options.set_global_options(
    region=options.SupportedRegion.US_CENTRAL1,
    memory=options.MemoryOption.GB_2,
    timeout_sec=300,
)

# Expose FastAPI as a Cloud Function
@https_fn.on_request()
def api(req: https_fn.Request) -> https_fn.Response:
    """HTTP Cloud Function that serves the FastAPI app."""
    from starlette.requests import Request as StarletteRequest
    from starlette.testclient import TestClient
    
    # Create test client for FastAPI
    client = TestClient(fastapi_app)
    
    # Forward the request to FastAPI
    headers = dict(req.headers)
    
    if req.method == "GET":
        response = client.get(req.path, headers=headers)
    elif req.method == "POST":
        response = client.post(req.path, headers=headers, json=req.get_json(silent=True))
    elif req.method == "PUT":
        response = client.put(req.path, headers=headers, json=req.get_json(silent=True))
    elif req.method == "DELETE":
        response = client.delete(req.path, headers=headers)
    else:
        response = client.request(req.method, req.path, headers=headers)
    
    return https_fn.Response(
        response=response.content,
        status=response.status_code,
        headers=dict(response.headers)
    )