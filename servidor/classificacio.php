<?php
/**
 * Progres de l'Aventura Matematica (osuhosting.com).
 *
 * Sense classificacio ni noms (25 set 2026): cada nen es nomes una clau calculada
 * per l'app, amb els seus totals i els dies que ha jugat. No hi ha cap accio que
 * llisti els altres nens. Dades en un JSON al costat, amb bloqueig de fitxer.
 *
 * cfg.php (no va a git) torna ['clau' => '<secret>'].
 */
header('Content-Type: application/json; charset=utf-8');

$cfg = @include __DIR__ . '/cfg.php';
if (!is_array($cfg) || empty($cfg['clau'])) {
    http_response_code(500);
    exit(json_encode(['ok' => false, 'error' => 'servidor sense configurar']));
}
if (!hash_equals($cfg['clau'], $_SERVER['HTTP_X_MATES_KEY'] ?? '')) {
    http_response_code(403);
    exit(json_encode(['ok' => false, 'error' => 'clau incorrecta']));
}

$dades = json_decode(file_get_contents('php://input'), true);
if (!is_array($dades)) {
    http_response_code(400);
    exit(json_encode(['ok' => false, 'error' => 'peticio invalida']));
}

$FITXER = __DIR__ . '/progres.json';
$CAMPS  = ['punts', 'encerts', 'errors', 'millor_ratxa', 'partides'];
$MAX_DIES = 3000;

function falla($codi, $msg) {
    http_response_code($codi);
    exit(json_encode(['ok' => false, 'error' => $msg]));
}

function clau_valida($d) {
    $clau = (string)($d['clau'] ?? '');
    if (!preg_match('/^[a-f0-9]{8,32}$/', $clau)) falla(400, 'clau invalida');
    return $clau;
}

function llegeix($f) {
    if (!file_exists($f)) return [];
    $j = json_decode(file_get_contents($f), true);
    return is_array($j) ? $j : [];
}

/** Obre el fitxer amb bloqueig, deixa que $canvi modifiqui les dades i les desa. */
function amb_bloqueig($f, $canvi) {
    $fh = fopen($f, 'c+');
    if (!$fh || !flock($fh, LOCK_EX)) falla(500, 'no es pot escriure');
    $t = stream_get_contents($fh);
    $tot = json_decode($t ?: '[]', true);
    if (!is_array($tot)) $tot = [];
    $tot = $canvi($tot);
    ftruncate($fh, 0);
    rewind($fh);
    fwrite($fh, json_encode($tot));
    fflush($fh);
    flock($fh, LOCK_UN);
    fclose($fh);
}

$accio = $dades['accio'] ?? '';

if ($accio === 'jugador') {
    $clau = clau_valida($dades);
    $j = llegeix($FITXER)[$clau] ?? null;
    if (!$j) exit(json_encode(['ok' => true, 'jugador' => null]));
    $out = array_intersect_key($j, array_flip($CAMPS));
    $out['dies'] = array_values($j['dies'] ?? []);
    exit(json_encode(['ok' => true, 'jugador' => $out]));
}

if ($accio === 'desa') {
    $clau = clau_valida($dades);
    amb_bloqueig($FITXER, function ($tot) use ($clau, $dades, $CAMPS) {
        $fila = $tot[$clau] ?? ['dies' => []];
        foreach ($CAMPS as $c) {
            // mai baixem un total: si arriben dues pestanyes a l'hora, es queda el millor
            $fila[$c] = max((int)($fila[$c] ?? 0), max(0, (int)($dades[$c] ?? 0)));
        }
        $fila['actualitzat'] = gmdate('c');
        $tot[$clau] = $fila;
        return $tot;
    });
    exit(json_encode(['ok' => true]));
}

if ($accio === 'dia') {
    $clau = clau_valida($dades);
    $dia = (string)($dades['dia'] ?? '');
    $data = DateTime::createFromFormat('!Y-m-d', $dia);
    // nomes dates reals, i no del futur (marge d'un dia per les zones horaries)
    if (!$data || $data->format('Y-m-d') !== $dia || $data > new DateTime('+1 day')) {
        falla(400, 'dia invalid');
    }
    amb_bloqueig($FITXER, function ($tot) use ($clau, $dia, $MAX_DIES) {
        $fila = $tot[$clau] ?? ['dies' => []];
        $dies = $fila['dies'] ?? [];
        if (!in_array($dia, $dies, true)) {
            $dies[] = $dia;
            sort($dies);
            $dies = array_slice($dies, -$MAX_DIES);
        }
        $fila['dies'] = $dies;
        $tot[$clau] = $fila;
        return $tot;
    });
    exit(json_encode(['ok' => true]));
}

falla(400, 'accio desconeguda');
