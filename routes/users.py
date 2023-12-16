import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.models.user import User
from app.requests.user import UserCreateRequest, UserUpdateRequest
from app.responses.user import (
    PaginatedUserResponse,
    SingleUserResponse
)
from app.services.user import UserService
from config.database import get_session

user_service = UserService(db=None)

route = APIRouter(
    prefix="/api", tags=["Users"], responses={404: {"description": "Not found"}}
)


@route.get("/users", status_code=200, response_model=PaginatedUserResponse)
async def get_users(
    page: Optional[int] = Query(1, description="Page number", gt=0),
    items_per_page: Optional[int] = Query(10, description="Items per page", gt=0),
    sort_type: Optional[str] = Query('asc', description="Sort type (asc or desc)"),
    sort_by: Optional[str] = Query('id', description="Sort by field"),
    db: Session = Depends(get_session),
):
    """
    Get a list of users with pagination.

    Args:
        page (int): The page number.
        items_per_page (int): Number of items per page.
        sort_by (str): Sort by field.
        sort_type (str): Sort type (asc or desc).
        db (Session): SQLAlchemy database session.

    Returns:
        List[UserResponse]: List of user objects.
    """
    try:
        user_service.db = db
        items, total, last_page, first_item, last_item = user_service.all(page, items_per_page, sort_type=sort_type, sort_by=sort_by)

        if not items:
            raise ValueError("No users found")

        return {
            "data": items,
            "meta": {
                "current_page": page,
                "last_page": last_page,
                "first_item": first_item,
                "last_item": last_item,
                "items_per_page": items_per_page,
                "total": total,
            },
            "status_code": 200,
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"{e}")
    except Exception as e:
        logging.error(e)
        raise HTTPException(status_code=500, detail="Internal server error")


@route.get("/users/{id}", status_code=200, response_model=SingleUserResponse)
async def get_user(id: int, db: Session = Depends(get_session)):
    """
    Get a user by their unique identifier.

    Args:
        id (int): The unique identifier of the user.
        db (Session): SQLAlchemy database session.

    Returns:
        UserResponse: User object.
    """
    try:
        user_service.db = db
        user = user_service.find(id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"data": user, "status_code": 200}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@route.post("/users", status_code=201, response_model=SingleUserResponse)
async def create_user(user: UserCreateRequest, db: Session = Depends(get_session)):
    """
    Create a new user.

    Args:
        user (UserCreateRequest): User creation request.
        db (Session): SQLAlchemy database session.

    Returns:
        UserCreateResponse: Created user object.

    Raises:
        HTTPException: If there is an internal server error.

    """
    try:
        user_service.db = db
        created_user = user_service.save(user)
        return {"data": created_user, "status_code": 201}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@route.put("/users/{id}", status_code=200, response_model=SingleUserResponse)
async def update_user(
    id: int, user: UserUpdateRequest, db: Session = Depends(get_session)
):
    """
    Update an existing user's information.

    Args:
        id (int): The unique identifier of the user to update.
        user (UserUpdateRequest): User update request.
        db (Session): SQLAlchemy database session.

    Returns:
        UserUpdateResponse: Updated user object.

    Raises:
        HTTPException: If the user is not found (status_code=404),
                       if there is a value error (status_code=400),
                       or if there is an internal server error (status_code=500).
    """
    try:
        user_service.db = db
        updated_user = user_service.update(id, user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"data": updated_user, "status_code": 200}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


@route.delete("/users/{id}", status_code=200, response_model=SingleUserResponse)
async def delete_user(id: int, db: Session = Depends(get_session)):
    """
    Delete a user by their unique identifier.

    Args:
        id (int): The unique identifier of the user to delete.
        db (Session): SQLAlchemy database session.

    Returns:
        dict: A dictionary containing the deleted user data and the status code.

    Raises:
        HTTPException: If the user is not found or if there is an internal server error.
    """
    try:
        user_service.db = db

        user = user_service.delete(id)

        if not user:
            raise HTTPException(status_code=500, detail="Failed to delete user")

        return {"data": user, "status_code": 200}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error {e}")
