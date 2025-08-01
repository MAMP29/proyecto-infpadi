#!/usr/bin/env bash

# start-demo.sh
# Script para iniciar el entorno de demostración completo de la aplicación de transferencia de estilo.
# Este script asume que se está ejecutando desde una shell de Nix activada con el flake.nix de este proyecto.

# Salir inmediatamente si un comando falla
set -e

echo "--- Iniciando el Entorno de Demostración ---"

# --- Paso 1: Preparar el Frontend ---
echo ""
echo "-> Paso 1: Configurando el frontend de Svelte..."

# Navegar al directorio del frontend
cd frontend

# Instalar las dependencias de Node.js.
# 'npm i' es un alias para 'npm install'.
echo "Instalando dependencias de npm (puede tardar un momento)..."
npm i

echo "Frontend configurado."
cd .. # Volver a la raíz del proyecto

# --- Paso 2: Iniciar el Backend de Ray ---
echo ""
echo "-> Paso 2: Iniciando el backend de Ray Serve en segundo plano..."

# Darle un momento a Ray para que se inicie completamente
sleep 5

# Desplegar la aplicación de Ray Serve
# Se ejecuta en segundo plano usando '&' para no bloquear la terminal.
python modelo/main.py --gpus 0 --force --backend onnx &

# Guardar el PID (Process ID) del proceso de Ray para poder detenerlo después
RAY_APP_PID=$!

echo "Backend de Ray iniciado con PID: $RAY_APP_PID"

# --- Paso 3: Iniciar el Servidor de Desarrollo del Frontend ---
echo ""
echo "-> Paso 3: Iniciando el servidor de desarrollo del frontend (Vite)..."

# Navegar al directorio del frontend de nuevo
cd frontend

# Iniciar el servidor de Vite, que se conectará al backend a través del proxy.
# Este será el proceso principal que mantendrá el script corriendo.
npm run dev

# --- Paso 4: Limpieza (se ejecuta cuando detienes el script con Ctrl+C) ---
echo ""
echo "--- Deteniendo la Demostración ---"

# Función de limpieza que se llamará al salir
cleanup() {
    echo "-> Deteniendo el proceso de la aplicación de Ray (PID: $RAY_APP_PID)..."
    kill $RAY_APP_PID
    sleep 2
    echo "-> Deteniendo el clúster de Ray..."
    ray stop
    echo "Limpieza completada. ¡Adiós!"
}

# 'trap' es un comando de shell que ejecuta 'cleanup' cuando recibe la señal de interrupción (Ctrl+C)
trap cleanup EXIT