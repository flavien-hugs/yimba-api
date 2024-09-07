from beanie import PydanticObjectId
from fastapi import HTTPException
from fastapi.responses import JSONResponse
from fastapi_pagination import Page, paginate
from fastapi_pagination.customization import CustomizedPage, UseOptionalParams
from fastapi_pagination.utils import disable_installed_extensions_check
from starlette import status

disable_installed_extensions_check()


def customize_page(model):
    return CustomizedPage[Page, UseOptionalParams()]


async def find_all(storage, model):
    result = model.find(storage, {})
    data = paginate([item async for item in result])
    return data


async def get(storage, model, oid: str, name: str = None):
    if (result := await model.find_one(storage, {"_id": oid})) is not None:
        return result
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name or 'Item'} not found.")


async def post(storage, model, data: dict):
    try:
        result = await model(**data.dict()).save(storage)
        response = JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "oid": result.inserted_id,
                "acknowledged": result.acknowledged,
                "inserted_id": result.inserted_id,
            },
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    return response


async def patch(storage, model, oid: str, data: dict, name: str = None):
    if (obj := await model.find_one(storage, {"_id": oid})) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{name or 'Item'} not found.")
    updated_data = data.dict(exclude_unset=True)
    for field, value in updated_data.items():
        setattr(obj, field, value)

    result = await obj.update(storage)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "oid": oid,
            "acknowledged": result.acknowledged,
            "modified_count": result.modified_count,
        },
    )


async def put(storage, model, oid: str, data: dict):
    obj = model(**data.dict())
    try:
        obj.id = PydanticObjectId(oid)
        result = await obj.update(storage)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid attribute: " + str(err),
        ) from err
    return JSONResponse(
        status_code=status.HTTP_200_OK if result.modified_count > 0 else status.HTTP_404_NOT_FOUND,
        content={
            "oid": oid,
            "acknowledged": result.acknowledged,
            "modified_count": result.modified_count,
        },
    )


async def delete(storage, model, oid: str):
    result = await model.delete_one(storage, oid)
    return JSONResponse(
        status_code=status.HTTP_200_OK if result.deleted_count > 0 else status.HTTP_404_NOT_FOUND,
        content={
            "oid": oid,
            "acknowledged": result.acknowledged,
            "deleted_count": result.deleted_count,
        },
    )
