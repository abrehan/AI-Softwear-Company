"""
Complete Language Configuration for AI Software House
Supports ALL major programming languages
"""

LANGUAGE_CONFIG = {
    # ============================================================
    # BACKEND LANGUAGES
    # ============================================================
    "python": {
        "extensions": [".py"],
        "frameworks": ["FastAPI", "Django", "Flask", "Streamlit", "Litestar"],
        "package_manager": "pip/poetry",
        "version": "3.8+",
        "testing": ["pytest", "unittest", "pytest-asyncio"],
        "linting": ["flake8", "black", "mypy", "isort"],
        "formatters": ["black", "autopep8"],
        "build_tools": ["setuptools", "poetry", "pdm"],
        "async_support": True,
        "type_hints": True,
        "template": "python",
        "icon": "🐍"
    },
    "csharp": {
        "extensions": [".cs"],
        "frameworks": ["ASP.NET Core", "Blazor", "Maui", "Xamarin", "Nancy"],
        "package_manager": "NuGet",
        "version": "8.0+",
        "testing": ["xUnit", "NUnit", "MSTest", "SpecFlow"],
        "linting": ["StyleCop", "Roslyn", "SonarAnalyzer"],
        "formatters": ["dotnet-format", "csharpier"],
        "build_tools": ["dotnet", "msbuild"],
        "async_support": True,
        "type_hints": True,
        "template": "csharp",
        "icon": "🎯"
    },
    "java": {
        "extensions": [".java"],
        "frameworks": ["Spring Boot", "Spring MVC", "Hibernate", "Quarkus", "Micronaut"],
        "package_manager": "Maven/Gradle",
        "version": "11+",
        "testing": ["JUnit", "TestNG", "Mockito", "AssertJ"],
        "linting": ["Checkstyle", "PMD", "SpotBugs"],
        "formatters": ["google-java-format", "prettier-java"],
        "build_tools": ["maven", "gradle"],
        "async_support": False,
        "type_hints": False,
        "template": "java",
        "icon": "☕"
    },
    "nodejs": {
        "extensions": [".js"],
        "frameworks": ["Express", "NestJS", "Fastify", "Koa", "Hapi"],
        "package_manager": "npm/yarn/pnpm",
        "version": "16+",
        "testing": ["Jest", "Mocha", "Vitest", "Playwright"],
        "linting": ["ESLint", "Standard"],
        "formatters": ["Prettier"],
        "build_tools": ["webpack", "vite", "esbuild"],
        "async_support": True,
        "type_hints": False,
        "template": "javascript",
        "icon": "🟢"
    },
    "typescript": {
        "extensions": [".ts", ".tsx"],
        "frameworks": ["NestJS", "Express", "Fastify", "tRPC"],
        "package_manager": "npm/yarn/pnpm",
        "version": "4.5+",
        "testing": ["Jest", "Vitest", "Playwright"],
        "linting": ["ESLint", "@typescript-eslint"],
        "formatters": ["Prettier"],
        "build_tools": ["tsc", "webpack", "vite", "esbuild"],
        "async_support": True,
        "type_hints": True,
        "template": "typescript",
        "icon": "🔷"
    },
    "go": {
        "extensions": [".go"],
        "frameworks": ["Gin", "Echo", "Fiber", "Chi", "Fiber"],
        "package_manager": "go mod",
        "version": "1.19+",
        "testing": ["testing", "testify", "ginkgo"],
        "linting": ["golangci-lint", "staticcheck"],
        "formatters": ["gofmt", "goimports"],
        "build_tools": ["go build"],
        "async_support": True,
        "type_hints": True,
        "template": "go",
        "icon": "🐹"
    },
    "rust": {
        "extensions": [".rs"],
        "frameworks": ["Actix", "Rocket", "Axum", "Tokio", "Tide"],
        "package_manager": "cargo",
        "version": "1.70+",
        "testing": ["cargo test", "criterion"],
        "linting": ["clippy", "rustfmt"],
        "formatters": ["rustfmt"],
        "build_tools": ["cargo"],
        "async_support": True,
        "type_hints": True,
        "template": "rust",
        "icon": "🦀"
    },
    "php": {
        "extensions": [".php"],
        "frameworks": ["Laravel", "Symfony", "CodeIgniter", "Slim", "Lumen"],
        "package_manager": "composer",
        "version": "8.0+",
        "testing": ["PHPUnit", "Pest", "Codeception"],
        "linting": ["PHP_CodeSniffer", "PHPMD"],
        "formatters": ["php-cs-fixer", "prettier-php"],
        "build_tools": ["composer"],
        "async_support": False,
        "type_hints": True,
        "template": "php",
        "icon": "🐘"
    },
    "ruby": {
        "extensions": [".rb"],
        "frameworks": ["Ruby on Rails", "Sinatra", "Hanami", "Roda"],
        "package_manager": "gem/bundle",
        "version": "3.0+",
        "testing": ["RSpec", "MiniTest", "Capybara"],
        "linting": ["RuboCop", "Standard"],
        "formatters": ["rubocop"],
        "build_tools": ["rake"],
        "async_support": False,
        "type_hints": False,
        "template": "ruby",
        "icon": "💎"
    },
    
    # ============================================================
    # FRONTEND LANGUAGES
    # ============================================================
    "react": {
        "extensions": [".jsx", ".tsx"],
        "frameworks": ["React", "Next.js", "Remix", "Gatsby"],
        "package_manager": "npm/yarn/pnpm",
        "version": "18+",
        "testing": ["Jest", "Testing Library", "Cypress", "Playwright"],
        "linting": ["ESLint", "Prettier"],
        "formatters": ["Prettier"],
        "build_tools": ["vite", "webpack", "esbuild"],
        "async_support": True,
        "type_hints": True,
        "template": "react",
        "icon": "⚛️"
    },
    "vue": {
        "extensions": [".vue"],
        "frameworks": ["Vue.js", "Nuxt", "Quasar"],
        "package_manager": "npm/yarn/pnpm",
        "version": "3+",
        "testing": ["Vitest", "Jest", "Cypress", "Playwright"],
        "linting": ["ESLint", "Prettier"],
        "formatters": ["Prettier"],
        "build_tools": ["vite", "webpack"],
        "async_support": True,
        "type_hints": True,
        "template": "vue",
        "icon": "🟩"
    },
    "angular": {
        "extensions": [".ts"],
        "frameworks": ["Angular"],
        "package_manager": "npm/yarn/pnpm",
        "version": "15+",
        "testing": ["Jasmine", "Karma", "Playwright"],
        "linting": ["ESLint", "Prettier"],
        "formatters": ["Prettier"],
        "build_tools": ["Angular CLI"],
        "async_support": True,
        "type_hints": True,
        "template": "angular",
        "icon": "🅰️"
    },
    "svelte": {
        "extensions": [".svelte"],
        "frameworks": ["Svelte", "SvelteKit"],
        "package_manager": "npm/yarn/pnpm",
        "version": "4+",
        "testing": ["Vitest", "Playwright"],
        "linting": ["ESLint", "Prettier"],
        "formatters": ["Prettier"],
        "build_tools": ["vite"],
        "async_support": True,
        "type_hints": True,
        "template": "svelte",
        "icon": "🔥"
    },
    
    # ============================================================
    # MOBILE LANGUAGES
    # ============================================================
    "swift": {
        "extensions": [".swift"],
        "frameworks": ["SwiftUI", "UIKit", "Vapor"],
        "package_manager": "SwiftPM",
        "version": "5.7+",
        "testing": ["XCTest", "Quick", "Nimble"],
        "linting": ["SwiftLint"],
        "formatters": ["swiftformat"],
        "build_tools": ["xcodebuild"],
        "async_support": True,
        "type_hints": True,
        "template": "swift",
        "icon": "🦅"
    },
    "kotlin": {
        "extensions": [".kt"],
        "frameworks": ["Spring Boot", "Ktor", "Android"],
        "package_manager": "Gradle",
        "version": "1.8+",
        "testing": ["JUnit", "Kotest", "MockK"],
        "linting": ["ktlint", "detekt"],
        "formatters": ["ktlint"],
        "build_tools": ["gradle"],
        "async_support": True,
        "type_hints": True,
        "template": "kotlin",
        "icon": "🟣"
    },
    "react_native": {
        "extensions": [".jsx", ".tsx"],
        "frameworks": ["React Native", "Expo"],
        "package_manager": "npm/yarn/pnpm",
        "version": "0.70+",
        "testing": ["Jest", "Testing Library"],
        "linting": ["ESLint", "Prettier"],
        "formatters": ["Prettier"],
        "build_tools": ["metro", "expo"],
        "async_support": True,
        "type_hints": True,
        "template": "react_native",
        "icon": "📱"
    },
    "flutter": {
        "extensions": [".dart"],
        "frameworks": ["Flutter"],
        "package_manager": "pub",
        "version": "3.0+",
        "testing": ["flutter_test", "integration_test"],
        "linting": ["dart analyze", "flutter_lints"],
        "formatters": ["dart format"],
        "build_tools": ["flutter"],
        "async_support": True,
        "type_hints": True,
        "template": "flutter",
        "icon": "🟦"
    },
    
    # ============================================================
    # AI/ML LANGUAGES
    # ============================================================
    "python_ml": {
        "extensions": [".py"],
        "frameworks": ["PyTorch", "TensorFlow", "JAX", "Scikit-learn", "HuggingFace"],
        "package_manager": "pip/conda",
        "version": "3.8+",
        "testing": ["pytest", "unittest"],
        "linting": ["flake8", "black"],
        "formatters": ["black"],
        "build_tools": ["setuptools"],
        "async_support": True,
        "type_hints": True,
        "template": "python_ml",
        "icon": "🧠"
    },
    "r": {
        "extensions": [".r"],
        "frameworks": ["Shiny", "Tidyverse", "Caret", "Tidymodels"],
        "package_manager": "CRAN",
        "version": "4.0+",
        "testing": ["testthat", "tinytest"],
        "linting": ["lintr"],
        "formatters": ["styler"],
        "build_tools": ["R CMD"],
        "async_support": False,
        "type_hints": False,
        "template": "r",
        "icon": "📊"
    },
    "julia": {
        "extensions": [".jl"],
        "frameworks": ["Flux.jl", "Zygote.jl", "DataFrames.jl"],
        "package_manager": "Pkg",
        "version": "1.8+",
        "testing": ["Test"],
        "linting": ["JuliaFormatter"],
        "formatters": ["JuliaFormatter"],
        "build_tools": ["Pkg"],
        "async_support": True,
        "type_hints": True,
        "template": "julia",
        "icon": "🧪"
    },
    
    # ============================================================
    # DEVOPS LANGUAGES
    # ============================================================
    "dockerfile": {
        "extensions": [""],
        "frameworks": ["Docker", "Podman"],
        "package_manager": "N/A",
        "version": "N/A",
        "testing": ["docker test"],
        "linting": ["hadolint"],
        "formatters": ["docker fmt"],
        "build_tools": ["docker build"],
        "async_support": False,
        "type_hints": False,
        "template": "dockerfile",
        "icon": "🐳"
    },
    "kubernetes": {
        "extensions": [".yaml", ".yml"],
        "frameworks": ["Kubernetes", "Helm", "Kustomize"],
        "package_manager": "Helm",
        "version": "N/A",
        "testing": ["kubeval", "kubetest"],
        "linting": ["kube-linter"],
        "formatters": ["kubectl"],
        "build_tools": ["kubectl", "helm"],
        "async_support": False,
        "type_hints": False,
        "template": "kubernetes",
        "icon": "☸️"
    },
    "terraform": {
        "extensions": [".tf"],
        "frameworks": ["Terraform", "OpenTofu"],
        "package_manager": "N/A",
        "version": "N/A",
        "testing": ["terraform test"],
        "linting": ["tflint"],
        "formatters": ["terraform fmt"],
        "build_tools": ["terraform"],
        "async_support": False,
        "type_hints": False,
        "template": "terraform",
        "icon": "🏗️"
    }
}

