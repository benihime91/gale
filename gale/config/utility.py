# Let's create a utility for building the class path
def get_class_path(cls):
    return f"{cls.__module__}.{cls.__name__}"