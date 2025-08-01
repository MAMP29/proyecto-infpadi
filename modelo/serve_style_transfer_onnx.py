import ray
from ray import serve
from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io
import onnxruntime
import numpy as np


# Definición del Despliegue de Ray Serve
@serve.deployment(
    num_replicas=2,  # Copias de nuestro servicio
    #ray_actor_options={"num_gpus": 0.25} # Cada copia usa un pedazo de la GPU
)
class StyleTransferService:
    def __init__(self, style_model_path: str):

        # print(f"Cargando el modelo desde: {style_model_path}")
        # self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        # print(f"Usando dispositivo: {self.device}")

        # Carga el modelo .onnx una vez y lo guarda en memoria.
        self.session = onnxruntime.InferenceSession(style_model_path)
        self.input_name = self.session.get_inputs()[0].name
        
        print("Modelo cargado y listo.")

    def _preprocess(self, image_bytes: bytes) -> np.ndarray:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        array = np.array(image, dtype=np.float32)
        array = array.transpose((2, 0, 1))
        array = np.expand_dims(array, axis=0)
        return array

    def _postprocess(self, output_numpy: np.ndarray) -> bytes:
        img_array = output_numpy[0]
        # Limitar valores
        img_array = np.clip(img_array, 0, 255)
        img_array = img_array.transpose((1, 2, 0))
        img_array = img_array.astype(np.uint8)
        pil_img = Image.fromarray(img_array)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG")
        return buffer.getvalue()

    # --- El Endpoint de la API ---
    async def stylize(self, image_bytes: bytes):
        """Recibe una imagen, la estiliza y la devuelve."""
        
        # 1. Pre-procesar la imagen
        input_numpy = self._preprocess(image_bytes)
        
        # 2. Ejecutar la inferencia (usando la sesión ONNX que ya cargamos)
        ort_inputs = {self.input_name: input_numpy}
        ort_outs = self.session.run(None, ort_inputs)
        output_numpy = ort_outs[0]
        
        # 3. Post-procesar el resultado
        result_bytes = self._postprocess(output_numpy)
        
        # 4. Devolver la imagen estilizada
        return result_bytes



if __name__ == "__main__":
    # Conectarse al clúster de Ray que ya está corriendo
    # address="auto" le dice a Ray que busque el clúster existente.
    ray.init(address="auto", namespace="serve") 

    mosaic_model_path = "modelo/saved_models/candy.onnx"
    service_app = StyleTransferService.bind(style_model_path=mosaic_model_path)

    # Desplegar la app en el clúster
    serve.run(service_app)