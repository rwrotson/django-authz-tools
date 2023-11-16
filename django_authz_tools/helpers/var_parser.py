import inspect
from dataclasses import dataclass
from enum import StrEnum, auto
from types import FrameType, ModuleType
from typing import Any, Type, TypeVar, Self

from django_authz_tools.exceptions import AuthzToolsException


class VariableNotFoundException(AuthzToolsException):
    """
    Raised when a variable is not found in a given frame.
    """
    pass


class AmbiguousVariableNameException(AuthzToolsException):
    """
    Raised when there's several suitable variables in a given frame,
    when there must be only one.
    """
    pass


class ValidationError(AuthzToolsException):
    """
    Raised when trying to create object with inconsistent or impossible values.
    """
    pass


def obj_name(obj: Any, frame: FrameType | None = None) -> str:
    """
    Get name of the particular variable, if it is possible in Python.

    WARNING: result is not guarantined.
    Raises AmbiguousVariableNameException in a set of regular cases.
    """

    frame: FrameType = frame or inspect.currentframe().f_back
    var_names = set()
    try:
        for name, value in frame.f_back.f_locals.items():
            if value is obj:
                var_names.add(name)
    finally:
        del frame

    if not var_names:
        raise VariableNotFoundException("Variable with the given value not found.")
    elif len(var_names) != 1:
        raise AmbiguousVariableNameException("Multiple variables with a given value found.")

    return var_names.pop()


class AccessType(StrEnum):
    """
    Types of objects detected by their case and code style.
    """

    PUBLIC = auto()
    PROTECTED = auto()
    PRIVATE = auto()
    DUNDER = auto()

    @classmethod
    def from_obj_name(cls, name: str) -> Self:
        if name[-2:] == "__" and name[:2] == "__":
            return AccessType.DUNDER
        elif name[:2] == "__":
            return AccessType.PRIVATE
        elif name[:1] == "_":
            return AccessType.PROTECTED
        return AccessType.PUBLIC

    @classmethod
    def from_obj(cls, obj: Any) -> Self:
        return cls.from_obj_name(name=obj_name(obj))

    @classmethod
    def from_str(cls, access_type_name: str) -> Self:
        access_type_name = access_type_name.upper()
        if not hasattr(cls, access_type_name):
            raise ValueError("No such string among AccessType members")
        return getattr(cls, access_type_name)

    def __str__(self):
        return super().upper()


def _is_const(name: str) -> bool:
    return name == name.upper()


def _is_class(name: str) -> bool:
    first_char, other_chars = name.strip("_")[1], name.strip("_")[0:]
    return (
        first_char.isupper() and
        "_" not in name and
        any([char != char.upper() for char in name])
    )


def _readonly_property(attr_name: str) -> Any:
    """
    Shortcut for making read-only property for a protected attribute.
    """

    def getter(self) -> Any:
        return getattr(self, f"_{attr_name}")

    return property(fget=getter)


TObj = TypeVar("TObj", bound=object)


class ObjInfo:
    """
    Class for parsing object info from object or module.
    Implemented as frozen class: you can't change it after initialization.
    """

    name: str
    value: TObj
    type: Type[TObj]
    access_type: AccessType
    is_const: bool
    is_class: bool
    is_callable: bool

    property_names = ["name", "value", "type", "access_type", "is_const", "is_class", "is_callable"]
    __slots__ = property_names + [f"_{name}" for name in property_names]

    def __init__(
        self,
        name: str,
        value: TObj,
        type: Type[TObj],  # noqa
        access_type: AccessType | str,
        is_const: bool,
        is_class: bool,
        is_callable: bool,
    ):
        args = [name, value, type, access_type, is_const, is_class, is_callable]
        for name, value in zip(self.property_names, args):
            setattr(self, f"_{name}", value)

        self.validate()
        self._set_readonly_properties()

    @classmethod
    def from_obj(cls, obj: TObj) -> Self:
        """
        This implementation uses unreliable obj_name(obj) function.
        We reccomend to use self.from_name_and_value(name, value) instead.
        """

        return cls.from_name_and_value(name=obj_name(obj), value=obj)

    @classmethod
    def from_name_and_value(cls, name: str, value: Any) -> Self:
        """
        Recommended reliable way to construct ObjInfo instance.
        """

        return cls(
            name=name,
            type=type(value),
            value=value,
            access_type=AccessType.from_obj_name(name),
            is_const=_is_const(name),
            is_class=_is_class(name),
            is_callable=callable(value),
        )

    def validate(self):
        self._types_consistent(value=self.value, type_=self.type)

    @staticmethod
    def _types_consistent(value: TObj, type_: Type[TObj]) -> None:
        if type(value) != type_:
            raise ValidationError(
                f"Object with {value=} is of type {type(value)}, must be of {type_}!"
            )

    def _set_readonly_properties(self):
        for property_name in self.property_names:
            setattr(self, property_name, _readonly_property(property_name))

    def __str__(self):
        return (
            f"VarInfo "
            f"<{self.name=}, {self.type=}, {self.value=}, "
            f"{self.access_type=}, {self.is_const=}, {self.is_class=}"
            f"{self.is_callable=}>"
        )


@dataclass(frozen=True, slots=True)
class ParsingOptions:
    """
    Tell which objects to parse from module.
    """

    access_types: set[AccessType] | None = None
    is_const: bool | None = None
    is_class: bool | None = None
    is_callable: bool | None = None

    def is_valid_for(self, name: str, value: Any) -> bool:
        obj_info = ObjInfo.from_name_and_value(name, value)

        is_access_valid = not self.access_types or (obj_info.access_type in self.access_types)
        is_other_valid = all([b in [True, None] for b in (self.is_class, self.is_class, self.is_callable)])

        return is_access_valid and is_other_valid

    def __str__(self):
        return (
            f"ParsingConfig "
            f"<{self.access_types=}, {self.is_const=} "
            f"{self.is_class=}, {self.is_callable=}>"
        )


def parse_module_attrs(module: ModuleType, options: ParsingOptions | None = None) -> list[ObjInfo]:
    def value(attr_name: str) -> Any:
        return getattr(module, attr_name)

    return [
        ObjInfo.from_name_and_value(name, value(name))
        for name in dir(module)
        if options and options.is_valid_for(name, value(name))
    ]


def parse_consts_from_module(module: ModuleType) -> list[ObjInfo]:
    return parse_module_attrs(
        module=module,
        options=ParsingOptions(
            access_types={
                AccessType.PUBLIC,
            },
            is_const=True,
            is_class=False,
            is_callable=False,
        ),
    )