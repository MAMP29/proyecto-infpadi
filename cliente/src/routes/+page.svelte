<script lang="ts">
  import { onMount } from 'svelte';
  import 'img-comparison-slider';

  // --- ESTADO DE LA APLICACIÓN ---
  let selectedFile: File | null = null;
  let originalImageURL: string | null = null;
  let stylizedImageURL: string | null = null;
  let selectedStyleId: string | null = null;
  let isLoading = false;
  let errorMessage: string | null = null;
  
  // Estado para el feedback de Drag and Drop
  let isDraggingOver = false;

  const API_URL = "http://127.0.0.1:8000";

  const styles = [
    { id: 'candy', name: 'Candy', thumbnail: '/thumbnails/candy.jpg' },
    { id: 'mosaic', name: 'Mosaic', thumbnail: '/thumbnails/mosaic.jpg' },
    { id: 'rain_princess', name: 'Rain Princess', thumbnail: '/thumbnails/rain_princess.jpg' },
    { id: 'udnie', name: 'Udnie', thumbnail: '/thumbnails/udnie.jpg' },
  ];

  // --- MANEJADORES DE EVENTOS ---

  // Función refactorizada para procesar un archivo
  function processFile(file: File) {
    // Validar tipo de archivo
    if (!file.type.startsWith('image/')) {
        errorMessage = "Por favor, sube un archivo de imagen (PNG, JPG, etc.).";
        return;
    }
    selectedFile = file;
    originalImageURL = URL.createObjectURL(selectedFile);
    stylizedImageURL = null; 
    errorMessage = null;
  }
  
  // Se activa desde el input de tipo "file"
  function handleFileSelect(event: Event) {
    const input = event.target as HTMLInputElement;
    if (input.files && input.files.length > 0) {
      processFile(input.files[0]);
    }
  }
  
  // MEJORA 2: Manejadores para Drag and Drop
  function handleDrop(event: DragEvent) {
    event.preventDefault();
    isDraggingOver = false;
    if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
        processFile(event.dataTransfer.files[0]);
    }
  }

  function selectStyle(styleId: string) {
    selectedStyleId = styleId;
  }

  // --- LÓGICA PRINCIPAL: LLAMADA A LA API ---

  async function stylizeImage() {
    if (!selectedFile || !selectedStyleId) {
      errorMessage = "Por favor, selecciona una imagen y un estilo.";
      return;
    }

    isLoading = true;
    errorMessage = null;
    stylizedImageURL = null;

    const formData = new FormData();
    formData.append('image', selectedFile);

    try {
      const response = await fetch(`${API_URL}/stylize/${selectedStyleId}`, {
        method: 'POST',
        body: formData,
        headers: {
            'Accept': 'image/jpeg'
        }
      });

      if (!response.ok) {
        throw new Error(`Error del servidor: ${response.status} ${response.statusText}`);
      }

      const imageBlob = await response.blob();
      stylizedImageURL = URL.createObjectURL(imageBlob);

    } catch (error) {
      console.error("Error al estilizar la imagen:", error);
      errorMessage = `No se pudo procesar la imagen. Verifica que el servicio de Ray esté corriendo. (${error})`;
    } finally {
      isLoading = false;
    }
  }
</script>

