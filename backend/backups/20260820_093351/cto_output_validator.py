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
        "oauth",
        "hashicorp vault",
        "vault",
        "aes-256",
        "message broker",
        "api gateway",
        "microservices",
        "aws",
        "azure",
        "google cloud",
        "gcp",
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

        # ==================================================
        # REQUIRED STRUCTURE
        # ==================================================

        for section in self.REQUIRED_SECTIONS:

            if section.lower() not in normalized:

                errors.append(
                    f"Missing required section: {section}"
                )

        # ==================================================
        # MARKDOWN / FORMAT QUALITY
        # ==================================================

        # Detect literal escaped newlines such as:
        # `n2. instead of:
        # 2.
        if "`n" in output or "\\n" in output:

            errors.append(
                "CTO output contains literal escaped newline "
                "characters. Use real line breaks."
            )

        # Detect accidental code fences.
        if "```" in output:

            errors.append(
                "CTO output must not contain Markdown code fences."
            )

        # ==================================================
        # CONFIRMED CURRENT ARCHITECTURE
        # ==================================================

        confirmed_section = self._extract_section(
            output,
            "## Confirmed Current Architecture",
            "## Architecture Gaps",
        )

        if confirmed_section:

            confirmed_lower = confirmed_section.lower()

            for technology in self.FORBIDDEN_CONFIRMED_TECHNOLOGIES:

                if technology in confirmed_lower:

                    if technology not in self.authoritative_context:

                        errors.append(
                            "Unconfirmed technology appears in "
                            "Confirmed Current Architecture: "
                            f"{technology}"
                        )

        # ==================================================
        # ARCHITECTURE GAPS
        # ==================================================

        gaps_section = self._extract_section(
            output,
            "## Architecture Gaps",
            "## Recommended Technology Architecture",
        )

        if gaps_section:

            gaps_lower = gaps_section.lower()

            if self.UNKNOWN_MARKER.lower() not in gaps_lower:

                errors.append(
                    "Architecture Gaps must explicitly contain: "
                    f"'{self.UNKNOWN_MARKER}'"
                )

            # Architecture Gaps must not become a place for
            # invented architecture.
            for technology in self.FORBIDDEN_CONFIRMED_TECHNOLOGIES:

                if technology in gaps_lower:

                    errors.append(
                        "Architecture Gaps contains an "
                        "unconfirmed technology: "
                        f"{technology}. "
                        "Move it to Recommended Technology Architecture "
                        "or state that it is not provided."
                    )

        # ==================================================
        # ORCHESTRATION ARCHITECTURE
        # ==================================================

        orchestration_section = self._extract_section(
            output,
            "## Orchestration Architecture",
            "## Context Architecture",
        )

        if orchestration_section:

            orchestration_lower = (
                orchestration_section.lower()
            )

            for technology in self.FORBIDDEN_CONFIRMED_TECHNOLOGIES:

                if technology in orchestration_lower:

                    if technology not in self.authoritative_context:

                        errors.append(
                            "Unconfirmed technology appears in "
                            "Orchestration Architecture: "
                            f"{technology}. "
                            "Label it Recommended/Proposed or "
                            "state that it is not provided."
                        )

        # ==================================================
        # CONTEXT ARCHITECTURE
        # ==================================================

        context_section = self._extract_section(
            output,
            "## Context Architecture",
            "## Agent Responsibility Boundaries",
        )

        if context_section:

            context_lower = context_section.lower()

            for technology in self.FORBIDDEN_CONFIRMED_TECHNOLOGIES:

                if technology in context_lower:

                    if technology not in self.authoritative_context:

                        errors.append(
                            "Unconfirmed technology appears in "
                            "Context Architecture: "
                            f"{technology}. "
                            "Label it Recommended/Proposed or "
                            "state that it is not provided."
                        )

        # ==================================================
        # RISKS
        # ==================================================

        risks_section = self._extract_section(
            output,
            "## Risks",
            "## Next Implementation Sequence",
        )

        if risks_section:

            risks_lower = risks_section.lower()

            if (
                self.UNKNOWN_MARKER.lower()
                not in risks_lower
                and "recommended risk to evaluate" not in risks_lower
            ):

                errors.append(
                    "Risks must either state "
                    f"'{self.UNKNOWN_MARKER}' "
                    "or explicitly label items as "
                    "'Recommended risk to evaluate'."
                )

        # ==================================================
        # RESPONSIBILITY BOUNDARIES
        # ==================================================

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
                and "recommended responsibility" not in responsibility_lower
                and "proposed responsibility" not in responsibility_lower
            ):

                errors.append(
                    "Agent responsibility boundaries must be "
                    "explicitly confirmed or labeled as "
                    "'Recommended responsibility' or "
                    "'Proposed responsibility'."
                )

        # ==================================================
        # TESTING STRATEGY
        # ==================================================

        testing_section = self._extract_section(
            output,
            "## Testing Strategy",
            "## Logging",
        )

        if testing_section:

            if (
                not testing_section.strip()
                or testing_section.strip().lower()
                == self.UNKNOWN_MARKER.lower()
            ):
                pass

        # ==================================================
        # DEVELOPMENT SEQUENCE
        # ==================================================

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
                "has been implemented",
                "is already implemented",
            ]

            for word in forbidden_completion_words:

                if word in sequence_lower:

                    errors.append(
                        "Development sequence must not be "
                        "described as completed."
                    )

                    break

            # Detect literal escaped newline formatting.
            if "`n" in sequence_section:

                errors.append(
                    "Next Implementation Sequence contains "
                    "literal `n characters. Use real newlines."
                )

        # ==================================================
        # RECOMMENDATIONS
        # ==================================================

        recommendations_section = self._extract_section(
            output,
            "## Recommendations",
            None,
        )

        if recommendations_section:

            # Recommendations may be empty/unknown, but if
            # technology is proposed it should be explicitly
            # labeled as Recommended/Proposed/Suggested.
            recommendation_lower = (
                recommendations_section.lower()
            )

            for technology in self.FORBIDDEN_CONFIRMED_TECHNOLOGIES:

                if technology in recommendation_lower:

                    if not any(
                        marker in recommendation_lower
                        for marker in [
                            "recommended",
                            "proposed",
                            "suggested",
                            "should be evaluated",
                        ]
                    ):

                        errors.append(
                            "Technology in Recommendations must be "
                            "explicitly labeled Recommended, Proposed, "
                            "Suggested, or Should be evaluated."
                        )

                        break

        # ==================================================
        # RETURN
        # ==================================================

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
