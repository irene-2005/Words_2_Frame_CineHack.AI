# test_api.ps1
# Make sure your FastAPI server is running before executing this

# Helper function to print responses nicely
function Print-Response($desc, $response) {
    Write-Host "`n$desc"
    $response | ConvertTo-Json -Depth 5 | Write-Host
}

# ---------- 1. Create a Project ----------
$projectPayload = @{
    name = "CineHack Project 1"
    description = "Test project for backend"
    budget = 10000.0
}
$projectResponse = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/projects/" -Body ($projectPayload | ConvertTo-Json) -ContentType "application/json"
Print-Response "Created Project:" $projectResponse

# ---------- 2. Get All Projects ----------
$allProjects = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/projects/"
Print-Response "All Projects:" $allProjects

# Store project ID for later
$projectId = $projectResponse.id

# ---------- 3. Create a Crew ----------
$crewPayload = @{
    name = "Alice"
    role = "Director"
}
$crewResponse = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/crews/" -Body ($crewPayload | ConvertTo-Json) -ContentType "application/json"
Print-Response "Created Crew:" $crewResponse

# ---------- 4. Get All Crews ----------
$allCrews = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/crews/"
Print-Response "All Crews:" $allCrews

# Store crew ID for task
$crewId = $crewResponse.id

# ---------- 5. Create a Task ----------
$taskPayload = @{
    title = "Shoot Scene 1"
    project_id = $projectId
    crew_id = $crewId
}
$taskResponse = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/tasks/" -Body ($taskPayload | ConvertTo-Json) -ContentType "application/json"
Print-Response "Created Task:" $taskResponse

# ---------- 6. Get All Tasks ----------
$allTasks = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/tasks/"
Print-Response "All Tasks:" $allTasks

# ---------- 7. Create a Finance Record ----------
$financePayload = @{
    project_id = $projectId
    amount_spent = 2500.0
    description = "Camera equipment"
}
$financeResponse = Invoke-RestMethod -Method Post -Uri "http://127.0.0.1:8000/finances/" -Body ($financePayload | ConvertTo-Json) -ContentType "application/json"
Print-Response "Created Finance Record:" $financeResponse

# ---------- 8. Get All Finances ----------
$allFinances = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/finances/"
Print-Response "All Finance Records:" $allFinances

# ---------- 9. Test Root ----------
$rootResponse = Invoke-RestMethod -Method Get -Uri "http://127.0.0.1:8000/"
Print-Response "Root Endpoint:" $rootResponse
