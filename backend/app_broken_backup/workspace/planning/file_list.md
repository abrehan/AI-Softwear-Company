{
    "backend": [
        "backend/app/main.py",
        "backend/app/core/config.py",
        "backend/app/core/security.py",
        "backend/app/database.py",
        "backend/app/models/user.py",
        "backend/app/models/project.py",
        "backend/app/schemas/user.py",
        "backend/app/schemas/project.py",
        "backend/app/api/routes/auth.py",
        "backend/app/api/routes/users.py",
        "backend/app/api/routes/projects.py",
        "backend/app/services/auth_service.py",
        "backend/app/services/user_service.py",
        "backend/app/services/project_service.py",
        "backend/app/utils/helpers.py",
        "backend/requirements.txt"
    ],
    "frontend": [
        "frontend/src/main.tsx",
        "frontend/src/App.tsx",
        "frontend/src/pages/Home.tsx",
        "frontend/src/pages/Login.tsx",
        "frontend/src/components/Navbar.tsx",
        "frontend/src/components/Footer.tsx"
    ],
    "database": [
        "database/schema.sql"
    ]
}