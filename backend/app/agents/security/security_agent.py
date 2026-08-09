from app.agents.base_agent import BaseAgent
from app.memory.project_memory import memory
from app.workspace.workspace import workspace


class SecurityAgent(BaseAgent):

    def __init__(self):
        super().__init__(
            "Security Agent",
            "Senior Cyber Security Engineer"
        )

        self.model = "llama3.2:1b"

    async def run(self, task: str):
        return await self.security_review(task)

    async def security_review(self, task: str):

        print("🔒 Security Agent Started")

        ceo_summary = memory.get("ceo") or ""
        pm_plan = memory.get("pm") or ""
        cto_architecture = memory.get("cto") or ""
        backend_design = memory.get("backend") or ""
        frontend_design = memory.get("frontend") or ""
        database_design = memory.get("database") or ""
        devops_plan = memory.get("devops") or ""
        qa_plan = memory.get("qa") or ""

        prompt = f"""
You are a Senior Cyber Security Engineer.

CEO Analysis

{ceo_summary}

Project Plan

{pm_plan}

Architecture

{cto_architecture}

Backend

{backend_design}

Frontend

{frontend_design}

Database

{database_design}

DevOps

{devops_plan}

QA

{qa_plan}

Original Project

{task}

Create a complete security assessment.

Return Markdown.

# Security Report

## Security Overview

## Authentication

## Authorization

## JWT Strategy

## OAuth

## API Security

## SQL Injection Protection

## XSS Protection

## CSRF Protection

## CORS Policy

## Password Policy

## Secrets Management

## Encryption

## Database Security

## Server Security

## Docker Security

## Cloud Security

## Vulnerability Assessment

## Security Checklist

## Future Improvements
"""

        result = await self.think_with_context(task)

        self.remember(task, result)

        memory.save("security", result)

        workspace.save(
            "security/security_report.md",
            result
        )

        print("💾 Security report saved")

        return result