<?php
/**
 * Classificacio de l'Aventura Matematica (osuhosting.com).
 *
 * Guarda NOMES el nom public ("Jan D.") i una clau calculada per l'app: aqui no
 * hi arriba mai el cognom sencer. Dades en un JSON al costat, amb bloqueig de
 * fitxer: la classe son unes desenes de nens, no cal cap base de dades.
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

$FITXER = __DIR__ . '/classificacio.json';
$CAMPS  = ['punts', 'encerts', 'errors', 'millor_ratxa', 'partides'];

function llegeix($f) {
    if (!file_exists($f)) return [];
    $t = file_get_contents($f);
    $j = json_decode($t, true);
    return is_array($j) ? $j : [];
}

$accio = $dades['accio'] ?? '';

if ($accio === 'top') {
    $n = min(max((int)($dades['n'] ?? 20), 1), 100);
    $tot = llegeix($FITXER);
    uasort($tot, function ($a, $b) {
        return [$b['punts'], $b['millor_ratxa']] <=> [$a['punts'], $a['millor_ratxa']];
    });
    $out = [];
    foreach (array_slice($tot, 0, $n, true) as $clau => $j) {
        $out[] = ['clau' => $clau, 'nom' => $j['nom']] + array_intersect_key($j, array_flip($CAMPS));
    }
    exit(json_encode(['ok' => true, 'top' => $out]));
}

if ($accio === 'jugador') {
    $clau = (string)($dades['clau'] ?? '');
    $tot = llegeix($FITXER);
    $j = $tot[$clau] ?? null;
    if (!$j) exit(json_encode(['ok' => true, 'jugador' => null]));
    exit(json_encode(['ok' => true,
        'jugador' => array_intersect_key($j, array_flip($CAMPS)) + ['nom' => $j['nom']]]));
}

if ($accio === 'desa') {
    $clau = (string)($dades['clau'] ?? '');
    $nom  = trim((string)($dades['nom'] ?? ''));
    if (!preg_match('/^[a-f0-9]{8,32}$/', $clau) || $nom === '') {
        http_response_code(400);
        exit(json_encode(['ok' => false, 'error' => 'clau o nom invalids']));
    }
    // per si de cas: aqui nomes hi pot haver "Nom I." (una paraula + inicial)
    $nom = mb_substr(preg_replace('/\s+/u', ' ', $nom), 0, 40);
    $fh = fopen($FITXER, 'c+');
    if (!$fh || !flock($fh, LOCK_EX)) {
        http_response_code(500);
        exit(json_encode(['ok' => false, 'error' => 'no es pot escriure']));
    }
    $t = stream_get_contents($fh);
    $tot = json_decode($t ?: '[]', true);
    if (!is_array($tot)) $tot = [];
    // dos nens poden ser tots dos "Jan D.": el segon surt com a "Jan D. 2"
    $agafats = [];
    foreach ($tot as $k => $j) if ($k !== $clau) $agafats[$j['nom']] = true;
    if (isset($agafats[$nom])) {
        $n = 2;
        while (isset($agafats[$nom . ' ' . $n])) $n++;
        $nom = $nom . ' ' . $n;
    }
    $fila = ['nom' => $nom, 'actualitzat' => gmdate('c')];
    foreach ($CAMPS as $c) $fila[$c] = max(0, (int)($dades[$c] ?? 0));
    // mai baixem un total: si arriben dues pestanyes a l'hora, es queda el millor
    if (isset($tot[$clau])) {
        foreach ($CAMPS as $c) $fila[$c] = max($fila[$c], (int)($tot[$clau][$c] ?? 0));
        $fila['nom'] = $tot[$clau]['nom'];   // el nom assignat no canvia mai
    }
    $tot[$clau] = $fila;
    ftruncate($fh, 0);
    rewind($fh);
    fwrite($fh, json_encode($tot, JSON_UNESCAPED_UNICODE));
    fflush($fh);
    flock($fh, LOCK_UN);
    fclose($fh);
    exit(json_encode(['ok' => true, 'nom' => $fila['nom']]));
}

http_response_code(400);
echo json_encode(['ok' => false, 'error' => 'accio desconeguda']);
