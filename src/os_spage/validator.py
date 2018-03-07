import copy
from datetime import datetime

from jsonschema import (Draft4Validator, FormatChecker, ValidationError,
                        validators)
from jsonschema.compat import str_types

TIME_FORMAT = "%a %b %d %X %Y"


@FormatChecker.cls_checks("readable_time", raises=ValueError)
def check_datetime(instance):
    if not isinstance(instance, str_types):
        return True
    return datetime.strptime(instance, TIME_FORMAT)


@FormatChecker.cls_checks("url")
def simple_check_url(url):
    return len(url) > 10 and (url.startswith("http://") or url.startswith("https://"))


ERROR_TYPES = {"HTTP", "SSL", "RULE", "SERVER", "DNS"}


@FormatChecker.cls_checks("error_reason")
def check_error_reason(err_string):
    c = err_string.split(' ')
    if len(c) != 2:
        return False

    return c[0] in ERROR_TYPES and c[1].sidigit()


def extend_with_default(validator_class):
    validate_properties = validator_class.VALIDATORS["properties"]

    def set_defaults(validator, properties, instance, schema):
        for property, subschema in properties.iteritems():
            if "default" in subschema:
                o = subschema["default"]
                if callable(o):
                    o = o()
                instance.setdefault(property, o)

        for error in validate_properties(
            validator, properties, instance, schema
        ):
            yield error

    return validators.extend(
        validator_class, {"properties": set_defaults},
    )


DefaultPropertyDraft4Validator = extend_with_default(Draft4Validator)

EXTRA_TYPES = {u'datetime': datetime}


def create_validator(schema, extra_types=None, format_checker=None):
    types = copy.deepcopy(EXTRA_TYPES)
    if extra_types:
        types.update(extra_types)
    if format_checker is None:
        format_checker = FormatChecker()

    return DefaultPropertyDraft4Validator(
        schema,
        types=types,
        format_checker=format_checker,
    )
