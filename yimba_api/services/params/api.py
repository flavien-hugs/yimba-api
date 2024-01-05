from fastapi import Security, HTTPException, Body
from fastapi.responses import JSONResponse, Response
from starlette import status

import pymongo
from yimba_api.services import router_factory
from yimba_api.services.params import model
from yimba_api.shared import crud
from yimba_api.shared.authentication import AuthTokenBearer


router = router_factory(
    prefix="/api/params",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.get(
    "/roles",
    summary="List all roles",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "client"]))],
)
@router.get(
    "/roles/{slug}",
    summary="Get single role by slug",
)
async def get_roles(slug: str = None):
    items = model.RoleInDB.find(router.storage, {"slug": slug} if slug else {})
    result = [{"key": x.slug, "value": x.name} async for x in items]
    return result


@router.post(
    "/roles",
    response_model=model.RoleInDB,
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    status_code=status.HTTP_201_CREATED,
    summary="Add new role",
)
async def add_roles(data: model.Role = Body(...)):
    if (
        ret := await model.RoleInDB.find_one(
            router.storage, {"slug": data.slug, "name": data.name}
        )
    ) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Role '{ret.slug}' is already exist !",
        )

    ret = await model.RoleInDB(**data.dict()).save(router.storage)
    return await commun.get(router.storage, model.RoleInDB, ret.inserted_id)


@router.patch(
    "/roles/{role_id}",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    summary="Update role",
)
async def update_role(role_id: str, payload: model.Role = Body(...)):
    try:
        obj = await commun.get(router.storage, model.RoleInDB, role_id)
        data = payload.dict(exclude_unset=True)
        for field, value in data.items():
            setattr(obj, field, value)
        result = await obj.update(router.storage)
    except pymongo.errors.DuplicateKeyError as pyerr:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=str(pyerr)
        ) from pyerr
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid attribute: " + str(err),
        ) from err
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "oid": role_id,
            "acknowledged": result.acknowledged,
            "modified_count": result.modified_count,
        },
    )


@router.delete(
    "/roles/{role_id}",
    response_class=Response,
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin"]))],
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete role",
)
async def delete_role(role_id: str):
    result = await commun.delete(router.storage, model.RoleInDB, role_id)
    return result
