from __future__ import annotations


class CTOOutputValidator:

    REQUIRED_SECTIONS = [
        "# System Architecture",
        "## Project Overview",
        "## Confirmed Current Architecture",
        "## Architecture Gaps",
        "## Recommended Technology Architecture",
        "## Orchestration Architecture",
        "## Context Architecture",
        "## Agent Responsibility Boundaries",
        "## Testing Strategy",
        "## Logging",
        "## Risks",
        "## Next Implementation Sequence",
        "## Recommendations",
    ]

    FORBIDDEN_CONFIRMED_TECHNOLOGIES = [
        "postgresql",
        "postgres",
        "redis",
        "docker",
        "docker compose",
        "kubernetes",
        "jenkins",
        "prometheus",
        "grafana",
        "haproxy",
        "celery",
        "oauth2",
        "oauth 2.0",
        "hashicorp vault",
        "vault",
        "aes-256",
        "message broker",
        "api gateway",
        "microservices",
    ]

    UNKNOWN_MARKER = "Not provided in current project context."

    def __init__(self, authoritative_context: str):
        self.authoritative_context = (
            authoritative_context or ""
        ).lower()

    def validate(
        self,
        output: str,
    ) -> tuple[bool, list[str]]:

        errors: list[str] = []

        if not output or not output.strip():
            return False, ["CTO output is empty."]

        normalized = output.lower()

        # --------------------------------------------------
        # REQUIRED STRUCTURE
        # --------------------------------------------------

        for section in self.REQUIRED_SECTIONS:
            if section.lower() not in normalized:
                errors.append(
                    f"Missing required section: {section}"
                )

        # --------------------------------------------------
        # CONFIRMED ARCHITECTURE
        # --------------------------------------------------

        confirmed_section = self._extract_section(
            output,
            "## Confirmed Current Architecture",
            "## Architecture Gaps",
        )

        if confirmed_section:

            confirmed_lower = confirmed_section.lower()

            for technology in self.FORBIDDEN_CONFIRMED_TECHNOLOGIES:

                if technology in confirmed_lower:

                    # A technology is allowed only if the
                    # authoritative context actually contains it.
                    if technology not in self.authoritative_context:

                        errors.append(
                            "Unconfirmed technology appears in "
                            "Confirmed Current Architecture: "
                            f"{technology}"
                        )

        # --------------------------------------------------
        # ARCHITECTURE GAPS
        # --------------------------------------------------

        gaps_section = self._extract_section(
            output,
            "## Architecture Gaps",
            "## Recommended Technology Architecture",
        )

        if gaps_section:

            if (
                self.UNKNOWN_MARKER.lower()
                not in gaps_section.lower()
            ):

                errors.append(
                    "Architecture Gaps must explicitly identify "
                    "unknown information using: "
                    f"'{self.UNKNOWN_MARKER}'"
                )

        # --------------------------------------------------
        # RISKS
        # --------------------------------------------------

        risks_section = self._extract_section(
            output,
            "## Risks",
            "## Next Implementation Sequence",
        )

        if risks_section:

            if (
                self.UNKNOWN_MARKER.lower()
                not in risks_section.lower()
                and "recommended risk" not in risks_section.lower()
            ):

                errors.append(
                    "Risks must either state "
                    "'Not provided in current project context.' "
                    "or explicitly label items as "
                    "'Recommended risk to evaluate'."
                )

        # --------------------------------------------------
        # RESPONSIBILITY BOUNDARIES
        # --------------------------------------------------

        responsibility_section = self._extract_section(
            output,
            "## Agent Responsibility Boundaries",
            "## Testing Strategy",
        )

        if responsibility_section:

            responsibility_lower = (
                responsibility_section.lower()
            )

            if (
                "specific responsibility boundaries are not provided"
                not in responsibility_lower
                and "recommended" not in responsibility_lower
                and "proposed" not in responsibility_lower
            ):

                errors.append(
                    "Agent responsibility boundaries must be "
                    "explicitly confirmed or labeled as "
                    "recommended/proposed."
                )

        # --------------------------------------------------
        # DEVELOPMENT SEQUENCE
        # --------------------------------------------------

        sequence_section = self._extract_section(
            output,
            "## Next Implementation Sequence",
            "## Recommendations",
        )

        if sequence_section:

            sequence_lower = sequence_section.lower()

            forbidden_completion_words = [
                "completed",
                "already implemented",
                "implemented successfully",
                "finished",
            ]

            for word in forbidden_completion_words:

                if word in sequence_lower:

                    errors.append(
                        "Development sequence must not be "
                        "described as completed."
                    )
                    break

        # --------------------------------------------------
        # RETURN
        # --------------------------------------------------

        return (
            len(errors) == 0,
            errors,
        )

    def _extract_section(
        self,
        text: str,
        start_heading: str,
        end_heading: str | None = None,
    ) -> str:

        lower = text.lower()

        start = lower.find(
            start_heading.lower()
        )

        if start == -1:
            return ""

        start += len(start_heading)

        if end_heading:

            end = lower.find(
                end_heading.lower(),
                start,
            )

            if end != -1:
                return text[start:end]

        return text[start:]


def validate_cto_output(
    output: str,
    authoritative_context: str,
) -> tuple[bool, list[str]]:

    validator = CTOOutputValidator(
        authoritative_context
    )

    return validator.validate(output)
