import test from 'node:test';
import assert from 'node:assert/strict';
import { guardarEscolaridad, guardarProfesionalTratante, guardarObjetivo, guardarAdmision, solicitar, ErrorAPI } from '../src/servicios/api.ts';

for (const [nombre, guardar, recurso] of [
  ['escolaridad', guardarEscolaridad, 'escolaridades'],
  ['profesional tratante', guardarProfesionalTratante, 'profesionales-tratantes'],
  ['objetivo', guardarObjetivo, 'objetivos'],
]) {
  test(`${nombre}: alta POST, edición PATCH y cookie de sesión`, async (t) => {
    const llamadas = [];
    t.mock.method(globalThis, 'fetch', async (url, opciones) => {
      llamadas.push([url, opciones]);
      return new Response(JSON.stringify({ id: 7 }), { status: 200 });
    });
    const datos = { fecha_inicio: '2026-03-01' };
    assert.deepEqual(await guardar(4, datos), { id: 7 });
    assert.deepEqual(await guardar(4, datos, 7), { id: 7 });
    assert.equal(llamadas[0][0], `/api/pacientes/4/${recurso}`);
    assert.equal(llamadas[0][1].method, 'POST');
    assert.equal(llamadas[1][0], `/api/pacientes/4/${recurso}/7`);
    assert.equal(llamadas[1][1].method, 'PATCH');
    assert.equal(llamadas[1][1].credentials, 'include');
    assert.deepEqual(JSON.parse(llamadas[1][1].body), datos);
  });
}
test('admisión conserva PUT como recurso único', async (t) => {
  const fetch = t.mock.method(globalThis, 'fetch', async () => new Response('{}'));
  await guardarAdmision(4, {});
  assert.equal(fetch.mock.calls[0].arguments[0], '/api/pacientes/4/admision');
  assert.equal(fetch.mock.calls[0].arguments[1].method, 'PUT');
});
test('cliente HTTP conserva mensaje de conflicto del backend', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => new Response(JSON.stringify({ detail: 'Conflicto de integridad' }), { status: 409 }));
  await assert.rejects(solicitar('/api/ejemplo'), (error) => error instanceof ErrorAPI && error.status === 409 && error.message === 'Conflicto de integridad');
});
