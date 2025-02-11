from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from config import conf
from fast_routers import shop_product_router, shop_category_router, main_photos_router, work_router, bot_user_router, \
    admin_user_router, order_router, cart_router, jwt_router, shop_router
from models import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mount("/media", StaticFiles(directory='media'), name='media')
    app.include_router(bot_user_router)
    app.include_router(admin_user_router)
    app.include_router(shop_router)
    app.include_router(work_router)
    app.include_router(shop_category_router)
    app.include_router(shop_product_router)
    # app.include_router(generate_router)
    app.include_router(main_photos_router)
    app.include_router(cart_router)
    app.include_router(order_router)
    app.include_router(jwt_router)
    await db.create_all()
    yield


app = FastAPI(docs_url="/docs", lifespan=lifespan)
app.add_middleware(SessionMiddleware, secret_key=conf.SECRET_KEY)
app.add_middleware(
    CORSMiddleware,
    # allow_origins=["http://localhost:8000", "https://arava1.vercel.app"],
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# minio_handler = MinioHandler(
#     os.getenv('MINIO_URL'),
#     os.getenv('MINIO_ACCESS_KEY'),
#     os.getenv('MINIO_SECRET_KEY'),
#     os.getenv('MINIO_BUCKET'),
#     False
# )


# @app.get("/media/{full_path:path}", name='media')
# async def get_media(full_path):
#     image_path = Path(f'media/{full_path}')
#     if not image_path.is_file():
#         return Response("Image not found on the server", status.HTTP_404_NOT_FOUND)
#     return FileResponse(image_path)
#
#
# @app.exception_handler(status.HTTP_401_UNAUTHORIZED)
# def auth_exception_handler(request: Request, exc):
#     return RedirectResponse(request.url_for('login_page'))
#

# @app.get("/banner", name="Banner photos")
# async def list_photo_banner():
#     #     # list_ = []
#     #     # image_path = os.listdir('media/banner')
#     #     # if not image_path:
#     #     #     return Response("Image not found on the server", status.HTTP_404_NOT_FOUND)
#     #     # for i in image_path:
#     #     #     file_path = 'media/banners/' + i
#     #     #     if i.endswith('png'):
#     #     #         type = 'png'
#     #     #     else:
#     #     #         type = 'jpeg'
#     #     #     list_.append(FileResponse(file_path, media_type=f"image/{type}", filename=i))
#     #     # return {"banner": list_}
#     #     file_path = os.path.join("media/banner", "Pasted_image.png")
#     #     if not os.path.exists(file_path):
#     #         return {"error": "File not found"}
#     #     return FileResponse(file_path, media_type="image/jpeg")
#     banner_dir = 'media/banners'
#
#     if not os.path.exists(banner_dir):
#         raise HTTPException(status_code=404, detail="Banner directory not found")
#
#     image_files = [f for f in os.listdir(banner_dir) if
#                    os.path.isfile(os.path.join(banner_dir, f)) and f.endswith(('.png', '.jpeg', '.jpg'))]
#
#     if not image_files:
#         raise HTTPException(status_code=404, detail="No images found in the banner directory")
#
#     banner_urls = [{"filename": f, "url": f"/media/banners/{f}"} for f in image_files]
#
#     return JSONResponse(content={"banners": banner_urls}, status_code=200)

# @app.get(path='/photo-all/', name="Get Shop Photos all")
# async def list_category_shop():
#     return {'shop-photos': await ShopPhoto.all()}
