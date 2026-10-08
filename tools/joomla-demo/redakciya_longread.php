<?php
/**
 * redakciya.php — моделирует редакционный конвейер на чистой Joomla 6
 * теми же моделями, которыми пользуется админка (com_users, com_workflow,
 * com_categories, com_content, com_menus). Запуск: php cli/redakciya.php
 */
const _JEXEC = 1;
define('JPATH_BASE', dirname(__DIR__));
require_once JPATH_BASE . '/includes/defines.php';
require_once JPATH_BASE . '/includes/framework.php';
require_once JPATH_LIBRARIES . '/namespacemap.php';
$nsMap = new JNamespacePsr4Map(); $nsMap->ensureMapFileExists(); $nsMap->load();

use Joomla\CMS\Factory;
use Joomla\CMS\Application\ConsoleApplication;
use Joomla\CMS\Table\Asset;
use Joomla\CMS\User\UserFactoryInterface;

$container = Factory::getContainer();
$container->alias('session', 'session.cli')
    ->alias('JSession', 'session.cli')
    ->alias(\Joomla\CMS\Session\Session::class, 'session.cli')
    ->alias(\Joomla\Session\Session::class, 'session.cli')
    ->alias(\Joomla\Session\SessionInterface::class, 'session.cli');
$app = $container->get(ConsoleApplication::class);
Factory::$application = $app;
$db  = Factory::getDbo();
$_SERVER['HTTP_HOST'] = 'localhost:8080';
$_SERVER['REQUEST_URI'] = '/';

$adminId = (int) $db->setQuery("SELECT id FROM #__users WHERE username='admin'")->loadResult();
$app->loadIdentity($container->get(UserFactoryInterface::class)->loadUserById($adminId));
$app->getLanguage()->load('com_users', JPATH_ADMINISTRATOR);

function model(string $component, string $name) {
    global $app;
    return $app->bootComponent($component)->getMVCFactory()->createModel($name, 'Administrator', ['ignore_request' => true]);
}
function must($ok, $model, string $what) {
    if (!$ok) { fwrite(STDERR, "FAIL $what: " . $model->getError() . "\n"); exit(1); }
    echo "ok  $what\n";
}
function setRules(string $assetName, array $rules): void {
    global $db;
    $asset = new Asset($db);
    if (!$asset->loadByName($assetName)) { fwrite(STDERR, "no asset $assetName\n"); exit(1); }
    $current = json_decode($asset->rules ?: '{}', true) ?: [];
    foreach ($rules as $action => $groups) {
        foreach ($groups as $gid => $val) { $current[$action][(string) $gid] = $val; }
    }
    $asset->rules = json_encode($current);
    if (!$asset->store()) { fwrite(STDERR, "asset store failed $assetName\n"); exit(1); }
    echo "ok  права: $assetName\n";
}


define('JPATH_COMPONENT', JPATH_ADMINISTRATOR . '/components/com_content');
define('JPATH_COMPONENT_ADMINISTRATOR', JPATH_ADMINISTRATOR . '/components/com_content');
define('JPATH_COMPONENT_SITE', JPATH_SITE . '/components/com_content');
$app->getLanguage()->load('com_content', JPATH_ADMINISTRATOR);
$catId = (int) $db->setQuery("SELECT id FROM #__categories WHERE alias='ekonomika' AND extension='com_content'")->loadResult();
$users = []; foreach ($db->setQuery("SELECT id, username FROM #__users")->loadObjectList() as $u) { $users[$u->username] = (int) $u->id; }
$trIds = []; foreach ($db->setQuery("SELECT id, title FROM #__workflow_transitions")->loadObjectList() as $t) { $trIds[$t->title] = (int) $t->id; }

$m = model('com_content', 'Article');
$html = '<p>Интерактивный лонгрид встроен в материал Joomla как есть — тот же файл, что открывается отдельно.</p><iframe src="/longread/index.html" title="Интерактивный лонгрид" style="width:100%;height:1400px;border:0;border-radius:6px"></iframe>';
must($m->save(['id' => 0, 'title' => 'Редакция в ядре: интерактивный лонгрид внутри сайта', 'alias' => 'longread', 'catid' => $catId, 'introtext' => $html, 'fulltext' => '', 'state' => 1, 'access' => 1,
    'language' => '*', 'created_by' => $users['bekzat'], 'created_by_alias' => '', 'featured' => 0, 'metadata' => [], 'images' => [], 'urls' => [], 'attribs' => ['show_title' => '1', 'show_author' => '0', 'show_category' => '0', 'show_publish_date' => '0', 'show_hits' => '0'], 'metadesc' => '', 'metakey' => '', 'note' => '']), $m, 'материал-лонгрид');
$aid = (int) $m->getState('article.id');
echo "article $aid\n";
