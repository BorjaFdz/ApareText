#!/usr/bin/env node

/**
 * Script que se ejecuta antes del build de Electron
 * Mata procesos relacionados y limpia archivos bloqueados
 */

const { execSync, spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

console.log('🧹 Ejecutando limpieza previa al build...');

// Función para ejecutar comandos de forma segura
function runCommand(command, description) {
  try {
    console.log(`📋 ${description}...`);
    execSync(command, { stdio: 'inherit' });
    console.log(`✅ ${description} completado`);
  } catch (error) {
    console.log(`⚠️  ${description} falló (posiblemente no hay procesos para matar):`, error.message);
  }
}

// 1. Matar procesos relacionados con ApareText
console.log('🔪 Matando procesos relacionados...');
runCommand('taskkill /F /IM "ApareText*.exe" /T', 'Matar procesos ApareText');
runCommand('taskkill /F /IM "electron.exe" /T', 'Matar procesos Electron');
runCommand('taskkill /F /IM "node.exe" /T', 'Matar procesos Node.js');

// 2. Esperar un momento para que los procesos se cierren
console.log('⏳ Esperando que los procesos se cierren...');
setTimeout(() => {
  // 3. Limpiar directorios de build
  const dirsToClean = ['dist', 'build'];

  dirsToClean.forEach(dir => {
    const fullPath = path.join(__dirname, '..', dir);
    if (fs.existsSync(fullPath)) {
      console.log(`🗑️  Limpiando directorio ${dir}...`);
      try {
        // Usar rimraf si está disponible, sino fs.rmSync
        if (fs.rmSync) {
          fs.rmSync(fullPath, { recursive: true, force: true });
        } else {
          // Fallback para versiones antiguas de Node
          execSync(`rimraf "${fullPath}"`, { stdio: 'inherit' });
        }
        console.log(`✅ Directorio ${dir} limpiado`);
      } catch (error) {
        console.log(`⚠️  Error limpiando ${dir}:`, error.message);
      }
    }
  });

  // 4. Crear directorios limpios
  dirsToClean.forEach(dir => {
    const fullPath = path.join(__dirname, '..', dir);
    if (!fs.existsSync(fullPath)) {
      fs.mkdirSync(fullPath, { recursive: true });
      console.log(`📁 Directorio ${dir} creado`);
    }
  });

  console.log('🎉 Limpieza previa al build completada');
}, 2000);