# Language families
LANGUAGE_FAMILIES = {
    "backend": ["python", "csharp", "java", "nodejs", "typescript", "go", "rust", "php", "ruby"],
    "frontend": ["react", "vue", "angular", "svelte", "javascript", "typescript"],
    "mobile": ["swift", "kotlin", "react_native", "flutter"],
    "ai_ml": ["python_ml", "r", "julia"],
    "devops": ["dockerfile", "kubernetes", "terraform"],
    "all": []  # Will be filled programmatically
}

# Fill 'all' family
all_languages = []
for family, langs in LANGUAGE_FAMILIES.items():
    if family != "all":
        all_languages.extend(langs)
LANGUAGE_FAMILIES["all"] = all_languages

# Model recommendations per language
MODEL_RECOMMENDATIONS = {
    "python": "codellama:7b",
    "csharp": "codellama:7b",
    "java": "codellama:7b",
    "nodejs": "codellama:7b",
    "typescript": "codellama:7b",
    "go": "codellama:7b",
    "rust": "codellama:7b",
    "php": "codellama:7b",
    "ruby": "codellama:7b",
    "swift": "codellama:7b",
    "kotlin": "codellama:7b",
    "react": "codellama:7b",
    "vue": "codellama:7b",
    "angular": "codellama:7b",
    "svelte": "codellama:7b",
    "react_native": "codellama:7b",
    "flutter": "codellama:7b",
    "python_ml": "codellama:7b",
    "r": "codellama:7b",
    "julia": "codellama:7b",
    "dockerfile": "codellama:7b",
    "kubernetes": "codellama:7b",
    "terraform": "codellama:7b",
    "javascript": "codellama:7b",
}

# Default model
DEFAULT_MODEL = "codellama:7b"
