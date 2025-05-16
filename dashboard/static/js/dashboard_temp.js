// Variables globales
let resultadoModal;
let isLoading = false;
let totalArticulos = [];    // Para almacenar todos los artículos
let currentPage = 1;        // Página actual
let articlesPerPage = 5;    // Artículos por página - Limitado a 5

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
    totalArticulos = await articulosResponse.json();
    
    // Ocultar spinner de carga
    document.getElementById('loading-articulos').style.display = 'none';
    
    // Mostrar tabla si hay artículos
    const tablaArticulos = document.getElementById('tabla-articulos');
    const noArticulos = document.getElementById('no-articulos');
    const paginacion = document.getElementById('articulos-paginacion');
    
    if (totalArticulos.length === 0) {
      // Mostrar mensaje si no hay artículos
      tablaArticulos.style.display = 'none';
      noArticulos.style.display = 'block';
      paginacion.style.display = 'none';
    } else {
      // Mostrar tabla y ocultar mensaje
      tablaArticulos.style.display = 'table';
      noArticulos.style.display = 'none';
      
      // Mostrar artículos con paginación
      mostrarArticulosPaginados(currentPage);
      
      // Actualizar controles de paginación
      actualizarPaginacion();
      paginacion.style.display = 'flex';
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
    document.getElementById('articulos-paginacion').style.display = 'none';
  }
}

