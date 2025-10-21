/**
 * ApareText - Electron Main Process (Simplified)
 * Paleta de comandos funcional sin módulos complejos
 */

const { app, BrowserWindow, ipcMain, globalShortcut, Tray, Menu, clipboard, nativeImage, dialog } = require('electron');
const path = require('path');
const axios = require('axios');
const fs = require('fs').promises;
const { spawn } = require('child_process');
const { PythonShell } = require('python-shell');

// Configuración
const API_HOST = '127.0.0.1';
const API_PORT = 46321;
const API_URL = `http://${API_HOST}:${API_PORT}`;

// Helper function to call Python backend
function callPythonBackend(func, args = []) {
    return new Promise((resolve, reject) => {
        const options = {
            mode: 'text',
            pythonPath: 'python', // or 'python3' depending on system
            scriptPath: __dirname,
            args: [func, ...args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : arg)]
        };

        PythonShell.run('python_backend.py', options, (err, results) => {
            if (err) {
                reject(err);
            } else {
                try {
                    const result = JSON.parse(results[0]);
                    resolve(result);
                } catch (e) {
                    reject(e);
                }
            }
        });
    });
}

// Constantes de UI
const WINDOW_SIZES = {
    MAIN: { width: 1200, height: 800 },
    PALETTE: { width: 600, height: 550 },
    LOADING: { width: 650, height: 450 }
};
let mainWindow = null;
let paletteWindow = null;
let loadingWindow = null;
let tray = null;
let isEnabled = true;
let backendProcess = null;

/**
 * Backend is now integrated, no need to start server
 */
function startBackendServer() {
    console.log('[ApareText] Backend integrated - no server to start');
    return true;
}/**
 * Detener el backend server
 */
function stopBackendServer() {
    // No backend process to stop
}

/**
 * Crear el icono de la aplicación (verde brillante - máxima visibilidad)
 */
function createAppIcon() {
    const { nativeImage } = require('electron');
    
    // Crear un bitmap simple de 16x16 en memoria con color verde neón brillante
    // Usamos createFromBitmap que es más confiable en Windows
    const size = 16;
    const buffer = Buffer.alloc(size * size * 4); // RGBA
    
    // Llenar todo de verde neón brillante (R=0, G=255, B=0, A=255)
    for (let i = 0; i < buffer.length; i += 4) {
        buffer[i] = 0;       // R
        buffer[i + 1] = 255; // G (verde brillante)
        buffer[i + 2] = 0;   // B
        buffer[i + 3] = 255; // A
    }
    
    const icon = nativeImage.createFromBuffer(buffer, {
        width: size,
        height: size
    });
    
    return icon;
}

/**
 * Crear ventana de paleta de comandos
 */
function createPaletteWindow() {
    paletteWindow = new BrowserWindow({
        width: WINDOW_SIZES.PALETTE.width,
        height: 550, // Aumentado más para mostrar TODO el contenido completo
        show: false,
        frame: false,
        transparent: true,
        resizable: false,
        skipTaskbar: true,
        alwaysOnTop: true,
        icon: createAppIcon(),
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            devTools: true // Habilitar DevTools para debug
        }
    });

    paletteWindow.loadFile('palette.html');

    // NO cerrar la ventana al perder foco, solo ocultarla
    paletteWindow.on('blur', () => {
        if (paletteWindow && !paletteWindow.isDestroyed()) {
            paletteWindow.hide();
        }
    });

    // Prevenir que se cierre
    paletteWindow.on('close', (event) => {
        if (!app.isQuitting) {
            event.preventDefault();
            paletteWindow.hide();
        }
    });
}

/**
 * Crear ventana principal (configuración)
 */
function createMainWindow() {
    mainWindow = new BrowserWindow({
        width: WINDOW_SIZES.MAIN.width,
        height: WINDOW_SIZES.MAIN.height,
        minWidth: 800,
        minHeight: 600,
        show: true, // Mostrar inmediatamente
        resizable: true, // Explícitamente redimensionable
        transparent: false, // Desactivar transparencia para mejor visibilidad
        backgroundColor: '#ffffff',
        frame: true,
        icon: createAppIcon(),
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false,
            devTools: true // Habilitar DevTools
        }
    });

    mainWindow.loadFile('manager.html');

    mainWindow.webContents.on('did-finish-load', () => {
        console.log('[ApareText] Manager window loaded successfully');
        mainWindow.show();
        mainWindow.focus();
    });

    mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription) => {
        console.error('[ApareText] Manager window failed to load:', errorCode, errorDescription);
    });

    mainWindow.on('close', (event) => {
        if (!app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });
}

