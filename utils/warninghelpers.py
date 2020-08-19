import warnings


class DeprecationWarning(DeprecationWarning):
    pass


warnings.simplefilter("default", DeprecationWarning)


# Deprecation warnings are disabled by default in Python 2.7, so this helper function enables them back.
def deprecation_warning(msg, stacklevel=0):
    warnings.warn(msg, category=DeprecationWarning, stacklevel=stacklevel + 1)
