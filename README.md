# Proyecto: Infraestructuras Paralelas y Distribuidas

Este repositorio contiene el desarrollo del proyecto para el curso de Infraestructuras Paralelas y Distribuidas (InfPaDi). El objetivo principal fue distribuir y paralelizar la inferencia de un modelo de estilo neuronal utilizando [Ray](https://www.ray.io/), comparando ejecuciones en GPU (Torch) y CPU (ONNX), e integrando tecnologías como Nix Flakes para la portabilidad del entorno.

---

## 📁 Estructura del Repositorio

* `modelo/`: Modelo de inteligencia artificial y servidor de inferencia.
* `cliente/`: Aplicación web para probar el modelo desde el navegador.

---

## 🧠 Modelo

Se utiliza un modelo de *Fast Style Transfer* basado en CNNs, tomado del repositorio oficial de [PyTorch Examples](https://github.com/pytorch/examples/tree/main/fast_neural_style). Este permite aplicar diferentes estilos artísticos preentrenados sobre imágenes de entrada.

Este proyecto adapta dicho modelo para su uso en entornos distribuidos, ejecutando múltiples instancias del mismo en paralelo mediante Ray.

👉 Consulta la [documentación original](https://github.com/pytorch/examples/blob/main/fast_neural_style/README.md) para más detalles sobre su arquitectura y entrenamiento.

---

### 🔧 Ejecución del modelo

1. Crea un entorno virtual en Python e instala los requerimientos según la carpeta `modelo/`. Hay dos opciones:

   * `requirements.txt`: entorno completo.
   * `requirements_min.txt`: entorno mínimo para inferencia.

2. Inicia un clúster local de Ray:

```bash
ray start --head
```

3. Ejecuta el servidor con ONNX:

```bash
python main.py --gpus 0 --force --backend onnx
```

4. Realiza una petición POST a la API:

```bash
curl -X POST \
     -F "image=@modelo/images/input-images/normal_girl.jpeg" \
     http://127.0.0.1:8000/stylize/mosaic \
     --output ray_mosaic_girl.jpg
```

---

## 🌐 Cliente

El cliente es una aplicación web que permite probar visualmente el sistema de estilización mediante una interfaz interactiva (desarrollado en Svelte).

Para ejecutarlo:

```bash
cd cliente
npm install
npm run dev
```

---

## ❄️ Nix Flakes

Para garantizar reproducibilidad y portabilidad, se incluyen flake.nix que encapsulan todas las dependencias necesarias:

* **Flake en raíz**: configuración para ejecutar el sistema en CPU (ONNX).
* **Flake en `modelo/`**: incluye PyTorch y CUDA, necesario para ejecución con GPU.

Uso:

```bash
nix develop
```

Esto abrirá un entorno de desarrollo aislado. Luego, puedes ejecutar el modelo o el cliente como se indicó arriba.

