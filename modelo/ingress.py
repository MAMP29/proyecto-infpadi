from ray import serve
from fastapi import FastAPI, UploadFile, File
from starlette.requests import Request # Importa Request
from starlette.responses import Response, JSONResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",  # URL del cliente en local
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],  # Permite todas las cabeceras
)

@serve.deployment()
@serve.ingress(app)
class Ingress:
    def __init__(self, candy_handle, mosaic_handle, rain_handle, udnie_handle):
        # Pasa los "handles" de los workers de backend
        self.candy_handle = candy_handle
        self.mosaic_handle = mosaic_handle
        self.rain_handle = rain_handle
        self.udnie_handle = udnie_handle

    @app.post("/stylize/candy")
    async def stylize_candy(self, image: UploadFile = File(...)):
        image_bytes = await image.read()
        # Llama remotamente al método 'stylize' del worker de candy
        result_bytes = await self.candy_handle.stylize.remote(image_bytes)
        return Response(content=result_bytes, media_type="image/jpeg")
    
    @app.post("/stylize/mosaic")
    async def stylize_mosaic(self, image: UploadFile = File(...)):
        image_bytes = await image.read()
        result_bytes = await self.mosaic_handle.stylize.remote(image_bytes)
        return Response(content=result_bytes, media_type="image/jpeg")

    @app.post("/stylize/rain_princess")
    async def stylize_rain(self, image: UploadFile = File(...)):
        image_bytes = await image.read()
        result_bytes = await self.rain_handle.stylize.remote(image_bytes)
        return Response(content=result_bytes, media_type="image/jpeg")

    @app.post("/stylize/udnie")
    async def stylize_udnie(self, image: UploadFile = File(...)):
        image_bytes = await image.read()
        result_bytes = await self.udnie_handle.stylize.remote(image_bytes)
        return Response(content=result_bytes, media_type="image/jpeg")

        
    # Puedes añadir un endpoint raíz para verificar que el servicio está vivo
    @app.get("/")
    def root(self):
        return JSONResponse({"message": "Ejecutándose", "Estilos disponibles": ["candy", "mosaic", "rain_princess", "udnie"]})