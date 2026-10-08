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


define('JPATH_COMPONENT', JPATH_ADMINISTRATOR . '/components/com_menus');
define('JPATH_COMPONENT_ADMINISTRATOR', JPATH_ADMINISTRATOR . '/components/com_menus');
define('JPATH_COMPONENT_SITE', JPATH_SITE . '/components/com_menus');
$app->getLanguage()->load('com_menus', JPATH_ADMINISTRATOR);
$catId = (int) $db->setQuery("SELECT id FROM #__categories WHERE alias='ekonomika' AND extension='com_content'")->loadResult();
$m = model('com_menus', 'Item');
$comContentId = (int) $db->setQuery("SELECT extension_id FROM #__extensions WHERE element='com_content' AND type='component'")->loadResult();
must($m->save(['id' => 0, 'title' => 'Экономика', 'alias' => 'ekonomika', 'menutype' => 'mainmenu', 'type' => 'component',
    'link' => 'index.php?option=com_content&view=category&layout=blog&id=' . $catId, 'component_id' => $comContentId,
    'published' => 1, 'parent_id' => 1, 'level' => 1, 'access' => 1, 'language' => '*', 'client_id' => 0,
    'params' => ['show_description' => 1, 'num_leading_articles' => 1, 'num_intro_articles' => 6, 'show_pagination' => 2]]), $m, 'пункт меню Экономика');
echo "menu id: " . $m->getState('item.id') . "\n";
