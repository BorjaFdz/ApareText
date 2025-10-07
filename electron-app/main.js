/**
 * ApareText - Electron Main Process (Simplified)
 * Paleta de comandos funcional sin módulos complejos
 */

const { app, BrowserWindow, ipcMain, globalShortcut, Tray, Menu, clipboard, nativeImage } = require('electron');
const path = require('path');
const axios = require('axios');

// Configuración
const API_URL = 'http://127.0.0.1:46321';
let mainWindow = null;
let paletteWindow = null;
let tray = null;
let isEnabled = true;

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
        width: 600,
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
        width: 1200,
        height: 800,
        show: false,
        transparent: true,
        backgroundColor: '#00000000',
        frame: true,
        icon: createAppIcon(),
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });

    mainWindow.loadFile('manager.html');

    mainWindow.on('close', (event) => {
        if (!app.isQuitting) {
            event.preventDefault();
            mainWindow.hide();
        }
    });
}

/**
 * Crear bandeja del sistema
 */
function createTray() {
    const icon = createAppIcon();
    tray = new Tray(icon);
    
    console.log('✅ Tray icon created (16x16 bright green)');

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
    tray.setToolTip('📝 ApareText - Text Expander (Click para abrir)');

    tray.on('click', showPalette);
}

/**
 * Toggle enabled/disabled
 */
function toggleEnabled() {
    isEnabled = !isEnabled;
    createTray(); // Refresh menu
    console.log(`ApareText ${isEnabled ? 'enabled' : 'disabled'}`);
}

/**
 * Mostrar paleta de comandos
 */
function showPalette() {
    if (!isEnabled) return;
    
    // Recrear la ventana si fue destruida
    if (!paletteWindow || paletteWindow.isDestroyed()) {
        console.log('Recreating palette window...');
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
    // Ctrl+Space para paleta
    const ret = globalShortcut.register('CommandOrControl+Space', showPalette);

    if (!ret) {
        console.error('❌ Failed to register global shortcut');
    } else {
        console.log('✅ Global hotkey registered: Ctrl+Space');
    }
}

/**
 * Verificar que el servidor API está corriendo
 */
async function checkApiServer(retries = 3) {
    for (let i = 0; i < retries; i++) {
        try {
            const response = await axios.get(`${API_URL}/health`, { timeout: 2000 });
            console.log('✅ API Server connected:', response.data);
            return true;
        } catch (error) {
            if (i < retries - 1) {
                console.log(`⏳ Waiting for API server... (attempt ${i + 1}/${retries})`);
                await new Promise(resolve => setTimeout(resolve, 1000));
            }
        }
    }
    console.error('❌ API Server not available. Please start it first:');
    console.error('   python -m server.main');
    return false;
}

/**
 * Simular escritura de texto (método simple sin librerías nativas)
 */
async function insertText(text) {
    // Guardar clipboard anterior
    const previousClipboard = clipboard.readText();
    
    // Copiar al clipboard
    clipboard.writeText(text);
    
    console.log('✅ Text copied to clipboard.');
    console.log('   Press Ctrl+V to paste in your target application.');
    
    // Restaurar clipboard después de 10 segundos
    setTimeout(() => {
        clipboard.writeText(previousClipboard);
    }, 10000);
}

/**
 * Inicialización de la aplicación
 */
app.whenReady().then(async () => {
    console.log('🚀 ApareText Electron starting...');

    // Verificar API
    const apiAvailable = await checkApiServer();
    if (!apiAvailable) {
        const { dialog } = require('electron');
        const result = await dialog.showMessageBox({
            type: 'warning',
            title: 'API Server Not Running',
            message: 'The Python API server is not running.',
            detail: 'Please start it with:\npython -m server.main\n\nContinue anyway?',
            buttons: ['Quit', 'Continue']
        });
        
        if (result.response === 0) {
            app.quit();
            return;
        }
    }

    // Crear ventanas
    createMainWindow();
    createPaletteWindow();
    createTray();

    // Registrar hotkeys
    registerHotkeys();

    console.log('✅ ApareText ready!');
    console.log('');
    console.log('📋 How to use:');
    console.log('   1. Press Ctrl+Space to open palette');
    console.log('   2. Search for your snippet');
    console.log('   3. Press Enter to select');
    console.log('   4. Text is copied to clipboard');
    console.log('   5. Press Ctrl+V to paste anywhere');
    console.log('');
    console.log('💡 Tip: Click the tray icon for quick access');
});

/**
 * Limpiar al salir
 */
app.on('will-quit', () => {
    globalShortcut.unregisterAll();
});

app.on('window-all-closed', () => {
    // No hacer quit (tenemos tray)
});

/**
 * IPC Handlers
 */
ipcMain.handle('get-snippets', async () => {
    try {
        const response = await axios.get(`${API_URL}/api/snippets`);
        return response.data;
    } catch (error) {
        console.error('Error fetching snippets:', error);
        return [];
    }
});

ipcMain.handle('search-snippets', async (event, query) => {
    try {
        const response = await axios.get(`${API_URL}/api/snippets/search/${encodeURIComponent(query)}`);
        return response.data;
    } catch (error) {
        console.error('Error searching snippets:', error);
        return [];
    }
});

ipcMain.handle('expand-snippet', async (event, snippetId, variables = {}) => {
    try {
        const response = await axios.post(`${API_URL}/api/snippets/expand`, {
            snippet_id: snippetId,
            variables: variables,
            source: 'palette',
            target_app: 'electron'
        });

        const { content } = response.data;

        // Insertar texto (copiar a clipboard)
        await insertText(content);
        
        // Ocultar paleta DESPUÉS de copiar
        setTimeout(() => {
            if (paletteWindow && !paletteWindow.isDestroyed()) {
                paletteWindow.hide();
            }
        }, 100);

        return { success: true };

    } catch (error) {
        console.error('Error expanding snippet:', error);
        return { success: false, error: error.message };
    }
});

ipcMain.handle('create-snippet', async (event, snippetData) => {
    try {
        const response = await axios.post(`${API_URL}/api/snippets`, snippetData);
        console.log('✅ Snippet created:', response.data.id);
        return response.data;
    } catch (error) {
        console.error('Error creating snippet:', error);
        throw error;
    }
});

ipcMain.handle('update-snippet', async (event, snippetId, snippetData) => {
    try {
        const response = await axios.put(`${API_URL}/api/snippets/${snippetId}`, snippetData);
        console.log('✅ Snippet updated:', snippetId);
        return response.data;
    } catch (error) {
        console.error('Error updating snippet:', error);
        throw error;
    }
});

ipcMain.handle('delete-snippet', async (event, snippetId) => {
    try {
        await axios.delete(`${API_URL}/api/snippets/${snippetId}`);
        console.log('✅ Snippet deleted:', snippetId);
        return { success: true };
    } catch (error) {
        console.error('Error deleting snippet:', error);
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

console.log('📝 ApareText Electron loaded');
