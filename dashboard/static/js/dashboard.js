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
// Función para cargar la configuración de IA
async function cargarConfiguracionIA() {
  try {
    document.getElementById('loading-config').style.display = 'block';
    document.getElementById('config-error').style.display = 'none';
    document.getElementById('config-content').style.display = 'none';
    
    const response = await fetch('/api/config/ai');
    if (!response.ok) throw new Error('Error al cargar la configuración');
    const config = await response.json();
    
    // Establecer el proveedor seleccionado
    document.getElementById('provider-select').value = config.provider;
    
    // Mostrar la configuración del proveedor seleccionado
    mostrarConfiguracionProveedor(config.provider, config.models[config.provider]);
    
    document.getElementById('loading-config').style.display = 'none';
    document.getElementById('config-content').style.display = 'block';
  } catch (error) {
    console.error('Error al cargar configuración:', error);
    document.getElementById('loading-config').style.display = 'none';
    document.getElementById('config-error').style.display = 'block';
    document.getElementById('config-error-message').textContent = error.message;
  }
}

// Función para mostrar la configuración específica del proveedor seleccionado
function mostrarConfiguracionProveedor(provider, config) {
  const configContainer = document.getElementById('provider-config');
  
  // Limpiar contenedor
  configContainer.innerHTML = '';
  
  // Crear campos de configuración según el proveedor
  const fieldConfigs = {
    'base_url': {
      label: 'URL Base',
      type: 'text',
      placeholder: 'Ejemplo: http://localhost:11434/v1'
    },
    'model': {
      label: 'Modelo',
      type: 'text',
      placeholder: 'Ejemplo: qwen3:8b'
    },
    'api_key': {
      label: 'API Key',
      type: 'password',
      placeholder: 'Introduce tu API key'
    }
  };
  
  // Crear campos para el proveedor actual
  for (const [key, fieldConfig] of Object.entries(fieldConfigs)) {
    const formGroup = document.createElement('div');
    formGroup.className = 'mb-3';
    
    const label = document.createElement('label');
    label.className = 'form-label';
    label.setAttribute('for', `config-${provider}-${key}`);
    label.textContent = fieldConfig.label;
    
    const input = document.createElement('input');
    input.type = fieldConfig.type;
    input.className = 'form-control';
    input.id = `config-${provider}-${key}`;
    input.name = key;
    input.placeholder = fieldConfig.placeholder;
    input.value = config[key] || '';
    
    // Ayuda contextual según el proveedor
    let helpText = '';
    if (key === 'base_url') {
      if (provider === 'ollama') {
        helpText = 'URL del servidor Ollama, por defecto: http://localhost:11434/v1';
      } else if (provider === 'openai') {
        helpText = 'URL de la API de OpenAI, por defecto: https://api.openai.com/v1';
      } else if (provider === 'deepseek') {
        helpText = 'URL de la API de DeepSeek, por defecto: https://api.deepseek.com/v1';
      }
    } else if (key === 'model') {
      if (provider === 'ollama') {
        helpText = 'Modelo de Ollama, ejemplos: qwen3:8b, llama3, etc.';
      } else if (provider === 'openai') {
        helpText = 'Modelo de OpenAI, ejemplos: gpt-3.5-turbo, gpt-4, etc.';
      } else if (provider === 'deepseek') {
        helpText = 'Modelo de DeepSeek, ejemplos: deepseek-chat, etc.';
      }
    } else if (key === 'api_key') {
      if (provider === 'ollama') {
        helpText = 'Normalmente no se requiere para Ollama local.';
      } else {
        helpText = `Introduce tu API key para ${provider.charAt(0).toUpperCase() + provider.slice(1)}.`;
      }
    }
    
    // Agregar texto de ayuda si existe
    if (helpText) {
      const helpElement = document.createElement('div');
      helpElement.className = 'form-text';
      helpElement.textContent = helpText;
      formGroup.appendChild(label);
      formGroup.appendChild(input);
      formGroup.appendChild(helpElement);
    } else {
      formGroup.appendChild(label);
      formGroup.appendChild(input);
    }
    
    configContainer.appendChild(formGroup);
  }
  
  // Añadir botón de guardar
  const saveBtn = document.createElement('button');
  saveBtn.type = 'button';
  saveBtn.className = 'btn btn-primary mt-3';
  saveBtn.innerHTML = '<i class="fas fa-save me-2"></i>Guardar Configuración';
  saveBtn.onclick = guardarConfiguracionIA;
  configContainer.appendChild(saveBtn);
}

