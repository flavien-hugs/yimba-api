import secrets
from typing import Optional

import pymongo
from fastapi import Body, HTTPException, Query, Security
from fastapi.responses import JSONResponse
from fastapi_pagination import paginate
from starlette import status

from jose import JWTError
from yimba_api.shared import crud, service
from yimba_api.services.auth import model
from yimba_api.services import router_factory
from yimba_api.shared.authentication import (
    AuthTokenBearer,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)

router = router_factory(
    prefix="/api/auth",
    tags=["CRUD"],
    responses={404: {"description": "Not found"}},
)


@router.get("/@ping")
def ping():
    return {"message": "pong !"}


@router.post("/users", response_model=model.UserOutSchema, summary="Create a User")
@router.post(
    "/users/clients", response_model=model.UserOutSchema, summary="Create client User"
)
async def create_user(payload: model.SignupUser = Body(...)):
    try:
        hashed_password = model.UserInDB.hash_password(payload.password)
        payload_role = await service.validate_roles_exist(payload.role)
        user = model.UserInDB(
            role=payload_role,
            email=payload.email.lower(),
            password=hashed_password,
        )

        result = await user.save(router.storage)
        response = JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={
                "oid": result.inserted_id,
                "acknowledged": result.acknowledged,
                "inserted_id": result.inserted_id,
            },
        )
    except pymongo.errors.DuplicateKeyError as error:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cette adresse e-mail: '{payload.email}' est déjà utilisé !",
        ) from error

    return response


@router.get(
    "/users",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "staff"]))],
    response_model=crud.CustomPage[model.UserOutSchema],
    summary="Get all Users Or Search Users",
)
async def get_users(
    query: Optional[str] = Query(
        None, alias="search", description="Search User by Adress Email or Fullname"
    )
):
    search_filter = (
        {
            "$or": [
                {"email": {"$regex": query, "$options": "i"}},
                {"fullname": {"$regex": query, "$options": "i"}},
            ]
        }
        if query
        else {}
    )

    users = model.UserInDB.find(router.storage, search_filter if query else {})
    result = paginate([user async for user in users])
    return result


@router.get(
    "/users/{user_id}",
    response_model=model.UserOutSchema,
    dependencies=[
        Security(AuthTokenBearer(allowed_role=["admin", "staff", "company", "client"]))
    ],
    summary="Get single User",
)
async def get_user(user_id: str):
    result = await crud.get(
        router.storage, model.UserInDB, user_id, name=f"User with ID '{user_id}'"
    )
    return model.UserOutSchema(**result.dict())


@router.patch(
    "/users/{user_id}",
    summary="Update User",
)
async def update_user(
    user_id: str,
    payload: model.UpdateUser = Body(...),
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin", "staff"])),
):
    result = await crud.patch(router.storage, model.UserInDB, user_id, payload)
    return result


@router.put(
    "/users/{user_id}",
    summary="Manage account",
)
async def manage_account_status(
    user_id: str,
    payload: model.ManageAccount = Body(...),
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin"])),
):
    user = await crud.get(
        router.storage,
        model.UserInDB,
        user_id,
        name=f"User with ID '{user_id}'",
    )
    user.is_active = payload.is_active
    await user.update(router.storage)
    action = "activé" if payload.is_active else "désactivé"

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            "message": f"Le compte Utilisateur '{user.email.lower()}' a été {action} avec succès."
        },
    )


@router.delete(
    "/users/{user_id}",
    summary="Delete User",
)
async def delete_user(
    user_id: str,
    current_user: str = Security(AuthTokenBearer(allowed_role=["admin"])),
):
    result = await crud.delete(router.storage, model.UserInDB, user_id)
    return result


@router.post("/login", summary="Login User", response_model=model.UserLoginOutDB)
async def login(payload: model.LoginUser = Body(...)):
    if not (
        user := await model.UserInDB.find_one(
            router.storage, {"email": payload.email.lower()}
        )
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Adresse e-mail incorrecte ou n'existe pas.",
        )

    if user and not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Votre compte a été désactivé. Contacter l'administrateur principal !",
        )

    if user and not model.UserInDB.verify_password(payload.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Votre mot de passe est incorrecte",
        )

    return model.UserLoginOutDB(
        **{
            "access_token": create_access_token(
                user=str(user.id), email=payload.email, role_or_type=str(user.role)
            ),
            "refresh_token": create_refresh_token(
                user=str(user.id), email=payload.email, role_or_type=str(user.role)
            ),
            "user": user.dict(),
        }
    )


@router.post("/change-password", summary="Change user password and Send email")
async def change_password(payload: model.ChangePassword = Body(...)):
    try:
        if not (
            user := await model.UserInDB.find_one(
                router.storage, {"email": payload.email.lower()}
            )
        ):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"L'utilisateur avec l'e-mail '{payload.email}' n'a pas été trouvé.",
            )

        password = secrets.token_urlsafe(6)
        user.password = model.UserInDB.hash_password(password)
        await crud.patch(router.storage, model.UserInDB, user.id, user)
        response = JSONResponse(
            status_code=status.HTTP_201_CREATED,
            content={"message": f"Votre nouveau mot de passe est : {password}"},
        )
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(err),
        ) from err
    return response


@router.post(
    "/logout",
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "staff"]))],
    response_model=dict,
    summary="Logout User",
    deprecated=True,
)
async def logout(user: model.LogoutUser = Body(...)):
    return {"message": "Logout successful"}


@router.post(
    "/refresh-token",
    response_model=dict,
    dependencies=[Security(AuthTokenBearer(allowed_role=["admin", "staff"]))],
    summary="Refresh Access Token",
)
async def refresh_token(data: model.LogoutUser = Body(...)):
    try:
        payload = decode_refresh_token(data.refresh_token)
        token = {
            "access_token": create_access_token(
                user=payload.sub, email=payload.email, role_or_type=payload.role_or_type
            ),
            "refresh_token": create_refresh_token(
                user=payload.sub, email=payload.email, role_or_type=payload.role_or_type
            ),
        }
    except JWTError as err:
        raise HTTPException(
            status_code=err.status_code,
            detail=str(err.detail),
        ) from err
    return token
