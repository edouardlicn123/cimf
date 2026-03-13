from .base import BaseField
from .string import StringField
from .string_long import StringLongField
from .text import TextField
from .text_long import TextLongField
from .text_with_summary import TextWithSummaryField
from .boolean import BooleanField
from .integer import IntegerField
from .decimal import DecimalField
from .float import FloatField
from .entity_reference import EntityReferenceField
from .file import FileField
from .image import ImageField
from .link import LinkField
from .email import EmailField
from .telephone import TelephoneField
from .datetime import DatetimeField
from .timestamp import TimestampField
from .geolocation import GeolocationField
from .color import ColorField
from .ai_tags import AITagsField
from .identity import IdentityField
from .masked import MaskedField
from .biometric import BiometricField
from .address import AddressField
from .gis import GISField

FIELD_TYPES = {
    'string': StringField,
    'string_long': StringLongField,
    'text': TextField,
    'text_long': TextLongField,
    'text_with_summary': TextWithSummaryField,
    'boolean': BooleanField,
    'integer': IntegerField,
    'decimal': DecimalField,
    'float': FloatField,
    'entity_reference': EntityReferenceField,
    'file': FileField,
    'image': ImageField,
    'link': LinkField,
    'email': EmailField,
    'telephone': TelephoneField,
    'datetime': DatetimeField,
    'timestamp': TimestampField,
    'geolocation': GeolocationField,
    'color': ColorField,
    'ai_tags': AITagsField,
    'identity': IdentityField,
    'masked': MaskedField,
    'biometric': BiometricField,
    'address': AddressField,
    'gis': GISField,
}

def get_field_type(name):
    return FIELD_TYPES.get(name, StringField)

def get_all_field_types():
    return FIELD_TYPES
