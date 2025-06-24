from enum import StrEnum


class YimbaApifyErrorCode(StrEnum):
    VALUE_ERROR = "document/document-value-error"
    MISSING_PARAMETER = "document/missing-parameter"
    PARAMETER_CONFLICT = "document/document-conflict"
    DOCUMENT_NOT_FOUND = "document/document-not-found"
    DOCUMENT_ALREADY_EXISTS = "document/document-already-exists"
    BAD_REQUEST = "collect-data/bad-request"