// Función para guardar la configuración de IA
async function guardarConfiguracionIA() {
  try {
    const provider = document.getElementById('provider-select').value;
    const config = {
      provider: provider,
      config: {
        base_url: document.getElementById(`config-${provider}-base_url`).value,
        model: document.getElementById(`config-${provider}-model`).value,
        api_key: document.getElementById(`config-${provider}-api_key`).value
      }
    };
    
    // Mostrar indicador de carga
    const saveBtn = document.querySelector('#provider-config button');
    const originalButtonText = saveBtn.innerHTML;
    saveBtn.disabled = true;
    saveBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>Guardando...';
    
    // Enviar configuración al servidor
    const response = await fetch('/api/config/ai', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(config)
    });
    
    const data = await response.json();
    
    // Restaurar botón
    saveBtn.disabled = false;
    saveBtn.innerHTML = originalButtonText;
    
    if (response.ok) {
      // Mostrar notificación de éxito
      const alertaDiv = document.createElement('div');
      alertaDiv.className = 'alert alert-success position-fixed bottom-0 end-0 m-3';
      alertaDiv.innerHTML = '<i class="fas fa-check-circle me-2"></i> Configuración guardada correctamente';
      document.body.appendChild(alertaDiv);
      
      // Eliminar la notificación después de 3 segundos
      setTimeout(() => {
        alertaDiv.remove();
      }, 3000);
      
      // Recargar configuración
      cargarConfiguracionIA();
    } else {
      throw new Error(data.error || 'Error al guardar la configuración');
    }
  } catch (error) {
    console.error('Error al guardar configuración:', error);
    
    // Mostrar notificación de error
    const alertaDiv = document.createElement('div');
    alertaDiv.className = 'alert alert-danger position-fixed bottom-0 end-0 m-3';
    alertaDiv.innerHTML = `<i class="fas fa-exclamation-triangle me-2"></i> Error: ${error.message}`;
    document.body.appendChild(alertaDiv);
    
    // Eliminar la notificación después de 5 segundos
    setTimeout(() => {
      alertaDiv.remove();
    }, 5000);
  }
}

// Función para manejar la navegación
function manejarNavegacion() {
  // Obtener la ubicación actual
  const hash = window.location.hash || '#dashboard';
  
  // Ocultar todas las secciones
  document.querySelectorAll('.card').forEach(section => {
    section.style.display = 'none';
  });
  
  // Quitar clase activa de todos los enlaces
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.remove('active');
  });
  
  // Mostrar la sección correspondiente y activar enlace
  if (hash === '#configuracion') {
    // Mostrar sección de configuración
    document.getElementById('configuracion-section').style.display = 'block';
    document.getElementById('nav-config').classList.add('active');
    // Cargar configuración de IA
    cargarConfiguracionIA();
  } else if (hash === '#articulos') {
    // Mostrar solo la sección de artículos
    document.querySelector('.card:nth-of-type(2)').style.display = 'block';
    document.getElementById('nav-articulos').classList.add('active');
  } else {
    // Dashboard: mostrar todas las secciones excepto configuración
    document.querySelectorAll('.card:not(#configuracion-section)').forEach(section => {
      section.style.display = 'block';
    });
    document.getElementById('nav-dashboard').classList.add('active');
  }
}

