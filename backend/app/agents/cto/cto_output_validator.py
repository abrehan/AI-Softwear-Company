import re


REQUIRED_SECTIONS = [
    "System Architecture",
    "Project Overview",
    "Confirmed Current Architecture",
    "Architecture Gaps",
    "Recommended Technology Architecture",
    "Orchestration Architecture",
    "Context Architecture",
    "Agent Responsibility Boundaries",
    "Testing Strategy",
    "Logging",
    "Risks",
    "Next Implementation Sequence",
    "Recommendations",
]


def validate_cto_output(result, authoritative_context):
    """Validate CTO architecture without requiring exact Markdown formatting."""

    if not result:
        return False, ["Empty CTO output"]

    result = normalize_cto_output(result)

    errors = []

    # ---------------------------------------------------------
    # REQUIRED SECTIONS
    # ---------------------------------------------------------

    for section in REQUIRED_SECTIONS:
        if not section_exists(result, section):
            errors.append(
                f"Missing required section: {section}"
            )

    # ---------------------------------------------------------
    # CHECK FOR DUPLICATE SECTION BLOCKS
    # ---------------------------------------------------------

    for section in REQUIRED_SECTIONS:
        count = count_section(result, section)

        if count > 1:
            errors.append(
                f"Duplicate section detected: {section}"
            )

    # ---------------------------------------------------------
    # CHECK CONFIRMED ARCHITECTURE
    # ---------------------------------------------------------

    confirmed = extract_section(
        result,
        "Confirmed Current Architecture",
    )

    authoritative_lower = (
        authoritative_context or ""
    ).lower()

    suspicious_technologies = [
        "postgresql",
        "sqlalchemy",
        "rabbitmq",
        "docker",
        "kubernetes",
        "istio",
        "loggly",
        "prometheus",
        "grafana",
        "microservices",
        "oauth",
        "jwt",
    ]

    for technology in suspicious_technologies:
        if technology in confirmed.lower():
            if technology not in authoritative_lower:
                errors.append(
                    f"Unconfirmed technology presented as current architecture: {technology}"
                )

    # ---------------------------------------------------------
    # CHECK RECOMMENDATIONS
    # ---------------------------------------------------------

    recommended = extract_section(
        result,
        "Recommended Technology Architecture",
    )

    # Recommendations are allowed to contain proposed
    # technologies.

    # ---------------------------------------------------------
    # RETURN
    # ---------------------------------------------------------

    if errors:
        return False, errors

    return True, []


def normalize_cto_output(result):
    result = (result or "").strip()

    # Convert escaped newlines.
    result = result.replace("\\r\\n", "\n")
    result = result.replace("\\n", "\n")
    result = result.replace("`r`n", "\n")
    result = result.replace("`n", "\n")

    # Remove code fences.
    result = re.sub(
        r"```(?:markdown|md|text)?",
        "",
        result,
        flags=re.IGNORECASE,
    )

    result = result.replace("```", "")

    # Normalize bold headings:
    #
    # **Project Overview**
    #
    # becomes
    #
    # ## Project Overview
    #
    for section in REQUIRED_SECTIONS:
        pattern = rf"^\s*\*\*{re.escape(section)}\*\*\s*$"

        result = re.sub(
            pattern,
            f"## {section}",
            result,
            flags=re.IGNORECASE | re.MULTILINE,
        )

    # Normalize "# System Architecture" variations.
    result = re.sub(
        r"^\s*\*\*System Architecture\*\*\s*$",
        "# System Architecture",
        result,
        flags=re.IGNORECASE | re.MULTILINE,
    )

    # Remove accidental duplicated empty sections later.
    result = remove_duplicate_empty_sections(result)

    return result.strip()


def section_exists(text, section):
    pattern = rf"(?im)^\s*(?:#+\s*)?{re.escape(section)}\s*$"

    return re.search(pattern, text) is not None


def count_section(text, section):
    pattern = rf"(?im)^\s*(?:#+\s*)?{re.escape(section)}\s*$"

    return len(re.findall(pattern, text))


def extract_section(text, section):
    lines = text.splitlines()

    start = None

    for index, line in enumerate(lines):
        normalized = re.sub(
            r"^\s*#+\s*",
            "",
            line.strip(),
        ).strip()

        normalized = normalized.strip("* ").strip()

        if normalized.lower() == section.lower():
            start = index
            break

    if start is None:
        return ""

    content = []

    for line in lines[start + 1:]:
        stripped = line.strip()

        # Stop at next Markdown heading.
        if re.match(r"^#{1,6}\s+", stripped):
            break

        content.append(line)

    return "\n".join(content).strip()


def remove_duplicate_empty_sections(text):
    lines = text.splitlines()

    seen = set()
    output = []

    i = 0

    while i < len(lines):
        line = lines[i]

        normalized = re.sub(
            r"^\s*#+\s*",
            "",
            line.strip(),
        ).strip()

        normalized = normalized.strip("* ").strip()

        if normalized.lower() in {
            section.lower()
            for section in REQUIRED_SECTIONS
        }:
            key = normalized.lower()

            # Look ahead to determine whether this section
            # is empty.
            j = i + 1

            while j < len(lines) and not lines[j].strip():
                j += 1

            is_empty = (
                j >= len(lines)
                or lines[j].strip().lower()
                == "not provided in current project context."
            )

            if key in seen and is_empty:
                i = j + 1
                continue

            seen.add(key)

        output.append(line)
        i += 1

    return "\n".join(output)
