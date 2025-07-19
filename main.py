import ray
from ray import serve
from modelo.serve_style_transfer import service_app

# Se conectara a un cluster de ray creado de forma manual
# ray start --head --num-gpus 1
# ray status para ver el estado
ray.init(address="auto", namespace="serve") 
    
# Desplegar la app en el clúster
serve.run(service_app)