from fastapi import APIRouter, UploadFile, File, Form
from fastapi import Response
from sqlalchemy.exc import DBAPIError
from starlette import status

from models import MainPhoto, AdminPanelUser

main_photos_router = APIRouter(prefix='/banners', tags=['Banners'])


@main_photos_router.get(path='', name="All banner photos")
async def list_category_shop():
    photos = await MainPhoto.all()
    return {'photos': photos}


@main_photos_router.post(path='', name="Create")
async def list_category_shop(operator_id: int, language: str, photo: UploadFile = File(default=None),
                             video: UploadFile = File(default=None)):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)

    if user:
        if user.status in ['moderator', "admin", "superuser"]:
            try:
                await MainPhoto.create(photo=photo, language=language, video=video)
                return {"ok": True}
            except DBAPIError as e:
                return Response("Yaratishda xatolik", status.HTTP_404_NOT_FOUND)

        else:
            return Response("Bu userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
    else:
        return Response("User yo'q", status.HTTP_404_NOT_FOUND)


# @main_photos_router.patch(path='/update', name="Update Banner photo")
# async def list_category_shop(operator_id: int, photo: UploadFile = File(), photo_id: int = Form()):
#     user = await AdminPanelUser.get(operator_id)
#     if not photo.content_type.startswith("image/"):
#         return Response("fayl rasim bo'lishi kerak", status.HTTP_404_NOT_FOUND)
#     if user:
#         if user.status.value in ['moderator', "admin", "superuser"]:
#             if await MainPhoto.get(photo_id):
#                 await MainPhoto.update(photo_id, photos=photo)
#                 return {"ok": True}
#             else:
#                 return Response("Bunday idli rasim yo'q", status.HTTP_404_NOT_FOUND)
#         else:
#             return Response("Bu userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
#     else:
#         return Response("User yo'q", status.HTTP_404_NOT_FOUND)


@main_photos_router.delete(path='/', name="Delete Banner photo")
async def list_category_shop(operator_id: int, photo_id: int = Form()):
    user: AdminPanelUser = await AdminPanelUser.get(operator_id)
    if user:
        if user.status in ['moderator', "admin", "superuser"]:
            if await MainPhoto.get(photo_id):
                await MainPhoto.delete(photo_id)
                return {"ok": True}
            else:
                return Response("Bunday idli rasim yo'q", status.HTTP_404_NOT_FOUND)
        else:
            return Response("Bu userda xuquq yo'q", status.HTTP_404_NOT_FOUND)
    else:
        return Response("User yo'q", status.HTTP_404_NOT_FOUND)
