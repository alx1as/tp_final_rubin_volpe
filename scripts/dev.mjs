import { spawn } from 'node:child_process';
import { existsSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const raiz = join(dirname(fileURLToPath(import.meta.url)), '..');
const windows = process.platform === 'win32';
const python = join(raiz, 'backend', '.venv', windows ? 'Scripts' : 'bin', windows ? 'python.exe' : 'python');
const vite = join(raiz, 'frontend', 'node_modules', 'vite', 'bin', 'vite.js');

if (!existsSync(python)) {
  console.error('No se encontro el entorno virtual en backend/.venv.');
  process.exit(1);
}
if (!existsSync(vite)) {
  console.error('No se encontro Vite. Ejecuta npm install dentro de frontend si aun no instalaste sus dependencias.');
  process.exit(1);
}

const procesos = [];
let cerrando = false;

function cerrar(codigo = 0) {
  if (cerrando) return;
  cerrando = true;
  for (const proceso of procesos) {
    if (proceso.exitCode === null && proceso.signalCode === null) {
      proceso.kill();
    }
  }
  setTimeout(() => process.exit(codigo), 800).unref();
}

function iniciar(nombre, comando, argumentos, directorio) {
  const proceso = spawn(comando, argumentos, { cwd: directorio, stdio: 'inherit' });
  procesos.push(proceso);
  proceso.on('error', (error) => {
    console.error(`No se pudo iniciar ${nombre}: ${error.message}`);
    cerrar(1);
  });
  proceso.on('exit', (codigo) => {
    if (!cerrando) {
      console.error(`${nombre} se detuvo (codigo ${codigo ?? 'desconocido'}).`);
      cerrar(codigo || 1);
    }
  });
}

process.on('SIGINT', () => cerrar());
process.on('SIGTERM', () => cerrar());

console.log('Iniciando FastAPI y React...');
iniciar('FastAPI', python, ['-m', 'uvicorn', 'app.main:create_app', '--factory', '--app-dir', 'backend', '--reload'], raiz);
iniciar('React', process.execPath, [vite], join(raiz, 'frontend'));
