class InvalidNameError(ValueError):
    pass

def clean_name(
    name: str,
) -> str:
    name = name.strip()

    if not name:
        raise InvalidNameError("Name cannot be blank")

    return name
