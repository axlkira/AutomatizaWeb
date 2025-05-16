<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-900 dark:to-gray-800">
    <nav class="bg-white shadow-sm dark:bg-gray-800">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between h-16">
          <div class="flex">
            <div class="flex-shrink-0 flex items-center">
              <img class="h-8 w-auto" src="./assets/logo.svg" alt="AutomatizaWeb">
              <span class="ml-2 text-xl font-semibold text-gray-800 dark:text-white">AutomatizaWeb</span>
            </div>
          </div>
          <div class="flex items-center">
            <button class="p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white">
              <i class="fas fa-bell"></i>
            </button>
            <button class="ml-4 p-2 rounded-md text-gray-500 hover:text-gray-700 dark:text-gray-300 dark:hover:text-white">
              <i class="fas fa-user-circle text-xl"></i>
            </button>
          </div>
        </div>
      </div>
    </nav>

    <div class="py-6">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex flex-wrap">
          <!-- Sidebar -->
          <div class="w-full md:w-1/5 pr-4">
            <div class="bg-white rounded-lg shadow-sm p-4 dark:bg-gray-800">
              <ul class="space-y-2">
                <li>
                  <a href="#" class="flex items-center p-2 text-gray-700 rounded-md hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-700">
                    <i class="fas fa-tachometer-alt w-6"></i>
                    <span>Dashboard</span>
                  </a>
                </li>
                <li>
                  <a href="#" class="flex items-center p-2 text-gray-700 rounded-md hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-700">
                    <i class="fas fa-file-alt w-6"></i>
                    <span>Artículos</span>
                  </a>
                </li>
                <li>
                  <a href="#" class="flex items-center p-2 text-gray-700 rounded-md hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-700">
                    <i class="fas fa-spider w-6"></i>
                    <span>Scraping</span>
                  </a>
                </li>
                <li>
                  <a href="#" class="flex items-center p-2 text-gray-700 rounded-md hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-700">
                    <i class="fas fa-tags w-6"></i>
                    <span>Categorías</span>
                  </a>
                </li>
                <li>
                  <a href="#" class="flex items-center p-2 text-gray-700 rounded-md hover:bg-blue-50 dark:text-gray-200 dark:hover:bg-gray-700">
                    <i class="fas fa-cog w-6"></i>
                    <span>Configuración</span>
                  </a>
                </li>
              </ul>
            </div>
          </div>

          <!-- Main Content -->
          <div class="w-full md:w-4/5 mt-4 md:mt-0">
            <div class="bg-white rounded-lg shadow-sm p-6 dark:bg-gray-800">
              <h1 class="text-2xl font-semibold text-gray-800 dark:text-white">Dashboard</h1>
              
              <!-- Stats Cards -->
              <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mt-6">
                <div class="bg-gradient-to-r from-purple-500 to-purple-600 rounded-lg p-4 text-white shadow-md">
                  <div class="flex justify-between">
                    <div>
                      <p class="text-sm text-purple-100">Artículos Generados</p>
                      <p class="text-3xl font-bold">{{ stats.articulos_generados }}</p>
                    </div>
                    <div class="text-purple-200">
                      <i class="fas fa-newspaper text-3xl"></i>
                    </div>
                  </div>
                </div>
                <div class="bg-gradient-to-r from-blue-500 to-blue-600 rounded-lg p-4 text-white shadow-md">
                  <div class="flex justify-between">
                    <div>
                      <p class="text-sm text-blue-100">URLs Procesadas</p>
                      <p class="text-3xl font-bold">{{ stats.urls_procesadas }}</p>
                    </div>
                    <div class="text-blue-200">
                      <i class="fas fa-link text-3xl"></i>
                    </div>
                  </div>
                </div>
                <div class="bg-gradient-to-r from-green-500 to-green-600 rounded-lg p-4 text-white shadow-md">
                  <div class="flex justify-between">
                    <div>
                      <p class="text-sm text-green-100">Categorías</p>
                      <p class="text-3xl font-bold">{{ stats.categorias }}</p>
                    </div>
                    <div class="text-green-200">
                      <i class="fas fa-tags text-3xl"></i>
                    </div>
                  </div>
                </div>
                <div class="bg-gradient-to-r from-red-500 to-red-600 rounded-lg p-4 text-white shadow-md">
                  <div class="flex justify-between">
                    <div>
                      <p class="text-sm text-red-100">Pendientes</p>
                      <p class="text-3xl font-bold">{{ stats.pendientes }}</p>
                    </div>
                    <div class="text-red-200">
                      <i class="fas fa-tasks text-3xl"></i>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Actions Section -->
              <div class="mt-8">
                <h2 class="text-xl font-semibold text-gray-800 dark:text-white">Acciones Rápidas</h2>
                <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                  <button @click="ejecutarScript('ejecutar_todo.py')" class="flex items-center justify-center p-4 bg-blue-50 hover:bg-blue-100 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg text-blue-600 dark:text-blue-300">
                    <i class="fas fa-play mr-2"></i>
                    <span>Ejecutar Todo</span>
                  </button>
                  <button @click="ejecutarScript('_2.Escrapear.py')" class="flex items-center justify-center p-4 bg-green-50 hover:bg-green-100 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg text-green-600 dark:text-green-300">
                    <i class="fas fa-spider mr-2"></i>
                    <span>Scraping</span>
                  </button>
                  <button @click="ejecutarScript('_4.Redactar.py')" class="flex items-center justify-center p-4 bg-purple-50 hover:bg-purple-100 dark:bg-gray-700 dark:hover:bg-gray-600 rounded-lg text-purple-600 dark:text-purple-300">
                    <i class="fas fa-file-alt mr-2"></i>
                    <span>Redactar</span>
                  </button>
                </div>
              </div>
              
              <!-- Recent Articles -->
              <div class="mt-8">
                <h2 class="text-xl font-semibold text-gray-800 dark:text-white">Artículos Recientes</h2>
                <div class="mt-4 overflow-x-auto">
                  <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
                    <thead class="bg-gray-50 dark:bg-gray-700">
                      <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Keyword</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Título</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Categoría</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">Acciones</th>
                      </tr>
                    </thead>
                    <tbody class="bg-white divide-y divide-gray-200 dark:bg-gray-800 dark:divide-gray-700">
                      <tr v-for="(articulo, index) in articulos" :key="index">
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{{ articulo.keyword }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{{ articulo.titulo }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{{ articulo.categoria }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">
                          <button class="text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-300 mr-2">
                            <i class="fas fa-edit"></i>
                          </button>
                          <button class="text-red-600 hover:text-red-800 dark:text-red-400 dark:hover:text-red-300">
                            <i class="fas fa-trash"></i>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';

export default {
  name: 'App',
  data() {
    return {
      stats: {
        articulos_generados: 0,
        urls_procesadas: 0,
        categorias: 0,
        pendientes: 0
      },
      articulos: [],
      ejecutando: false
    }
  },
  mounted() {
    this.cargarDatos();
  },
  methods: {
    async cargarDatos() {
      try {
        const statsResponse = await axios.get('http://localhost:5000/api/stats');
        this.stats = statsResponse.data;
        
        const articulosResponse = await axios.get('http://localhost:5000/api/articulos');
        this.articulos = articulosResponse.data;
      } catch (error) {
        console.error('Error al cargar datos:', error);
      }
    },
    async ejecutarScript(script) {
      if (this.ejecutando) return;
      
      this.ejecutando = true;
      try {
        await axios.post('http://localhost:5000/api/ejecutar', { script });
        await this.cargarDatos();
        alert(`Script ${script} ejecutado con éxito`);
      } catch (error) {
        console.error('Error al ejecutar script:', error);
        alert(`Error al ejecutar ${script}`);
      } finally {
        this.ejecutando = false;
      }
    }
  }
}
</script>

<style>
body {
  font-family: 'Poppins', sans-serif;
}
</style>
