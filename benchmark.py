import requests
import time
import threading
import statistics
import numpy as np

# --- Configuración ---
API_URL = "http://127.0.0.1:8000/stylize/candy"
IMAGE_PATH = "modelo/images/input-images/pericles-test.jpeg"
NUM_REQUESTS = 120  # Total de peticiones a enviar
CONCURRENCY = 10   # Cuántos "usuarios" simultáneos

# --- Variables para guardar resultados ---
latencies = []
errors = 0

def make_request():
    global errors
    try:
        with open(IMAGE_PATH, "rb") as image_file:
            files = {"image": (IMAGE_PATH, image_file, "image/jpeg")}
            
            start_time = time.time()
            response = requests.post(API_URL, files=files)
            end_time = time.time()

            if response.status_code == 200:
                latencies.append(end_time - start_time)
            else:
                errors += 1
    except Exception as e:
        errors += 1
        print(f"Error en la petición: {e}")

# --- Motor del Benchmark ---
print(f"Iniciando benchmark con {NUM_REQUESTS} peticiones y concurrencia de {CONCURRENCY}...")

threads = []
start_benchmark_time = time.time()

for i in range(NUM_REQUESTS):
    thread = threading.Thread(target=make_request)
    threads.append(thread)
    thread.start()
    
    # Limita la concurrencia
    if len(threading.enumerate()) > CONCURRENCY:
        # Espera a que algunos hilos terminen antes de lanzar más
        for t in threads:
            t.join(timeout=0.1)

# Espera a que todos los hilos terminen
for thread in threads:
    thread.join()

end_benchmark_time = time.time()
total_time = end_benchmark_time - start_benchmark_time
qps = NUM_REQUESTS / total_time

# --- Impresión de Resultados ---
print("\n--- Resultados del Benchmark ---")
print(f"Tiempo total: {total_time:.2f} segundos")
print(f"Peticiones completadas: {len(latencies)}")
print(f"Errores: {errors}")
print(f"Rendimiento (QPS): {qps:.2f} peticiones/segundo")
print("\n--- Estadísticas de Latencia ---")
if latencies:
    print(f"Latencia promedio: {statistics.mean(latencies):.4f} s")
    print(f"Latencia mediana (p50): {statistics.median(latencies):.4f} s")
    print(f"Latencia p95: {np.percentile(latencies, 95):.4f} s")
    print(f"Latencia p99: {np.percentile(latencies, 99):.4f} s")
