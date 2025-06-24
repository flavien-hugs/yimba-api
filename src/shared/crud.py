from typing import Type

from beanie import Document, PydanticObjectId
from fastapi import HTTPException, Body, status
from fastapi.encoders import jsonable_encoder
from fastapi_pagination import Page
from fastapi_pagination.customization import CustomizedPage, UseOptionalParams
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import BaseModel

from src.common.helpers.exceptions import CustomHTTException
from .error_codes import YimbaApifyErrorCode

disable_installed_extensions_check()


def customize_page(model):
    return CustomizedPage[Page, UseOptionalParams()]


def encode_input(data) -> dict:
    req = jsonable_encoder(data)
    data = {k: v for k, v in req.items()}
    return data


async def get(document: Type[Document], id: PydanticObjectId) -> Document:
    if (doc := await document.get({"_id": PydanticObjectId(id)})) is None:
        raise CustomHTTException(
            code_error=YimbaApifyErrorCode.DOCUMENT_NOT_FOUND,
            message_error=f"{document.__name__} with value '{id}' not found!",
            status_code=status.HTTP_404_NOT_FOUND,
        )

    return doc


async def post(document: Type[Document], payload: BaseModel = Body(...)) -> Document:
    try:
        doc = await document(**payload.model_dump()).create()
    except HTTPException as err:
        raise CustomHTTException(
            code_error=YimbaApifyErrorCode.DOCUMENT_ALREADY_EXISTS,
            message_error=str(err),
            status_code=status.HTTP_409_CONFLICT,
        ) from err

    return doc


async def patch(document: Type[Document], id: PydanticObjectId, payload: BaseModel = Body(...)) -> Document:
    doc = await get(document=document, id=PydanticObjectId(id))
    result = await doc.set({**payload.model_dump(exclude_none=True, exclude_unset=True)})
    return result


async def delete(document: Type[Document], id: PydanticObjectId) -> None:
    doc = await get(document=document, id=PydanticObjectId(id))
    await doc.delete()
