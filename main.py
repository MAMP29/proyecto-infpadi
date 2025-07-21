import ray
from ray import serve
from modelo.serve_style_transfer import StyleTransferService
from modelo.ingress import Ingress  # Usa la clase corregida

# Iniciar o conectar al clúster de Ray
ray.init(address="auto", namespace="serve") 
    
# 1. Construir las aplicaciones de backend (workers)
candy_app = StyleTransferService.bind(style_model_path="modelo/saved_models/candy.onnx")
mosaic_app = StyleTransferService.bind(style_model_path="modelo/saved_models/mosaic.onnx")
rain_app = StyleTransferService.bind(style_model_path="modelo/saved_models/rain_princess.onnx")
udnie_app = StyleTransferService.bind(style_model_path="modelo/saved_models/udnie.onnx")

# 2. Construir la aplicación de frontend
api_router = Ingress.bind(
    candy_handle=candy_app, 
    mosaic_handle=mosaic_app,
    rain_handle=rain_app,
    udnie_handle=udnie_app,
)

# 3. Desplegar
serve.run(target=api_router, route_prefix="/")