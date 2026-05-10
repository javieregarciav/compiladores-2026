<?php

header('Content-Type: application/json; charset=utf-8');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['error' => 'Método no permitido. Usa POST.']);
    exit;
}

$body = file_get_contents('php://input');
$data = json_decode($body, true);

if (json_last_error() !== JSON_ERROR_NONE || !isset($data['codigo'])) {
    http_response_code(400);
    echo json_encode(['error' => 'JSON inválido o campo "codigo" faltante.']);
    exit;
}

$codigo = $data['codigo'];

if (strlen($codigo) > 64000) {
    http_response_code(413);
    echo json_encode(['error' => 'Código demasiado largo (máx. 64 KB).']);
    exit;
}

$tmpDir  = sys_get_temp_dir();
$tmpFile = tempnam($tmpDir, 'minicomp_') . '.ml';

if (file_put_contents($tmpFile, $codigo) === false) {
    http_response_code(500);
    echo json_encode(['error' => 'No se pudo crear el archivo temporal.']);
    exit;
}

$bridgePath  = __DIR__ . '/bridge.py';

$python      = (PHP_OS_FAMILY === 'Windows') ? 'python' : 'python3';

$cmd = escapeshellcmd($python) . ' '
     . escapeshellarg($bridgePath) . ' '
     . escapeshellarg($tmpFile)
     . ' 2>&1';

$output     = [];
$returnCode = 0;
exec($cmd, $output, $returnCode);

@unlink($tmpFile);

$outputStr = implode("\n", $output);

if ($returnCode !== 0) {
    http_response_code(500);
    echo json_encode([
        'error'  => 'Error al ejecutar el lexer Python.',
        'detalle' => $outputStr,
    ]);
    exit;
}

$resultado = json_decode($outputStr, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    http_response_code(500);
    echo json_encode([
        'error'   => 'El lexer no devolvió JSON válido.',
        'detalle' => $outputStr,
    ]);
    exit;
}

echo json_encode($resultado, JSON_UNESCAPED_UNICODE);
