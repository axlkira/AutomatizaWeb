// Variables globales
let resultadoModal;
let isLoading = false;

// Función para cambiar entre modo claro y oscuro
function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  const isDarkMode = document.body.classList.contains('dark-mode');
  localStorage.setItem('darkMode', isDarkMode ? 'enabled' : 'disabled');
  
  // Cambiar el ícono del botón
  const icon = document.getElementById('dark-mode-icon');
  if (isDarkMode) {
    icon.classList.remove('fa-moon');
    icon.classList.add('fa-sun');
  } else {
    icon.classList.remove('fa-sun');
    icon.classList.add('fa-moon');
  }
}

// Función para cargar los datos del dashboard
async function cargarDashboard() {
  try {
    // Cargar estadísticas
    const statsResponse = await fetch('/api/stats');
    if (!statsResponse.ok) throw new Error('Error al cargar estadísticas');
    const stats = await statsResponse.json();
    
    // Actualizar contadores de estadísticas
    document.getElementById('articulos-generados').textContent = stats.articulos_generados;
    document.getElementById('urls-procesadas').textContent = stats.urls_procesadas;
    document.getElementById('categorias').textContent = stats.categorias;
    document.getElementById('pendientes').textContent = stats.pendientes;
    
    // Cargar artículos recientes
    const articulosResponse = await fetch('/api/articulos');
    if (!articulosResponse.ok) throw new Error('Error al cargar artículos');
    const articulos = await articulosResponse.json();
    
    // Ocultar spinner de carga
    document.getElementById('loading-articulos').style.display = 'none';
    
    // Mostrar tabla si hay artículos
    const tablaArticulos = document.getElementById('tabla-articulos');
    const articulosBody = document.getElementById('articulos-body');
    const noArticulos = document.getElementById('no-articulos');
    
    // Limpiar tabla anterior
    articulosBody.innerHTML = '';
    
    if (articulos.length === 0) {
      // Mostrar mensaje si no hay artículos
      tablaArticulos.style.display = 'none';
      noArticulos.style.display = 'block';
    } else {
      // Mostrar tabla y ocultar mensaje
      tablaArticulos.style.display = 'table';
      noArticulos.style.display = 'none';
      
      // Rellenar tabla con artículos
      articulos.forEach(articulo => {
        const fila = document.createElement('tr');
        fila.innerHTML = `
          <td>${articulo.keyword || 'Sin palabra clave'}</td>
          <td>${articulo.titulo || 'Sin título'}</td>
          <td>${articulo.categoria || 'Sin categoría'}</td>
          <td>
            <a href="/api/descargar-redactados" class="btn btn-sm btn-success me-1" title="Descargar">
              <i class="fas fa-download"></i>
            </a>
            <button class="btn btn-sm btn-primary me-1" title="Ver" onclick="verArticulo('${articulo.id}')">
              <i class="fas fa-eye"></i>
            </button>
          </td>
        `;
        articulosBody.appendChild(fila);
      });
    }
    
    // Actualizar visibilidad del botón de descarga según si hay artículos
    const btnDescargarRedactados = document.getElementById('btn-descargar-redactados');
    if (btnDescargarRedactados) {
      btnDescargarRedactados.style.display = stats.articulos_generados > 0 ? 'inline-block' : 'none';
    }
    
  } catch (error) {
    console.error('Error en la carga de datos:', error);
    document.getElementById('loading-articulos').style.display = 'none';
    document.getElementById('no-articulos').style.display = 'block';
    document.getElementById('tabla-articulos').style.display = 'none';
  }
}

// Función para ver detalles de un artículo
function verArticulo(id) {
  alert('Funcionalidad de visualización de artículo en desarrollo');
  console.log('Ver artículo con ID:', id);
}

// Variable para el intervalo de progreso
let progresoInterval = null;

// Función para actualizar el progreso del proceso Redactar
async function actualizarProgresoRedactar() {
  try {
    const response = await fetch(`/api/progreso/_4.Redactar.py`);
    if (!response.ok) throw new Error('Error al obtener progreso');
    const data = await response.json();
    
    const progressBar = document.getElementById('redactar-progress-bar');
    const progressText = document.getElementById('redactar-progress-text');
    
    if (progressBar && progressText) {
      progressBar.style.width = `${data.progreso}%`;
      progressBar.setAttribute('aria-valuenow', data.progreso);
      progressText.textContent = `Progreso: ${data.progreso}%`;
      
      // Si llega al 100%, detener el intervalo
      if (data.progreso >= 100) {
        progressText.textContent = 'Completado 100%';
        clearInterval(progresoInterval);
        progresoInterval = null;
        // Recargar datos después de completar
        setTimeout(() => {
          cargarDashboard();
          document.getElementById('redactar-progress-container').style.display = 'none';
          document.getElementById('redactar-progress-text').style.display = 'none';
        }, 2000);
      }
    }
  } catch (error) {
    console.error('Error al actualizar progreso:', error);
  }
}

