from fastapi import APIRouter, status
from fastapi.responses import JSONResponse

from db import DBQuery, emails_details_table, users_table
from models import EmailDetail, User
from utils import check_password, generate_access_token, password_hasher

auth_router = APIRouter()


@auth_router.post("/login")
def login(login_data: User):
    if login_data:
        # check if user exists
        user = users_table.search(DBQuery.username == login_data.username)

        if user:
            user = user[0]

            password_correct = check_password(login_data.password, user["password"])

            if password_correct:
                payload = {
                    "id": user["id"],
                    "username": user["username"],
                }

                # create access token
                access_token = generate_access_token(payload)

                response = {
                    "login": True,
                    "access_token": access_token,
                    "message": "Login successful",
                }

                return JSONResponse(response, status_code=status.HTTP_200_OK)

        else:
            response = {
                "login": False,
                "message": "User does not exist",
            }

            return JSONResponse(response, status_code=status.HTTP_404_NOT_FOUND)

    else:

        response = {
            "login": False,
            "message": "Invalid login credentials",
        }

        return JSONResponse(response, status_code=status.HTTP_401_UNAUTHORIZED)


# create account
@auth_router.post("/sign-up")
def signup(sign_up_data: User):
    if sign_up_data:
        # check if user exists
        user = users_table.search(DBQuery.username == sign_up_data.username)

        if user:
            response = {
                "created": False,
                "message": "User already exists",
            }

            return JSONResponse(response, status_code=status.HTTP_409_CONFLICT)

        else:

            # hash the password
            sign_up_data.password = password_hasher(sign_up_data.password)

            users_table.insert(sign_up_data.model_dump())

            response = {
                "created": True,
                "message": "User created successfully",
            }

            return JSONResponse(response, status_code=status.HTTP_201_CREATED)


# delete the user
@auth_router.delete("/{user_id}")
def delete_user(user_id: str):
    users_table.remove(DBQuery.id == user_id)

    response = {
        "deleted": True,
    }

    return JSONResponse(response, status_code=status.HTTP_200_OK)


@auth_router.get("")
def get_users():
    users = users_table.all()

    response = {
        "users": users,
    }

    return JSONResponse(response, status_code=status.HTTP_200_OK)


@auth_router.post("/emails")
def create_email_details(email_data: EmailDetail):

    if email_data:
        # insert the emails for configuration
        emails_details_table.insert(email_data.model_dump())

        return JSONResponse(
            {
                "message": "Emails added successfully",
                "created": True,
            },
            status_code=status.HTTP_201_CREATED,
        )

    else:
        return JSONResponse(
            {
                "message": "Invalid email data",
                "created": False,
            },
            status_code=status.HTTP_400_BAD_REQUEST,
        )


@auth_router.get("/emails")
def get_email_details():
    email_details = emails_details_table.all()

    return JSONResponse(
        {
            "emails": email_details,
        },
        status_code=status.HTTP_200_OK,
    )
