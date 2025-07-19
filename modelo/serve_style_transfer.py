import ray
from ray import serve
from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io
import torch
import onnxruntime
import numpy as np

from torchvision import transforms

# Definición de la Aplicación FastAPI (para manejar las peticiones HTTP)
app = FastAPI()

# Definición del Despliegue de Ray Serve
@serve.deployment(
    num_replicas=2,  # 2 copias de nuestro servicio
    ray_actor_options={"num_gpus": 0.5} # Cada copia usa media GPU
)
@serve.ingress(app) # Conecta este despliegue con nuestra app FastAPI
class StyleTransferService:
    def __init__(self, style_model_path: str):

        print(f"Cargando el modelo desde: {style_model_path}")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Usando dispositivo: {self.device}")
        
        # Carga el modelo .onnx una vez y lo guarda en memoria.
        self.session = onnxruntime.InferenceSession(style_model_path)
        self.input_name = self.session.get_inputs()[0].name
        
        print("Modelo cargado y listo.")

    # Pre-procesamiento de la imagen de entrada
    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        
        content_transform = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.mul(255))
        ])
        tensor = content_transform(image).unsqueeze(0)
        return tensor.cpu().numpy()

    # Post-procesamiento del resultado
    def _postprocess(self, output_tensor: np.ndarray) -> bytes:

        img = torch.from_numpy(output_tensor[0]).clone().clamp(0, 255).numpy()
        img = img.transpose(1, 2, 0).astype("uint8")
        pil_img = Image.fromarray(img)
        
        # Guardar en un buffer de memoria en lugar de un archivo
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG")
        return buffer.getvalue()

    # --- El Endpoint de nuestra API ---
    @app.post("/stylize")
    async def stylize(self, image: UploadFile = File(...)):
        """Recibe una imagen, la estiliza y la devuelve."""
        image_bytes = await image.read()
        
        # 1. Pre-procesar la imagen
        input_numpy = self._preprocess(image_bytes)
        
        # 2. Ejecutar la inferencia (usando la sesión ONNX que ya cargamos)
        ort_inputs = {self.input_name: input_numpy}
        ort_outs = self.session.run(None, ort_inputs)
        output_numpy = ort_outs[0]
        
        # 3. Post-procesar el resultado
        result_bytes = self._postprocess(output_numpy)
        
        # 4. Devolver la imagen estilizada
        from starlette.responses import Response
        return Response(content=result_bytes, media_type="image/jpeg")


mosaic_model_path = "modelo/saved_models/candy.onnx"
service_app = StyleTransferService.bind(style_model_path=mosaic_model_path)

# candy_model_path = "saved_models/candy.onnx"
# app_van_gogh = StyleTransferService.bind(style_model_path=candy_model_path)

if __name__ == "__main__":
    # Conectarse al clúster de Ray que ya está corriendo
    # address="auto" le dice a Ray que busque el clúster existente.
    ray.init(address="auto", namespace="serve") 
    
    # Desplegar la app en el clúster
    serve.run(service_app)
