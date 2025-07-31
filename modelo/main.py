import subprocess
import sys
import argparse
import os

def check_gpu_available():
    try:
        import torch
        return torch.cuda.device_count()
    except ImportError:
        try:
            result = subprocess.run(["nvidia-smi", "-L"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                return len(result.stdout.strip().split('\n'))
        except FileNotFoundError:
            pass
    return 0

def stop_ray_cluster():
    print("Deteniendo clúster Ray si está en ejecución...")
    subprocess.run(["ray", "stop"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def start_ray_cluster(num_gpus, force_restart=False):
    if force_restart:
        stop_ray_cluster()
    else:
        # Verificar si Ray ya está corriendo
        try:
            import ray
            ray.init(address="auto")
            ray.shutdown()
            print("Ray ya está corriendo. No se reinicia.")
            return
        except Exception:
            pass

    cmd = ["ray", "start", "--head"]
    if num_gpus > 0:
        cmd.append(f"--num-gpus={num_gpus}")

    print(f"Iniciando clúster Ray con {num_gpus} GPU(s)...")
    subprocess.run(cmd, check=True)

def get_absolute_model_path(relative_path):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, relative_path)

def main():
    parser = argparse.ArgumentParser(description="Desplegar aplicación Style Transfer sobre Ray Serve.")
    parser.add_argument("--gpus", type=int, default=0, help="Número de GPUs a usar (puede ser 0)")
    parser.add_argument("--restart", action="store_true", help="Reiniciar el clúster Ray si ya está en ejecución")
    parser.add_argument("--stop", action="store_true", help="Detener el clúster Ray y salir sin desplegar")
    parser.add_argument("--force", action="store_true", help="Forzar el uso del número de GPUs indicado (sin verificar)")
    args = parser.parse_args()

    if args.stop:
        stop_ray_cluster()
        print("Clúster detenido. No se ha desplegado la aplicación.")
        sys.exit(0)

    if not args.force:
        available_gpus = check_gpu_available()
        if args.gpus > available_gpus:
            print(f"Solo hay {available_gpus} GPU(s) disponibles. Se usará ese valor.")
            num_gpus = available_gpus
        else:
            num_gpus = args.gpus
    else:
        print("Modo forzado activado. No se verifica la disponibilidad de GPUs.")
        num_gpus = args.gpus

    start_ray_cluster(num_gpus, force_restart=args.restart)

    # ---------------- Aplicación principal ----------------
    import ray
    from ray import serve
    from serve_style_transfer import StyleTransferService
    from ingress import Ingress

    ray.init(address="auto", namespace="serve")

    # Ruta absoluta a los modelos
    candy_model = get_absolute_model_path("saved_models/candy.onnx")
    mosaic_model = get_absolute_model_path("saved_models/mosaic.onnx")
    rain_model = get_absolute_model_path("saved_models/rain_princess.onnx")
    udnie_model = get_absolute_model_path("saved_models/udnie.onnx")

    candy_app = StyleTransferService.bind(style_model_path=candy_model)
    mosaic_app = StyleTransferService.bind(style_model_path=mosaic_model)
    rain_app = StyleTransferService.bind(style_model_path=rain_model)
    udnie_app = StyleTransferService.bind(style_model_path=udnie_model)

    api_router = Ingress.bind(
        candy_handle=candy_app,
        mosaic_handle=mosaic_app,
        rain_handle=rain_app,
        udnie_handle=udnie_app,
    )

    serve.run(target=api_router, route_prefix="/")
    print("Aplicación desplegada con éxito.")

if __name__ == "__main__":
    main()
