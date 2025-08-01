import ray
from ray import serve
from fastapi import FastAPI, UploadFile, File
from PIL import Image
import io
import re
import torch
import onnxruntime
import numpy as np

from torchvision import transforms
from neural_style.transformer_net import TransformerNet

# Definición del Despliegue de Ray Serve
@serve.deployment(
    num_replicas=1,
    ray_actor_options={"num_gpus": 0.25} 
)
class StyleTransferService:
    def __init__(self, style_model_path: str):
        print(f"Cargando modelo PyTorch (.pth) desde: {style_model_path}")
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Usando dispositivo: {self.device}")

        # 1. Instancia el modelo (vacío por ahora)
        self.model = TransformerNet()

        # 2. Carga el state_dict del archivo
        state_dict = torch.load(style_model_path, map_location='cpu', weights_only=False)

        # 3. Aplica el parche de compatibilidad
        for k in list(state_dict.keys()):
            if re.search(r'in\d+\.running_(mean|var)$', k):
                print(f"Eliminando clave obsoleta: {k}")
                del state_dict[k]

        # 4. Carga el state_dict limpio en el modelo
        self.model.load_state_dict(state_dict)

        # 5. Mueve el modelo completo a la GPU
        self.model.to(self.device)
        
        # 6. Pon el modelo en modo de evaluación
        self.model.eval()

        print("Modelo PyTorch cargado en GPU y listo.")

    def _preprocess(self, image_bytes: bytes) -> torch.Tensor:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        transform_pipeline = transforms.Compose([
            transforms.ToTensor(),
            transforms.Lambda(lambda x: x.mul(255))
        ])
        # Devuelve un tensor de PyTorch directamente
        return transform_pipeline(image).unsqueeze(0).to(self.device)


    def _postprocess(self, output_tensor: torch.Tensor) -> bytes:
        # La entrada ya es un tensor de PyTorch en la GPU
        img_tensor = output_tensor.squeeze(0).cpu() # Mover a CPU para procesar
        img_tensor = img_tensor.clamp(0, 255)
        
        # Convertir a NumPy para guardar con PIL
        img_numpy = img_tensor.permute(1, 2, 0).numpy().astype("uint8")
        
        pil_img = Image.fromarray(img_numpy)
        buffer = io.BytesIO()
        pil_img.save(buffer, format="JPEG")
        return buffer.getvalue()

    async def stylize(self, image_bytes: bytes) -> bytes:
        # Desactivar el cálculo de gradientes para máxima velocidad
        with torch.no_grad():
            # 1. Pre-procesar a un Tensor de PyTorch en la GPU
            input_tensor = self._preprocess(image_bytes)
            
            # 2. Ejecutar la inferencia con el modelo de PyTorch
            output_tensor = self.model(input_tensor)
            
            # 3. Post-procesar el resultado
            result_bytes = self._postprocess(output_tensor)
            
            return result_bytes



if __name__ == "__main__":
    # Conectarse al clúster de Ray que ya está corriendo
    # address="auto" le dice a Ray que busque el clúster existente.
    ray.init(address="auto", namespace="serve") 

    mosaic_model_path = "modelo/saved_models/candy.onnx"
    service_app = StyleTransferService.bind(style_model_path=mosaic_model_path)

    # Desplegar la app en el clúster
    serve.run(service_app)
