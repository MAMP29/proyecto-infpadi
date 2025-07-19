# Proyecto Infraestructuras paralelas y distribuidas

Repositorio que encapsula el proyecto de InfPaDi, a continuación se hace un repaso por las diversas carpetas:

---
## Modelo

Modelo de inteligencia artificial usado, este modelo es un ejemplo tomado directamente del repositorio de ejemplos de [Pytorch](https://github.com/pytorch/examples/tree/main), se trata de un modelo Fast Style Transfer el cual permite aplicar determinados estilos (entrenados previamente) a una imagen en particular, en el fondo es una red de tipo CNN.

Es un ejemplo interesante para explorar el paralelismo y distribución de múltiples instancias para la inferencia del modelo con las imágenes empleando Ray.

En el siguiente [README](https://github.com/pytorch/examples/blob/main/fast_neural_style/README.md) del repositorio original puede encontrar las instrucciones de uso y funcionamiento por si esta interesado.

---

Para ejecutar el modelo directamente cree un entorno virtual de python e instale lo necesario en la carpeta de requerimentos. Acto seguído:

- Abra un clúster de Ray, allí se cargara el modelo (por ahora solo se ha probado con GPU)

```bash
ray start --head --num-gpus 1
```

- Ejecute el archivo principal

```bash
python main.py
```

- Mediante curl o cualquier elemento para peticiones https lance una petición para estilizar la imagen que desee, ejemplo:

```bash
curl -X POST \
     -F "image=@modelo/images/input-images/normal_girl.jpeg" \
     http://127.0.0.1:8000/stylize \
     --output ray_mosaic_girl.jpg
```