/**
 * Crear ventana de carga
 */
function createLoadingWindow() {
    loadingWindow = new BrowserWindow({
        width: WINDOW_SIZES.LOADING.width,
        height: WINDOW_SIZES.LOADING.height,
        show: false,
        frame: false,
        transparent: false, // Cambiar a false para mejor compatibilidad en Windows
        resizable: false,
        alwaysOnTop: true,
        backgroundColor: '#2c3e50', // Color de fondo sólido
        icon: createAppIcon(),
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    loadingWindow.loadFile('loading.html');

    loadingWindow.once('ready-to-show', () => {
        loadingWindow.show();
        loadingWindow.center(); // Centrar la ventana
    });
}

/**
 * Crear bandeja del sistema
 */
function createTray() {
    const icon = createAppIcon();
    tray = new Tray(icon);

    const contextMenu = Menu.buildFromTemplate([
        {
            label: 'ApareText v1.0',
            type: 'normal',
            enabled: false
        },
        { type: 'separator' },
        {
            label: isEnabled ? '✓ Enabled' : '✗ Disabled',
            type: 'normal',
            click: toggleEnabled
        },
        { type: 'separator' },
        {
            label: 'Open Palette (Ctrl+Space)',
            type: 'normal',
            click: showPalette
        },
        {
            label: 'Snippet Manager',
            type: 'normal',
            click: () => {
                mainWindow.show();
                mainWindow.focus();
            }
        },
        { type: 'separator' },
        {
            label: 'Quit',
            type: 'normal',
            click: () => {
                app.isQuitting = true;
                app.quit();
            }
        }
    ]);

    tray.setContextMenu(contextMenu);
    tray.setToolTip('ApareText - Text Expander (Click para abrir)');

    tray.on('click', showPalette);
}

/**
 * Toggle enabled/disabled
 */
function toggleEnabled() {
    isEnabled = !isEnabled;
    createTray();
}

/**
 * Mostrar paleta de comandos
 */
function showPalette() {
    if (!isEnabled) return;
    
    // Recrear la ventana si fue destruida
    if (!paletteWindow || paletteWindow.isDestroyed()) {
        createPaletteWindow();
    }
    
    if (paletteWindow) {
        // Centrar en pantalla actual
        const { screen } = require('electron');
        const cursor = screen.getCursorScreenPoint();
        const currentDisplay = screen.getDisplayNearestPoint(cursor);
        const { x, y, width, height } = currentDisplay.workArea;

        paletteWindow.setPosition(
            Math.floor(x + (width - 600) / 2),
            Math.floor(y + (height - 400) / 3)
        );

        paletteWindow.show();
        paletteWindow.focus();
    }
}

/**
 * Registrar hotkeys globales
 */
function registerHotkeys() {
    const ret = globalShortcut.register('CommandOrControl+Space', showPalette);

    if (!ret) {
        console.error('Failed to register global shortcut Ctrl+Space');
    }
}

/**
 * Verificar que el backend Python está funcionando
 */
async function checkApiServer(retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const result = await callPythonBackend('health');
            return result.status === 'healthy';
        } catch (error) {
            if (i < retries - 1) {
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }
    return false;
}

/**
 * Copiar texto al clipboard
 */
async function insertText(text) {
    const previousClipboard = clipboard.readText();
    clipboard.writeText(text);
    
    // Restaurar clipboard después de 10 segundos
    setTimeout(() => {
        clipboard.writeText(previousClipboard);
    }, 10000);
}

/**
 * Copiar imagen al clipboard desde Base64
 */
async function copyImageToClipboard(base64Data) {
    try {
        // Extraer el contenido Base64 (quitar el prefijo data:image/...)
        const base64Content = base64Data.includes(',') 
            ? base64Data.split(',')[1] 
            : base64Data;
        
        // Crear buffer desde Base64
        const buffer = Buffer.from(base64Content, 'base64');
        
        // Crear nativeImage desde el buffer
        const image = nativeImage.createFromBuffer(buffer);
        
        if (image.isEmpty()) {
            throw new Error('Invalid image data');
        }
        
        // Copiar al clipboard
        clipboard.writeImage(image);
        
        console.log('[ApareText] Image copied to clipboard successfully');
        return true;
    } catch (error) {
        console.error('[ApareText] Error copying image to clipboard:', error);
        throw error;
    }
}

/**
 * Verificar si el servidor API está disponible
 */
async function checkApiServer() {
    try {
        const response = await axios.get(`${API_URL}/`, { timeout: 2000 });
        return response.status === 200;
    } catch (error) {
        console.log('[ApareText] API not ready yet:', error.message);
        return false;
    }
}

/**
 * Inicialización de la aplicación
 */
app.whenReady().then(async () => {
    console.log('[ApareText] Starting...');

    // Crear ventana de carga
    createLoadingWindow();

    // Actualizar mensaje inicial
    if (loadingWindow && !loadingWindow.isDestroyed()) {
        loadingWindow.webContents.send('loading-update', {
            message: 'Iniciando servidor backend...',
            progress: 10
        });
    }

    // Iniciar backend automáticamente en producción
    const backendStarted = startBackendServer();

    // Esperar un poco para que el backend comience
    await new Promise(resolve => setTimeout(resolve, backendStarted ? 1000 : 500));

    if (loadingWindow && !loadingWindow.isDestroyed()) {
        loadingWindow.webContents.send('loading-update', {
            message: backendStarted ? 'Esperando que el servidor esté listo...' : 'Verificando servidor en modo desarrollo...',
            progress: 30
        });
    }

    // Verificar API con reintentos
    let apiAvailable = false;
    let attempts = 0;
    const maxAttempts = 30; // 30 segundos máximo

    console.log('[ApareText] Starting API check loop...');

    while (!apiAvailable && attempts < maxAttempts) {
        console.log(`[ApareText] API check attempt ${attempts + 1}/${maxAttempts}`);
        apiAvailable = await checkApiServer();
        console.log(`[ApareText] API available: ${apiAvailable}`);
        
        if (!apiAvailable) {
            attempts++;
            const progress = 30 + (attempts / maxAttempts) * 50; // 30% to 80%
            if (loadingWindow && !loadingWindow.isDestroyed()) {
                loadingWindow.webContents.send('loading-update', {
                    message: `Esperando servidor... (${attempts}/${maxAttempts})`,
                    progress: Math.min(progress, 80)
                });
            }
            await new Promise(resolve => setTimeout(resolve, 1000));
        }
    }

    console.log(`[ApareText] API check completed. Available: ${apiAvailable}, Attempts: ${attempts}`);

    if (!apiAvailable) {
        if (loadingWindow && !loadingWindow.isDestroyed()) {
            loadingWindow.webContents.send('loading-update', {
                message: 'Error: Servidor no disponible',
                progress: 0
            });
        }
        const { dialog } = require('electron');
        const result = await dialog.showMessageBox({
            type: 'warning',
            title: 'API Server Not Running',
            message: 'The Python API server is not running.',
            detail: app.isPackaged 
                ? 'The backend server failed to start. Please check the installation or try reinstalling.\n\nContinue anyway?'
                : 'Please start it with:\npython -m uvicorn server.api:app --reload --port 46321\n\nContinue anyway?',
            buttons: ['Quit', 'Continue']
        });
        
        if (result.response === 0) {
            app.quit();
            return;
        }
    }

    // Servidor listo
    if (loadingWindow && !loadingWindow.isDestroyed()) {
        loadingWindow.webContents.send('loading-update', {
            message: '¡Listo! Iniciando interfaz...',
            progress: 100
        });
    }

    // Esperar un momento para mostrar el 100% y que el usuario lo vea
    await new Promise(resolve => setTimeout(resolve, 1500));

    // Crear ventanas principales
    createMainWindow();
    createPaletteWindow();
    createTray();
    registerHotkeys();

    // Ocultar ventana de carga
    if (loadingWindow && !loadingWindow.isDestroyed()) {
        loadingWindow.hide();
    }

    console.log('[ApareText] Ready! Press Ctrl+Space to open palette');
});

/**
 * Limpiar al salir
 */
app.on('will-quit', () => {
    console.log('[ApareText] Shutting down...');
    globalShortcut.unregisterAll();
    stopBackendServer(); // Detener el backend
});

app.on('before-quit', () => {
    // Marcar que estamos cerrando para prevenir re-abrir ventanas
    app.isQuitting = true;
});

app.on('window-all-closed', () => {
    // No hacer quit (tenemos tray)
});

/**
 * IPC Handlers
 */
ipcMain.handle('get-snippets', async () => {
    try {
        const result = await callPythonBackend('get_snippets');
        return result;
    } catch (error) {
        console.error('Error fetching snippets:', error);
        return [];
    }
});

ipcMain.handle('search-snippets', async (event, query) => {
    try {
        const result = await callPythonBackend('search_snippets', [query]);
        return result;
    } catch (error) {
        console.error('Error searching snippets:', error);
        return [];
    }
});

ipcMain.handle('expand-snippet', async (event, snippetId, variables = {}) => {
    try {
        console.log('[EXPAND] 🔍 Fetching snippet:', snippetId);
        // Primero obtener el snippet para verificar su tipo
        const snippetResponse = await axios.get(`${API_URL}/api/snippets/${snippetId}`);
        const snippet = snippetResponse.data;
        console.log('[EXPAND] 📦 Snippet type:', snippet.snippet_type, '| Name:', snippet.name);
        
        // Si es snippet tipo IMAGE, copiar imagen directamente al clipboard
        if (snippet.snippet_type === 'image') {
            if (!snippet.image_data) {
                throw new Error('El snippet de imagen no tiene datos de imagen');
            }
            
            await copyImageToClipboard(snippet.image_data);
            
            // Mostrar notificación de éxito
            showNotification(
                'Imagen Copiada',
                `"${snippet.name}" se ha copiado al portapapeles`,
                'success'
            );
            
            // Ocultar paleta DESPUÉS de copiar
            setTimeout(() => {
                if (paletteWindow && !paletteWindow.isDestroyed()) {
                    paletteWindow.hide();
                }
            }, 100);
            
            return { success: true, type: 'image' };
        }
        
        // Si es snippet tipo TEXT, usar el endpoint de expansión normal
        const response = await axios.post(`${API_URL}/api/snippets/expand`, {
            snippet_id: snippetId,
            variables: variables,
            source: 'palette',
            target_app: 'electron'
        });

        const { content } = response.data;

        // Insertar texto (copiar a clipboard)
        await insertText(content);
        
        // Mostrar notificación de éxito
        showNotification(
            'Snippet Expandido',
            `"${snippet.name}" se ha insertado correctamente`,
            'success'
        );
        
        // Ocultar paleta DESPUÉS de copiar
        setTimeout(() => {
            if (paletteWindow && !paletteWindow.isDestroyed()) {
                paletteWindow.hide();
            }
        }, 100);

        return { success: true, type: 'text' };

    } catch (error) {
        console.error('Error expanding snippet:', error);
        showNotification(
            'Error al Expandir',
            `No se pudo expandir el snippet: ${error.message}`,
            'error'
        );
        return { success: false, error: error.message };
    }
});

ipcMain.handle('create-snippet', async (event, snippetData) => {
    try {
        const response = await axios.post(`${API_URL}/api/snippets`, snippetData);
        showNotification(
            'Snippet Creado',
            `"${snippetData.name}" se ha creado correctamente`,
            'success'
        );
        return response.data;
    } catch (error) {
        console.error('Error creating snippet:', error);
        showNotification(
            'Error al Crear',
            `No se pudo crear el snippet: ${error.message}`,
            'error'
        );
        throw error;
    }
});

ipcMain.handle('update-snippet', async (event, snippetId, snippetData) => {
    try {
        const response = await axios.put(`${API_URL}/api/snippets/${snippetId}`, snippetData);
        showNotification(
            'Snippet Actualizado',
            `"${snippetData.name}" se ha actualizado correctamente`,
            'success'
        );
        return response.data;
    } catch (error) {
        console.error('Error updating snippet:', error);
        showNotification(
            'Error al Actualizar',
            `No se pudo actualizar el snippet: ${error.message}`,
            'error'
        );
        throw error;
    }
});

ipcMain.handle('delete-snippet', async (event, snippetId) => {
    try {
        // Primero obtener el nombre del snippet para la notificación
        const snippetResponse = await axios.get(`${API_URL}/api/snippets/${snippetId}`);
        const snippetName = snippetResponse.data.name;
        
        await axios.delete(`${API_URL}/api/snippets/${snippetId}`);
        showNotification(
            'Snippet Eliminado',
            `"${snippetName}" se ha eliminado correctamente`,
            'success'
        );
        return { success: true };
    } catch (error) {
        console.error('Error deleting snippet:', error);
        showNotification(
            'Error al Eliminar',
            `No se pudo eliminar el snippet: ${error.message}`,
            'error'
        );
        throw error;
    }
});

// IPC: Abrir Manager desde el palette
ipcMain.on('open-manager', () => {
    if (mainWindow) {
        mainWindow.show();
        mainWindow.focus();
    }
});

// IPC: Abrir Manager en modo "nuevo snippet"
ipcMain.on('open-manager-new', () => {
    if (mainWindow) {
        mainWindow.show();
        mainWindow.focus();
        // Enviar evento al manager para que abra el formulario de nuevo snippet
        mainWindow.webContents.once('dom-ready', () => {
            mainWindow.webContents.send('trigger-new-snippet');
        });
    }
});

// ============================================
// NUEVOS IPC HANDLERS
// ============================================

// IPC: Obtener estadísticas
ipcMain.handle('get-stats', async (event) => {
    try {
        const response = await axios.get(`${API_URL}/api/stats`);
        return response.data;
    } catch (error) {
        console.error('[ApareText] Error getting stats:', error);
        return {
            total_uses: 0,
            top_snippets: []
        };
    }
});

// IPC: Exportar snippets
ipcMain.handle('export-snippets', async (event) => {
    try {
        const response = await axios.get(`${API_URL}/api/export`);
        return response.data;
    } catch (error) {
        console.error('[ApareText] Error exporting snippets:', error);
        throw error;
    }
});

// IPC: Guardar archivo (dialog)
ipcMain.handle('save-file-dialog', async (event, options) => {
    const { dialog } = require('electron');
    const fs = require('fs').promises;
    
    try {
        const result = await dialog.showSaveDialog(mainWindow || paletteWindow, {
            title: 'Exportar Snippets',
            defaultPath: options.defaultPath,
            filters: options.filters
        });

        if (!result.canceled && result.filePath) {
            // Obtener datos de exportación
            const response = await axios.get(`${API_URL}/api/export`);
            await fs.writeFile(result.filePath, JSON.stringify(response.data, null, 2), 'utf8');
            return result.filePath;
        }
        
        return null;
    } catch (error) {
        console.error('[ApareText] Error saving file:', error);
        throw error;
    }
});

// IPC: Abrir archivo (dialog)
ipcMain.handle('open-file-dialog', async (event, options) => {
    const { dialog } = require('electron');
    
    try {
        const result = await dialog.showOpenDialog(mainWindow || paletteWindow, {
            title: 'Importar Snippets',
            filters: options.filters,
            properties: options.properties
        });

        if (!result.canceled && result.filePaths && result.filePaths.length > 0) {
            return result.filePaths[0];
        }
        
        return null;
    } catch (error) {
        console.error('[ApareText] Error opening file:', error);
        throw error;
    }
});

// IPC: Importar snippets
ipcMain.handle('import-snippets', async (event, filePath) => {
    const fs = require('fs').promises;
    
    try {
        // Leer archivo
        const content = await fs.readFile(filePath, 'utf8');
        const data = JSON.parse(content);
        
        // Enviar al API
        const response = await axios.post(`${API_URL}/api/import`, data);
        return response.data;
    } catch (error) {
        console.error('[ApareText] Error importing snippets:', error);
        throw error;
    }
});

// ============================================
// CONFIGURATION SYSTEM
// ============================================

// Configuración por defecto
const DEFAULT_CONFIG = {
    theme: 'light',
    fontSize: 'medium',
    autoExpand: false,
    confirmDelete: true,
    showNotifications: true,
    fuzzySearch: true,
    searchTags: true,
    defaultSort: 'name',
    autoBackup: false,
    backupFreq: 'weekly',
    backupPath: ''
};

let userConfig = { ...DEFAULT_CONFIG };

// Cargar configuración desde archivo
async function loadConfig() {
    try {
        const configPath = path.join(app.getPath('userData'), 'config.json');
        const configData = await fs.readFile(configPath, 'utf8');
        const savedConfig = JSON.parse(configData);
        userConfig = { ...DEFAULT_CONFIG, ...savedConfig };
    } catch (error) {
        // Si no existe el archivo, usar configuración por defecto
        userConfig = { ...DEFAULT_CONFIG };
    }
}

// Guardar configuración a archivo
async function saveConfig(config) {
    try {
        const configPath = path.join(app.getPath('userData'), 'config.json');
        await fs.writeFile(configPath, JSON.stringify(config, null, 2));
        userConfig = { ...config };
    } catch (error) {
        console.error('[ApareText] Error saving config:', error);
        throw error;
    }
}

// IPC: Obtener configuración
ipcMain.handle('get-config', async () => {
    await loadConfig();
    return userConfig;
});

// IPC: Guardar configuración
ipcMain.handle('save-config', async (event, config) => {
    await saveConfig(config);
    return { success: true };
});

// IPC: Seleccionar directorio
ipcMain.handle('select-directory', async () => {
    if (!mainWindow) return null;
    
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openDirectory'],
        title: 'Seleccionar carpeta para backups'
    });
    
    if (result.canceled) {
        return null;
    }
    
    return result.filePaths[0];
});

// ============================================
// FIN CONFIGURATION SYSTEM
// ============================================

// ============================================
// FIN NUEVOS IPC HANDLERS
// ============================================

console.log('[ApareText] Electron loaded');
