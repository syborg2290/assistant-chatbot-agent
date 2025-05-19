import uuid


def uuid_to_str(obj, seen=None):
    """
    Convert UUID objects to strings and handle circular references.
    This method will track objects that are already serialized.
    """
    if seen is None:
        seen = set()

    # Prevent circular references by checking if the object is already serialized
    if id(obj) in seen:
        return None  # You can return None or a placeholder value to break the reference
    seen.add(id(obj))

    # Handle UUID conversion
    if isinstance(obj, uuid.UUID):
        return str(obj)

    # Handle nested objects with __dict__ attribute
    if hasattr(obj, "__dict__"):
        return {key: uuid_to_str(value, seen) for key, value in obj.__dict__.items()}

    # Default return value for any non-serializable objects
    return obj
