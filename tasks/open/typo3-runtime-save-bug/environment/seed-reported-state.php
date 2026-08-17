<?php

declare(strict_types=1);

/**
 * Put the instance into the state a real bug report described.
 *
 * This seeds *data*, not a defect. The defect is the extension's own, present
 * at the pinned commit, and nothing here touches its code. What is recreated
 * is the situation an editor reported from production: a translation record
 * that will not save, and beside it the orphaned row the failed save left
 * behind — `sys_language_uid = 0` with unresolved foreign keys, colliding with
 * the unique key `translation` on every subsequent attempt.
 *
 * It is seeded rather than reproduced because reproducing it needs a click in
 * the backend module, and this environment has no web server. A developer
 * handed this ticket receives exactly this: a database in a broken state and a
 * report that saving does nothing.
 *
 * The schema is the extension's own ext_tables.sql at the pinned commit; the
 * values are the ones the report names.
 */

// 127.0.0.1, not the service name: under egress control every service shares
// the sidecar's network namespace, so there is no `db` to resolve. See the
// DB_HOST comment in task.toml.
$host = getenv('DB_HOST') ?: '127.0.0.1';
$user = getenv('DB_USER') ?: 'typo3';
$password = getenv('DB_PASSWORD') ?: '';
$database = getenv('DB_NAME') ?: 'typo3';

$db = new mysqli($host, $user, $password, $database);
if ($db->connect_errno !== 0) {
    fwrite(STDERR, "seed: cannot connect: {$db->connect_error}\n");
    exit(1);
}
$db->set_charset('utf8mb4');

$now = time();

function statement(mysqli $db, string $sql, string $types, mixed ...$values): int
{
    $statement = $db->prepare($sql);
    if ($statement === false) {
        fwrite(STDERR, "seed: prepare failed: {$db->error}\n  {$sql}\n");
        exit(1);
    }
    $statement->bind_param($types, ...$values);
    if (!$statement->execute()) {
        fwrite(STDERR, "seed: execute failed: {$statement->error}\n  {$sql}\n");
        exit(1);
    }

    return (int) $db->insert_id;
}

// A storage folder for the records. The report names storage pid 64; the
// number itself carries no meaning, only that the records live on a page.
$storagePid = statement(
    $db,
    "INSERT INTO pages (pid, tstamp, crdate, deleted, hidden, doktype, title, slug)
     VALUES (0, ?, ?, 0, 0, 254, 'TextDB storage', '/textdb-storage')",
    'ii',
    $now,
    $now
);

$environmentUid = statement(
    $db,
    "INSERT INTO tx_nrtextdb_domain_model_environment (pid, tstamp, crdate, deleted, hidden, name)
     VALUES (?, ?, ?, 0, 0, 'default')",
    'iii',
    $storagePid,
    $now,
    $now
);

$componentUid = statement(
    $db,
    "INSERT INTO tx_nrtextdb_domain_model_component (pid, tstamp, crdate, deleted, hidden, name)
     VALUES (?, ?, ?, 0, 0, 'template')",
    'iii',
    $storagePid,
    $now,
    $now
);

$typeUid = statement(
    $db,
    "INSERT INTO tx_nrtextdb_domain_model_type (pid, tstamp, crdate, deleted, hidden, name)
     VALUES (?, ?, ?, 0, 0, 'Email')",
    'iii',
    $storagePid,
    $now,
    $now
);

$placeholder = 'SYSTEM_MAIL_FOOTER_HTML_MFAG';

// The record the editor is trying to change. Its value is the old one, because
// the save did not take.
statement(
    $db,
    "INSERT INTO tx_nrtextdb_domain_model_translation
        (pid, tstamp, crdate, sys_language_uid, deleted, hidden, environment, component, type, placeholder, value)
     VALUES (?, ?, ?, 0, 0, 0, ?, ?, ?, ?, 'Mit freundlichen Gruessen<br>Ihr Team')",
    'iiiiiis',
    $storagePid,
    $now,
    $now,
    $environmentUid,
    $componentUid,
    $typeUid,
    $placeholder
);

// What the failed save left behind: same placeholder, same page, but with the
// three foreign keys unresolved. The unique key `translation` covers
// (sys_language_uid, pid, environment, component, type, placeholder, deleted),
// so this row does not collide with the one above — and every further save
// attempt collides with *it*.
statement(
    $db,
    "INSERT INTO tx_nrtextdb_domain_model_translation
        (pid, tstamp, crdate, sys_language_uid, deleted, hidden, environment, component, type, placeholder, value)
     VALUES (?, ?, ?, 0, 0, 0, 0, 0, 0, ?, 'Mit freundlichen Gruessen<br>Ihr Team (neu)')",
    'iiis',
    $storagePid,
    $now,
    $now,
    $placeholder
);

printf(
    "seeded: storage pid %d, environment %d, component %d, type %d, placeholder %s\n",
    $storagePid,
    $environmentUid,
    $componentUid,
    $typeUid,
    $placeholder
);