// Función para mostrar artículos paginados
function mostrarArticulosPaginados(page) {
  const articulosBody = document.getElementById('articulos-body');
  
  // Limpiar tabla anterior
  articulosBody.innerHTML = '';
  
  // Calcular índices de la página actual
  const startIndex = (page - 1) * articlesPerPage;
  const endIndex = Math.min(startIndex + articlesPerPage, totalArticulos.length);
  
  // Obtener artículos para la página actual
  const articulosPagina = totalArticulos.slice(startIndex, endIndex);
  
  // Agregar artículos a la tabla
  articulosPagina.forEach(articulo => {
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

// Función para actualizar controles de paginación
function actualizarPaginacion() {
  const paginacion = document.getElementById('articulos-paginacion');
  const ul = paginacion.querySelector('ul.pagination');
  
  // Limpiar paginación anterior
  ul.innerHTML = '';
  
  // Calcular total de páginas
  const totalPages = Math.ceil(totalArticulos.length / articlesPerPage);
  
  // Botón "Anterior"
  const prevLi = document.createElement('li');
  prevLi.className = `page-item ${currentPage === 1 ? 'disabled' : ''}`;
  prevLi.innerHTML = `<a class="page-link" href="#" tabindex="-1">Anterior</a>`;
  prevLi.addEventListener('click', (e) => {
    e.preventDefault();
    if (currentPage > 1) {
      cambiarPagina(currentPage - 1);
    }
  });
  ul.appendChild(prevLi);
  
  // Botones de páginas numeradas
  for (let i = 1; i <= totalPages; i++) {
    const pageLi = document.createElement('li');
    pageLi.className = `page-item ${i === currentPage ? 'active' : ''}`;
    pageLi.innerHTML = `<a class="page-link" href="#">${i}</a>`;
    pageLi.addEventListener('click', (e) => {
      e.preventDefault();
      cambiarPagina(i);
    });
    ul.appendChild(pageLi);
  }
  
  // Botón "Siguiente"
  const nextLi = document.createElement('li');
  nextLi.className = `page-item ${currentPage === totalPages ? 'disabled' : ''}`;
  nextLi.innerHTML = `<a class="page-link" href="#">Siguiente</a>`;
  nextLi.addEventListener('click', (e) => {
    e.preventDefault();
    if (currentPage < totalPages) {
      cambiarPagina(currentPage + 1);
    }
  });
  ul.appendChild(nextLi);
}

// Función para cambiar de página
function cambiarPagina(page) {
  currentPage = page;
  mostrarArticulosPaginados(page);
  actualizarPaginacion();
}

// Función para ver detalles de un artículo
async function verArticulo(id) {
  try {
    // Mostrar indicador de carga
    const articuloModal = new bootstrap.Modal(document.getElementById('articuloModal'));
    document.getElementById('articulo-cuerpo').innerHTML = '<div class="text-center p-5"><div class="spinner-border text-primary" role="status"></div><p class="mt-3">Cargando artículo...</p></div>';
    document.getElementById('articulo-titulo').innerText = 'Cargando...';
    articuloModal.show();
    
    // Obtener datos del artículo
    const response = await fetch(`/api/articulo/${id}`);
    if (!response.ok) throw new Error('Error al cargar el artículo');
    const articulo = await response.json();
    
    // Actualizar modal con datos del artículo
    document.getElementById('articulo-titulo').innerText = articulo.titulo;
    
    // Crear contenido estructurado del artículo
    let contenidoHTML = `
      <div class="article-container">
        <div class="article-meta mb-4">
          <div class="badge bg-primary me-2">${articulo.categoria}</div>
          <small class="text-muted">Keyword: ${articulo.keyword}</small>
        </div>
        
        <div class="article-description mb-4">
          <p class="lead">${articulo.descripcion}</p>
        </div>
        
        <div class="article-content">
          ${articulo.articulo}
        </div>
        
        <div class="article-footer mt-4 pt-3 border-top">
          <div class="row">
            <div class="col-md-6">
              <small class="text-muted">URL amigable: ${articulo.slug}</small>
            </div>
            <div class="col-md-6 text-end">
              <a href="#" class="btn btn-sm btn-outline-primary" onclick="copiarAlPortapapeles('${encodeURIComponent(articulo.articulo)}'); return false;">
                <i class="fas fa-copy me-1"></i> Copiar HTML
              </a>
            </div>
          </div>
        </div>
      </div>
    `;
    
    document.getElementById('articulo-cuerpo').innerHTML = contenidoHTML;
  } catch (error) {
    console.error('Error al cargar artículo:', error);
    document.getElementById('articulo-cuerpo').innerHTML = `
      <div class="alert alert-danger">
        <i class="fas fa-exclamation-triangle me-2"></i>
        Error al cargar el artículo: ${error.message}
      </div>
    `;
  }
}

// Función para copiar el contenido HTML al portapapeles
function copiarAlPortapapeles(texto) {
  const textoDecode = decodeURIComponent(texto);
  navigator.clipboard.writeText(textoDecode)
    .then(() => {
      // Mostrar notificación de éxito
      const alertaDiv = document.createElement('div');
      alertaDiv.className = 'alert alert-success position-fixed bottom-0 end-0 m-3';
      alertaDiv.innerHTML = '<i class="fas fa-check-circle me-2"></i> HTML copiado al portapapeles';
      document.body.appendChild(alertaDiv);
      
      // Eliminar la notificación después de 3 segundos
      setTimeout(() => {
        alertaDiv.remove();
      }, 3000);
    })
    .catch(err => {
      console.error('Error al copiar:', err);
    });
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

  // Inicializar el uploader de CSV
  initCSVUploader();
  
  // Cargar datos iniciales
  cargarDashboard();
  
  // Configurar manejo de navegación
  window.addEventListener('hashchange', manejarNavegacion);
  manejarNavegacion(); // Manejar navegación inicial
  
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
  
  // Configurar botones de acciones
  document.getElementById('btn-fusionar').addEventListener('click', () => ejecutarScript('_0.Fusionar.py'));
  document.getElementById('btn-descanivalizar').addEventListener('click', () => ejecutarScript('_01.Descanivalizador.py'));
  document.getElementById('btn-agrupar').addEventListener('click', () => ejecutarScript('_1.Agrupar.py'));
  document.getElementById('btn-scraping').addEventListener('click', () => ejecutarScript('_2.Escrapear.py'));
  document.getElementById('btn-categorizar').addEventListener('click', () => ejecutarScript('_3.Categorizar.py'));
  document.getElementById('btn-redactar').addEventListener('click', () => ejecutarScript('_4.Redactar.py'));
});
