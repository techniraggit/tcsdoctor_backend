from django.core.validators import RegexValidator, _lazy_re_compile
from django.utils.translation import gettext_lazy as _

validator_ascii = RegexValidator(
    regex=r"^[\x00-\x7F]*$", message="Only ASCII characters allowed"
)

pincode_validator = RegexValidator(
    _lazy_re_compile(
        r"(?:^[A-Z]{1,2}\d[A-Z\d]? ?\d[A-Z]{2}$)|(?:^\d{5}[-]?(?:\d{4,6})?$)|(?:^\d{6}$)"
    ),
    message=_("Enter a valid pincode."),
    code="invalid",
)