<div class="min-h-screen bg-gray-900 text-white flex flex-col items-center p-4 sm:p-8">
  
  <header class="text-center mb-8">
    <h1 class="text-4xl sm:text-5xl font-extrabold text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-pink-600">
      Estilizador de Imágenes Neuronal
    </h1>
    <p class="text-gray-400 mt-2">Creado con Ray Serve y SvelteKit</p>
  </header>

  <main class="w-full max-w-7xl grid grid-cols-1 lg:grid-cols-2 gap-8">

    <!-- === Panel de Controles (Izquierda) === -->
    <div class="bg-gray-800 p-6 rounded-2xl shadow-lg flex flex-col space-y-6">
      
      <!-- 1. Carga de Imagen con DRAG AND DROP -->
      <div>
        <h2 class="text-xl font-bold mb-3 border-l-4 border-purple-400 pl-3">1. Sube tu Imagen</h2>
        <div 
            class="mt-2 flex justify-center rounded-lg border border-dashed border-gray-500 px-6 py-10 transition-colors"
            class:bg-gray-700={isDraggingOver}
            class:border-pink-500={isDraggingOver}
            on:dragenter|preventDefault|stopPropagation={() => isDraggingOver = true}
            on:dragover|preventDefault|stopPropagation={() => isDraggingOver = true}
            on:dragleave|preventDefault|stopPropagation={() => isDraggingOver = false}
            on:drop|preventDefault|stopPropagation={handleDrop}
        >
          <div class="text-center">
            <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true"><path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" /></svg>
            <div class="mt-4 flex text-sm leading-6 text-gray-400">
              <label for="file-upload" class="relative cursor-pointer rounded-md font-semibold text-pink-500 hover:text-pink-400">
                <span>Selecciona un archivo</span>
                <input on:change={handleFileSelect} id="file-upload" name="file-upload" type="file" class="sr-only" accept="image/png, image/jpeg, image/webp">
              </label>
              <p class="pl-1">o arrástralo aquí</p>
            </div>
            <p class="text-xs leading-5 text-gray-500">PNG, JPG, WEBP hasta 10MB</p>
          </div>
        </div>
      </div>

      <!-- 2. Selección de Estilo con ACCESIBILIDAD MEJORADA -->
      <div>
        <h2 class="text-xl font-bold mb-4 border-l-4 border-purple-400 pl-3">2. Elige un Estilo</h2>
        <div class="grid grid-cols-2 sm:grid-cols-4 gap-4">
          {#each styles as style (style.id)}
            <button 
              type="button"
              on:click={() => selectStyle(style.id)}
              class="text-left p-2 rounded-lg border-2 transition-all"
              class:border-pink-500={selectedStyleId === style.id}
              class:bg-gray-700={selectedStyleId === style.id}
              class:border-transparent={selectedStyleId !== style.id}
            >
              <img src={style.thumbnail} alt={`Estilo ${style.name}`} class="w-full h-24 object-cover rounded-md pointer-events-none" />
              <span class="mt-2 block text-sm font-medium text-center text-white">{style.name}</span>
            </button>
          {/each}
        </div>
      </div>
      
      <!-- 3. Botón de Acción -->
      <div>
        <button on:click={stylizeImage} disabled={!selectedFile || !selectedStyleId || isLoading} class="w-full bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white font-bold py-3 px-4 rounded-lg shadow-lg transition-transform transform hover:scale-105 disabled:opacity-50 disabled:saturate-50 disabled:cursor-not-allowed">
          {#if isLoading}
            <span class="animate-pulse">Procesando...</span>
          {:else}
            ✨ ¡Estilizar!
          {/if}
        </button>
      </div>
    </div>

    <!-- === Panel de Resultado (Derecha) MEJORADO === -->
    <div class="bg-gray-800 p-6 rounded-2xl shadow-lg flex flex-col items-center justify-center min-h-[50vh] lg:min-h-full">
      <div class="w-full flex-grow flex flex-col items-center justify-center">
        {#if errorMessage}
          <div class="text-red-400 bg-red-900/50 p-4 rounded-lg"><p class="font-bold">¡Oops! Hubo un error</p><p class="text-sm mt-1">{errorMessage}</p></div>
        
        {:else if isLoading}
           <div class="flex items-center justify-center text-lg">
              <svg class="animate-spin h-6 w-6 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
              <p class="ml-3">Aplicando estilo...</p>
           </div>

        {:else if originalImageURL && stylizedImageURL}
          <img-comparison-slider class="w-full h-auto max-h-[70vh] rounded-lg outline-none focus:ring-2 focus:ring-pink-500">
            <img slot="first" src={originalImageURL} class="w-full h-full object-contain" />
            <img slot="second" src={stylizedImageURL} class="w-full h-full object-contain" />
          </img-comparison-slider>
          
        {:else if originalImageURL}
          <img src={originalImageURL} alt="Imagen original" class="max-h-[70vh] rounded-lg shadow-md" />
          <p class="mt-4 text-gray-300">Ahora, selecciona un estilo y presiona "¡Estilizar!".</p>
        
        {:else}
          <p class="text-gray-500">Sube una imagen para comenzar</p>
        {/if}
      </div>
      
      <!-- Botón de descarga condicional -->
      {#if stylizedImageURL && !isLoading}
        <div class="w-full pt-4 mt-4 border-t border-gray-700">
            <a 
                href={stylizedImageURL} 
                download="imagen_estilizada.jpg" 
                class="w-full block text-center bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg transition-colors"
            >
                ↓ Descargar Imagen Estilizada
            </a>
        </div>
      {/if}
    </div>
  </main>
</div>