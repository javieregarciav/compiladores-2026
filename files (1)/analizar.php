<?php
/**
 * analizar.php
 * ------------
 * Endpoint PHP que recibe código fuente vía POST/JSON,
 * lo pasa al lexer Python real (lexer.py + tabla_simbolos.py)
 * y devuelve el resultado como JSON al navegador.
 *
 * Flujo:
 *   index.php  →  fetch POST  →  analizar.php  →  python3 bridge.py  →  JSON
 *
 * Requiere:
 *   - PHP 7.4+ con exec() habilitado
 *   - Python 3.10+ en PATH (comando: python3)
 *   - bridge.py en la misma carpeta
 */

// ── Headers CORS + JSON ────────────────────────────────────────────
header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

// Manejo de preflight OPTIONS
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// ── Solo aceptar POST ──────────────────────────────────────────────
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Método no permitido. Usa POST.']);
    exit;
}

// ── Leer body JSON ────────────────────────────────────────────────
$body = file_get_contents('php://input');
$data = json_decode($body, true);

if (json_last_error() !== JSON_ERROR_NONE || !isset($data['codigo'])) {
    http_response_code(400);
    echo json_encode(['error' => 'JSON inválido o campo "codigo" faltante.']);
    exit;
}

$codigo = $data['codigo'];

// ── Validación básica de tamaño ────────────────────────────────────
if (strlen($codigo) > 64000) {
    http_response_code(413);
    echo json_encode(['error' => 'Código demasiado largo (máx. 64 KB).']);
    exit;
}

// ── Escribir el código en un archivo temporal ──────────────────────
// (Evita problemas de escapado en la línea de comandos)
$tmpDir  = sys_get_temp_dir();
$tmpFile = tempnam($tmpDir, 'minicomp_') . '.ml';

if (file_put_contents($tmpFile, $codigo) === false) {
    http_response_code(500);
    echo json_encode(['error' => 'No se pudo crear el archivo temporal.']);
    exit;
}

// ── Construir el comando ───────────────────────────────────────────
// bridge.py recibe la ruta del archivo temporal como argumento
$bridgePath  = __DIR__ . '/bridge.py';
// En Windows el binario suele ser 'python'; en Linux/Mac es 'python3'
$python      = (PHP_OS_FAMILY === 'Windows') ? 'python' : 'python3';

// escapeshellarg protege contra inyección de comandos
$cmd = escapeshellcmd($python) . ' '
     . escapeshellarg($bridgePath) . ' '
     . escapeshellarg($tmpFile)
     . ' 2>&1';

// ── Ejecutar el lexer ──────────────────────────────────────────────
$output     = [];
$returnCode = 0;
exec($cmd, $output, $returnCode);

// Limpiar archivo temporal
@unlink($tmpFile);

$outputStr = implode("\n", $output);

// ── Verificar errores de ejecución ────────────────────────────────
if ($returnCode !== 0) {
    http_response_code(500);
    echo json_encode([
        'error'  => 'Error al ejecutar el lexer Python.',
        'detalle' => $outputStr,
    ]);
    exit;
}

// ── Decodificar resultado JSON del bridge ─────────────────────────
$resultado = json_decode($outputStr, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    http_response_code(500);
    echo json_encode([
        'error'   => 'El lexer no devolvió JSON válido.',
        'detalle' => $outputStr,
    ]);
    exit;
}

// ── Responder al frontend ──────────────────────────────────────────
echo json_encode($resultado, JSON_UNESCAPED_UNICODE);