// Funcionalidad para la subida de archivos CSV
function initCSVUploader() {
  const dropArea = document.getElementById('drop-area');
  const fileInput = document.getElementById('file-input');
  const selectBtn = document.getElementById('select-files-btn');
  const uploadBtn = document.getElementById('upload-files-btn');
  const fileList = document.getElementById('file-list');
  const uploadList = document.getElementById('upload-list');
  const uploadFeedback = document.getElementById('upload-feedback');
  const uploadMessage = document.getElementById('upload-message');
  
  let files = [];
  
  // Prevenir el comportamiento por defecto del navegador
  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, e => {
      e.preventDefault();
      e.stopPropagation();
    }, false);
  });
  
  // Efectos visuales durante el drag
  ['dragenter', 'dragover'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => {
      dropArea.classList.add('highlight');
    }, false);
  });
  
  ['dragleave', 'drop'].forEach(eventName => {
    dropArea.addEventListener(eventName, () => {
      dropArea.classList.remove('highlight');
    }, false);
  });
  
  // Manejar archivos soltados
  dropArea.addEventListener('drop', e => {
    const droppedFiles = e.dataTransfer.files;
    handleFiles(droppedFiles);
  }, false);
  
  // Manejar selección de archivos vía input
  fileInput.addEventListener('change', e => {
    handleFiles(e.target.files);
  });
  
  // Botón para seleccionar archivos
  selectBtn.addEventListener('click', () => {
    fileInput.click();
  });
  
  // Botón para subir archivos
  uploadBtn.addEventListener('click', () => {
    uploadFiles();
  });
  
  // Manejar archivos seleccionados o soltados
  function handleFiles(newFiles) {
    // Filtrar solo archivos CSV
    const csvFiles = Array.from(newFiles).filter(file => 
      file.name.toLowerCase().endsWith('.csv')
    );
    
    if (csvFiles.length === 0) {
      showMessage('Por favor, selecciona archivos CSV válidos.', 'warning');
      return;
    }
    
    // Añadir a la lista de archivos
    files = [...files, ...csvFiles];
    updateFileList();
  }
  
  // Actualizar la lista visual de archivos
  function updateFileList() {
    fileList.innerHTML = '';
    
    if (files.length > 0) {
      uploadList.style.display = 'block';
      
      files.forEach((file, index) => {
        const li = document.createElement('li');
        li.className = 'list-group-item d-flex justify-content-between align-items-center';
        li.innerHTML = `
          <span>
            <i class="fas fa-file-csv me-2 text-primary"></i>
            ${file.name} <small class="text-muted">(${formatFileSize(file.size)})</small>
          </span>
          <button class="btn btn-sm btn-outline-danger" data-index="${index}">
            <i class="fas fa-times"></i>
          </button>
        `;
        
        // Botón para eliminar el archivo
        const removeBtn = li.querySelector('button');
        removeBtn.addEventListener('click', () => {
          files.splice(index, 1);
          updateFileList();
        });
        
        fileList.appendChild(li);
      });
    } else {
      uploadList.style.display = 'none';
    }
  }
  
  // Formatear tamaño del archivo
  function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }
  
  // Subir archivos al servidor
  function uploadFiles() {
    if (files.length === 0) {
      showMessage('No hay archivos para subir.', 'warning');
      return;
    }
    
    // Mostrar estado de carga
    showMessage('Subiendo archivos...', 'info');
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    
    fetch('/api/upload-csv', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        showMessage(`${data.message} Se subieron ${files.length} archivos.`, 'success');
        files = [];
        updateFileList();
      } else {
        showMessage(`Error: ${data.message}`, 'danger');
      }
    })
    .catch(error => {
      console.error('Error:', error);
      showMessage('Error durante la subida de archivos. Inténtalo de nuevo.', 'danger');
    });
  }
  
  // Mostrar mensaje de feedback
  function showMessage(message, type) {
    uploadFeedback.style.display = 'block';
    uploadMessage.className = `alert alert-${type}`;
    uploadMessage.innerHTML = message;
    
    // Si es un mensaje de éxito, ocultarlo después de 5 segundos
    if (type === 'success') {
      setTimeout(() => {
        uploadFeedback.style.display = 'none';
      }, 5000);
    }
  }
}

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
  
  // Manejar cambios en el selector de proveedor de IA
  const providerSelect = document.getElementById('provider-select');
  if (providerSelect) {
    providerSelect.addEventListener('change', function() {
      // Obtener la configuración actual y mostrar los campos del proveedor seleccionado
      fetch('/api/config/ai')
        .then(response => response.json())
        .then(config => {
          mostrarConfiguracionProveedor(providerSelect.value, config.models[providerSelect.value]);
        })
        .catch(error => {
          console.error('Error al cambiar proveedor:', error);
        });
    });
  }
  
  // Configurar navegación
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      // Si es el enlace de configuración, cargar la configuración de IA
      if (this.id === 'nav-config') {
        setTimeout(() => {
          if (document.getElementById('configuracion-section').style.display === 'block') {
            cargarConfiguracionIA();
          }
        }, 100);
      }
    });
  });
  
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
