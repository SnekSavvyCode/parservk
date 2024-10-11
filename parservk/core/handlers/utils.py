import re
import logging
import inspect

from typing import Any, Optional, Union

from .basehandler import BaseHandler

def create_compile_from_class(class_: object, *args: Any, **kwargs: Any) -> tuple[re.Pattern, object, str]:
    """
    Creates a regular expression based on the class.

    :param class_: A subclass of BaseHandler.
    :param args: Additional arguments for creating an instance of the class.
    :param kwargs: Keyword arguments for creating an instance of the class.
    
    :return: A tuple containing:
        - A compiled regular expression.
        - An instance of the class.
        - The name of the class.
    """

    name = class_.get_name(class_)
    re_compile = re.compile(f"""{class_.RE_URL_API}{name}\.[a-zA-Z]+""", re.VERBOSE)
    
    return re_compile, class_(*args, **kwargs), name

def create_compiles(*args: Any, **kwargs: Any) -> list[tuple]:
    """
    Creates a list of compilations for all subclasses of BaseHandler.

    :param args: Additional arguments for creating instances of classes.
    :param kwargs: Keyword arguments for creating instances of classes.
    
    :return: A list of tuples with regular expressions, objects, and class names.
    """

    return [create_compile_from_class(child_class, *args, **kwargs) for child_class in get_subclasses()]

def create_names() -> list[str]:
    """
    Creates a list of names for all subclasses of BaseHandler.

    :return: A list of names.
    """
 
    return [child_class.get_name(child_class) for child_class in get_subclasses()]

def create_names_and_obj() -> dict[str, object]:
    """
    Creates a dictionary with names and objects of all subclasses of BaseHandler.

    :return: A dictionary where keys are names and values are objects.
    """
    
    return dict(zip(create_names(), get_subclasses()))

def get_subclasses() -> list:
    """
    Gets an list for all subclasses of BaseHandler.

    :return: An list of subclasses.
    """

    return BaseHandler.__subclasses__()

def get_submethods_from_method(method: str, skipped_handlers: list[str] = []) -> dict[str, Any]:
    """
    Extracts submethods from the specified method.

    :param method: The name of the method.
    :param skipped_handlers: Handlers to skip.
    :return: A dictionary of submethods.
    """
    re_handler = re.compile(r".+_handler")
    obj = get_obj_from_method(method)
    submethods = inspect.getmembers(obj, predicate=inspect.isfunction)
    
    return {submethod[0].split("_")[0]: submethod[-1] for submethod in submethods if re_handler.fullmatch(submethod[0]) and not submethod[0] in skipped_handlers}

def get_obj_from_method(method: str, default: Optional[Any] = None) -> Union[Optional[Any], object]:
    """
    Gets an object from the method by name.

    :param method: The name of the method.
    :param default: A default value if the method is not found.
    
    :return: An object or the default value.
    """
    
    return create_names_and_obj().get(method.lower(), default)

def is_method_supported(method: str, enable_logging: Optional[logging.Logger] = None) -> bool:
    """
    Checks if the method is supported and performs logging.

    :param method: The name of the method.
    :param enable_logging: A logger object.
    
    :return: True if the method is supported, otherwise False.
    """
    result = method.lower() in create_names()
    
    if not result and enable_logging is not None:
        enable_logging.warning(f"The method '{method}' is not supported by the BaseHandler.")
    
    return result

def is_submethod_supported(submethod: str, method: str, enable_logging: Optional[logging.Logger] = None):
	"""
	Checks if the submethod is supported and performs logging.

    :param submethod: Submethod of method.
    :param methods: Method from child BaseHandler.
    
    :return: The object of a submethod or False.
    """
    
	result, method = is_submethod_in_methods(submethod, [method])
	
	if not result[0] and enable_logging is not None:
		obj = get_obj_from_method(method[0])
		enable_logging.warning(f"The submethod '{submethod}' is not supported by the '{obj.__name__}'.")
	
	return result[0]
		

def is_submethod_in_methods(submethod: str, methods: list[str]) -> tuple[list[bool], list[str]]:
    """
    Checks for the presence of submethods in a list of methods.

    :param submethod: Submethod of method.
    :param methods: A list of methods.
    
    :return: A tuple containing a list of results and the original list of methods.
    """

    results = []
    for method in methods:
        results.append(get_submethods_from_method(method).get(submethod, False))
    
    return results, methods