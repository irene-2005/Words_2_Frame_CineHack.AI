Quick API guide — uploads and AI analysis

This backend exposes endpoints for project management and AI script analysis.

Bootstrap (create first admin user)

You can create a user via the `/users/` endpoint. For the first admin user, create via a small script or SQLite direct edit; for convenience you can use the SQLite shell to set `is_admin` to 1 for a user after creation.

Example (PowerShell):

# Create a user (no special admin flag via API)
PS> curl -X POST -H "Content-Type: application/json" -d '{"username":"director","email":"d@example.com","password":"secret"}' http://127.0.0.1:8000/users/

# Use /token to login and receive a bearer token (JSON body with username/password)
PS> curl -X POST -H "Content-Type: application/json" -d '{"username":"director","password":"secret"}' http://127.0.0.1:8000/token

Save the access_token from the response.

Upload script (admin-only)

Use the returned Bearer token in Authorization header. This endpoint accepts multipart file upload.

Example (curl):

curl -X POST "http://127.0.0.1:8000/projects/1/upload_script" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -F "file=@/path/to/script.txt"

Example (PowerShell):

$token = "<ACCESS_TOKEN>"
$headers = @{ Authorization = "Bearer $token" }
Invoke-RestMethod -Uri "http://127.0.0.1:8000/projects/1/upload_script" -Method Post -InFile "C:\path\to\script.txt" -ContentType "multipart/form-data" -Headers $headers

Trigger analysis (admin-only)

After upload, call the analyze endpoint to parse the uploaded script and create Scenes and ToDos.

curl -X POST "http://127.0.0.1:8000/projects/1/analyze_script" \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"filename":"script.txt"}'


Notes
- The server saves uploads to `./uploads/`. Sanitize and secure this directory before production.
- Replace the dev JWT secret in `app/auth.py` with a secure environment variable for production.
- The AI model is loaded from `ai/models/budget_model.pkl` if present; otherwise a heuristic is used.
- Use `/docs` for interactive API docs when running the app.
