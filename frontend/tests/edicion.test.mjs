import test from 'node:test';
import assert from 'node:assert/strict';
import { crearRegistroEdicion } from '../src/hooks/estadoEdicion.ts';
import { escolaridadVigente, periodoSesiones } from '../src/modulos/pacientes/seguimientoFechas.ts';

function entorno() {
  const registro = crearRegistroEdicion();
  const llamadas = [];
  const confirmar = (respuesta) => registro.confirmar((mensaje) => { llamadas.push(['confirmar', mensaje]); return respuesta; }, (mensaje) => llamadas.push(['aviso', mensaje]));
  return { registro, llamadas, confirmar };
}
test('sin editores o con formulario intacto permite navegar sin confirmar', () => {
  const { registro, llamadas, confirmar } = entorno();
  assert.equal(confirmar(false), true);
  registro.registrar(Symbol(), { pendiente: false, ocupado: false });
  assert.equal(confirmar(false), true);
  assert.deepEqual(llamadas, []);
});
test('un editor modificado permite cancelar o confirmar el abandono', () => {
  const { registro, llamadas, confirmar } = entorno();
  registro.registrar(Symbol(), { pendiente: true, ocupado: false });
  assert.equal(confirmar(false), false);
  assert.equal(confirmar(true), true);
  assert.deepEqual(llamadas.map(([tipo]) => tipo), ['confirmar', 'confirmar']);
});
test('una operación bloquea la navegación incluso si hay cambios pendientes', () => {
  const { registro, llamadas, confirmar } = entorno();
  registro.registrar(Symbol(), { pendiente: true, ocupado: false });
  registro.registrar(Symbol(), { pendiente: false, ocupado: true });
  assert.equal(confirmar(true), false);
  assert.deepEqual(llamadas.map(([tipo]) => tipo), ['aviso']);
});
test('audio pendiente protege la sesión aunque el formulario esté intacto', () => {
  const { registro, confirmar } = entorno();
  const audio = Symbol();
  registro.registrar(Symbol(), { pendiente: false, ocupado: false });
  registro.registrar(audio, { pendiente: true, ocupado: false });
  assert.equal(confirmar(false), false);
  registro.retirar(audio);
  assert.equal(confirmar(false), true);
});
test('actualizar y retirar editores no deja bloqueos residuales', () => {
  const { registro, confirmar } = entorno();
  const id = Symbol();
  registro.registrar(id, { pendiente: true, ocupado: true });
  registro.registrar(id, { pendiente: false, ocupado: false });
  assert.equal(confirmar(false), true);
  registro.retirar(id);
  assert.deepEqual(registro.estado(), { pendiente: false, ocupado: false });
});
test('escolaridad con fecha de fin futura o igual a hoy permanece vigente', () => {
  const registro = { fecha_inicio: '2026-03-01', fecha_fin: '2026-12-15' };
  assert.equal(escolaridadVigente([registro], '2026-11-25'), registro);
  assert.equal(escolaridadVigente([registro], '2026-12-15'), registro);
  assert.equal(escolaridadVigente([registro], '2026-12-16'), undefined);
});
test('escolaridad elige el período vigente más reciente sin mutar la colección', () => {
  const anterior = { fecha_inicio: '2025-03-01', fecha_fin: null };
  const actual = { fecha_inicio: '2026-03-01', fecha_fin: null };
  const futuro = { fecha_inicio: '2027-03-01', fecha_fin: null };
  const registros = [anterior, actual, futuro];
  assert.equal(escolaridadVigente(registros, '2026-11-25'), actual);
  assert.deepEqual(registros, [anterior, actual, futuro]);
});
test('período de informe usa extremos del historial y hoy si no existen sesiones', () => {
  assert.deepEqual(periodoSesiones([{ fecha: '2026-11-01' }, { fecha: '2026-06-01' }], '2026-11-25'), { periodo_desde: '2026-06-01', periodo_hasta: '2026-11-01' });
  assert.deepEqual(periodoSesiones([], '2026-11-25'), { periodo_desde: '2026-11-25', periodo_hasta: '2026-11-25' });
});