// Función para ejecutar scripts
async function ejecutarScript(script) {
  if (isLoading) return;
  
  isLoading = true;
  try {
    // Si es el script de redactar, mostrar la barra de progreso
    if (script === '_4.Redactar.py') {
      document.getElementById('redactar-progress-container').style.display = 'block';
      document.getElementById('redactar-progress-text').style.display = 'block';
      document.getElementById('redactar-progress-bar').style.width = '0%';
      document.getElementById('redactar-progress-text').textContent = 'Iniciando proceso...';
      
      // Iniciar intervalo para actualizar el progreso
      if (progresoInterval) clearInterval(progresoInterval);
      progresoInterval = setInterval(actualizarProgresoRedactar, 1000); // Actualizar cada segundo
    }
    
    // Mostrar modal con mensaje de carga
    resultadoModal.show();
    document.getElementById('resultado-contenido').textContent = 'Ejecutando script, por favor espere...';
    
    console.log('Ejecutando script:', script);
    // Llamar a la API para ejecutar el script con timeout más largo
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 180000); // 3 minutos de timeout
    
    const response = await fetch('/api/ejecutar', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ script }),
      signal: controller.signal
    });
    
    clearTimeout(timeoutId);
    const data = await response.json();
    
    // Mostrar resultado en el modal
    if (data.success) {
      document.getElementById('resultado-contenido').textContent = 
        `✅ Script ejecutado exitosamente\n\nSalida:\n${data.output}\n\nErrores:\n${data.error || 'Ninguno'}`;
    } else {
      document.getElementById('resultado-contenido').textContent = 
        `❌ Error al ejecutar el script\n\nDetalles:\n${data.error || 'Error desconocido'}`;
      
      // Detener la barra de progreso si hay error
      if (script === '_4.Redactar.py' && progresoInterval) {
        clearInterval(progresoInterval);
        progresoInterval = null;
        document.getElementById('redactar-progress-container').style.display = 'none';
        document.getElementById('redactar-progress-text').style.display = 'none';
      }
    }
    
    // Recargar los datos del dashboard
    await cargarDashboard();
    
  } catch (error) {
    console.error('Error al ejecutar script:', error);
    document.getElementById('resultado-contenido').textContent = 
      `❌ Error al comunicarse con el servidor\n\nDetalles:\n${error.message}`;
      
    // Detener la barra de progreso si hay error
    if (script === '_4.Redactar.py' && progresoInterval) {
      clearInterval(progresoInterval);
      progresoInterval = null;
      document.getElementById('redactar-progress-container').style.display = 'none';
      document.getElementById('redactar-progress-text').style.display = 'none';
    }
  } finally {
    isLoading = false;
  }
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
  // Inicializar modal
  resultadoModal = new bootstrap.Modal(document.getElementById('resultadoModal'));
  
  // Cargar datos iniciales
  cargarDashboard();
  
  // Inicializar modo oscuro si estaba activado
  if (localStorage.getItem('darkMode') === 'enabled') {
    document.body.classList.add('dark-mode');
    const icon = document.getElementById('dark-mode-icon');
    if (icon) {
      icon.classList.remove('fa-moon');
      icon.classList.add('fa-sun');
    }
  }
  
  // Configurar botón de modo oscuro
  const darkModeButton = document.getElementById('dark-mode-toggle');
  if (darkModeButton) {
    darkModeButton.addEventListener('click', toggleDarkMode);
  }
  
  // Configurar botones para cada paso del proceso
  // Paso 1: Fusionar
  const btnFusionar = document.getElementById('btn-fusionar');
  if (btnFusionar) {
    btnFusionar.addEventListener('click', function() {
      console.log('Ejecutando Paso 1: Fusionar');
      ejecutarScript('_0.Fusionar.py');
    });
  }
  
  // Paso 2: Agrupar
  const btnAgrupar = document.getElementById('btn-agrupar');
  if (btnAgrupar) {
    btnAgrupar.addEventListener('click', function() {
      console.log('Ejecutando Paso 2: Agrupar');
      ejecutarScript('_1.Agrupar.py');
    });
  }
  
  // Paso 3: Escrapear
  const btnScraping = document.getElementById('btn-scraping');
  if (btnScraping) {
    btnScraping.addEventListener('click', function() {
      console.log('Ejecutando Paso 3: Escrapear');
      ejecutarScript('_2.Escrapear.py');
    });
  }
  
  // Paso 4: Categorizar
  const btnCategorizar = document.getElementById('btn-categorizar');
  if (btnCategorizar) {
    btnCategorizar.addEventListener('click', function() {
      console.log('Ejecutando Paso 4: Categorizar');
      ejecutarScript('_3.Categorizar.py');
    });
  }
  
  // Paso 5: Redactar
  const btnRedactar = document.getElementById('btn-redactar');
  if (btnRedactar) {
    btnRedactar.addEventListener('click', function() {
      console.log('Ejecutando Paso 5: Redactar');
      ejecutarScript('_4.Redactar.py');
    });
  }
  
  // Botón para ejecutar todos los pasos
  const btnEjecutarTodo = document.getElementById('btn-ejecutar-todo');
  if (btnEjecutarTodo) {
    btnEjecutarTodo.addEventListener('click', async function() {
      if (confirm('Esta acción ejecutará todos los pasos en secuencia. Puede tomar varios minutos. ¿Desea continuar?')) {
        console.log('Ejecutando secuencia completa...');
        alert('Iniciando proceso completo. Por favor, sea paciente.');
        // Implementación futura para ejecutar todos los scripts en secuencia
      }
    });
  }
});
