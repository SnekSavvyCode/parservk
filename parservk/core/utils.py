import inspect


def name_from_class(class_: object) -> str:
    """
    Returns the class name in lowercase.

    :param class_: subclass of Base.
    :return: class name in lowercase.
    """
    
    return class_.__name__.lower()

def url_from_class(class_: object) -> str:
    """
    Returns the URL for the class.

    :param class_: subclass of Base.
    :return: URL for the class.
    """
    
    return f"{class_.URL_API}{name_from_class(class_)}"

def submethods_from_class(class_: object) -> dict:
    """
    Returns a dictionary with method names in lowercase.

    :param class_: subclass of Base.
    :return: dictionary with method names in lowercase.
    """
    
    return {name.lower(): f".{name}" for name, _ in inspect.getmembers(class_, predicate=inspect.isfunction) if not name.count("_")}

def multi_ids_from_class(class_: object) -> list:
    """
    Returns a list of attributes ending with "ids".

    :param class_: subclass of Base.
    :return: list of attributes ending with "ids".
    """
    
    return [attr for attr in class_.DATACLASS.__fields__ if attr.endswith("ids")]

def method_from_class(class_: object) -> dict:
    """
    Returns a dictionary with class information.

    :param class_: subclass of Base.
    :return: dictionary with class information.
    """
    
    url = url_from_class(class_)
    methods = submethods_from_class(class_)
    multi_ids = multi_ids_from_class(class_)
    name = name_from_class(class_)
    
    return {"url": url, "methods": methods, "multi_ids": multi_ids, "name": name}

def called_from(is_nested_function: bool = False) -> str:
    """
    Returns the name of the function that called the current function.

    :param is_nested_function: flag indicating whether the function is nested.
    :return: name of the function that called the current function.
    """
    
    stack = inspect.stack()[2][0] if is_nested_function else inspect.stack()[1][0]
    frame_func = inspect.getframeinfo(stack)
    
    return frame_func.function