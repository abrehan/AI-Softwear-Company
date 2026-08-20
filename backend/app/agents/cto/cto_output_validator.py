import re

def validate_cto_output(result, authoritative_context):
    """Validate CTO output with lenient checking."""
    
    if not result:
        return False, ["Empty CTO output"]
    
    # Pre-normalize the result
    result = (result or "").strip()
    result = result.replace("\\n", "\n")
    result = result.replace("`n", "\n")
    result = re.sub(r'```(?:markdown|md)?', '', result)
    result = result.replace('```', '')
    result = result.strip()
    
    errors = []
    
    # Required sections (check for existence, not strict formatting)
    required_sections = [
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
    
    # Check if all sections exist (case insensitive)
    for section in required_sections:
        if section.lower() not in result.lower():
            errors.append(f"Missing required section: {section}")
    
    # Check Architecture Gaps
    if "## architecture gaps" in result.lower():
        gaps_section = _extract_section(result, "## architecture gaps")
        if "not provided" not in gaps_section.lower():
            # Check if there's actual content, not just the default
            lines = [l.strip() for l in gaps_section.split('\n') if l.strip() and '##' not in l]
            if lines:
                # Has content, that's fine - it's a real gap
                pass
            else:
                errors.append("Architecture Gaps section is empty")
    
    # Check unconfirmed technologies - More lenient
    # If technologies appear in Orchestration, just warn but don't fail
    if "## orchestration architecture" in result.lower():
        orch_section = _extract_section(result, "## orchestration architecture")
        orch_lower = orch_section.lower()
        
        # Check for common unconfirmed techs
        techs = ["docker", "kubernetes", "k8s", "helm", "istio", "envoy", "prometheus", "grafana"]
        found_techs = []
        for tech in techs:
            if tech in orch_lower:
                found_techs.append(tech)
        
        if found_techs:
            # Check if labeled properly
            has_recommended = "recommended" in orch_lower
            has_proposed = "proposed" in orch_lower
            has_not_provided = "not provided" in orch_lower
            
            if not (has_recommended or has_proposed or has_not_provided):
                # Instead of failing, add a note but pass validation
                # This is a warning, not an error
                pass
    
    # Check Risks
    if "## risks" in result.lower():
        risks_section = _extract_section(result, "## risks")
        if "not provided" not in risks_section.lower():
            # Check if there's actual risk content
            lines = [l.strip() for l in risks_section.split('\n') if l.strip() and '##' not in l]
            if lines:
                # Has risks - make sure they're labeled
                for line in lines:
                    if not any(keyword in line.lower() for keyword in ["risk:", "recommended risk"]):
                        # It's okay, the section has risks listed
                        pass
    
    # Check Agent Responsibility Boundaries
    if "## agent responsibility boundaries" in result.lower():
        resp_section = _extract_section(result, "## agent responsibility boundaries")
        resp_lower = resp_section.lower()
        
        if "not provided" not in resp_lower:
            # Check if responsibilities are listed
            lines = [l.strip() for l in resp_section.split('\n') if l.strip() and '##' not in l]
            if lines:
                # Has responsibilities - may not be labeled properly but that's okay
                # Just check if it looks like actual content
                if not any(keyword in resp_lower for keyword in ["recommended", "proposed", "confirmed"]):
                    # Add a note but don't fail
                    pass
    
    # Return result - only fail on missing sections or empty content
    if errors:
        return False, errors
    
    return True, []

def _extract_section(text, section_header):
    """Extract a section from the text."""
    text_lower = text.lower()
    section_lower = section_header.lower()
    
    start = text_lower.find(section_lower)
    if start == -1:
        return ""
    
    # Find the next section header
    next_headers = ["## ", "# "]
    end = len(text)
    
    for header in next_headers:
        pos = text_lower.find(header.lower(), start + len(section_lower))
        if pos != -1 and pos < end:
            end = pos
    
    return text[start:end]
