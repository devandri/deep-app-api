def get_field_name(loc: tuple) -> str:
    parts = list(loc)
    
    if parts[:2] == ["body", "payload"]:
        parts = parts[2:]
        
    return ".".join(str(part) for part in parts)