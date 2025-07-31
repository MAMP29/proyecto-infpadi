# Stage 1: Construir la aplicación Svelte
FROM node:22-alpine AS builder

# Establece el directorio de trabajo dentro del contenedor.
WORKDIR /app

# Copia los archivos de configuración de paquetes (package.json y package-lock.json/yarn.lock)
COPY package*.json ./

# Instala las dependencias del proyecto.
RUN npm install

# Copia el resto del código de la aplicación al directorio de trabajo.
COPY . .

# Ejecuta el comando de construcción de Vite para Svelte.
# Esto creará la carpeta 'dist' con los archivos estáticos de tu aplicación.
RUN npm run build

# Stage 2: Servir la aplicación con Nginx
# Usamos una imagen ligera de Nginx para servir los archivos estáticos.
FROM nginx:alpine

# Elimina la configuración predeterminada de Nginx.
RUN rm /etc/nginx/conf.d/default.conf

# Copia tu archivo de configuración de Nginx personalizado.
# Este archivo definirá cómo Nginx servirá tu aplicación y en qué puerto.
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copia los archivos de la aplicación construida (desde la etapa 'builder')
# al directorio de Nginx donde se sirven los archivos estáticos.
COPY --from=builder /app/build /usr/share/nginx/html

# Expone el puerto 80
# Este es el puerto en el que Nginx escuchará las conexiones.
EXPOSE 80

# Comando para iniciar Nginx en primer plano cuando se inicie el contenedor.
CMD ["nginx", "-g", "daemon off;"]
