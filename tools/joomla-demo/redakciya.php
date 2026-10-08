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

/* 1. Включить процессы публикации в настройках материалов */
$ext = $db->setQuery("SELECT extension_id, params FROM #__extensions WHERE element='com_content' AND type='component'")->loadObject();
$params = json_decode($ext->params ?: '{}', true) ?: [];
$params['workflow_enabled'] = '1';
$db->setQuery("UPDATE #__extensions SET params=" . $db->quote(json_encode($params)) . " WHERE extension_id=" . (int) $ext->extension_id)->execute();
echo "ok  workflow_enabled=1\n";

/* 2. Группы — детьми Registered (id 2) */
$groups = [];
foreach (['reporter' => 'Репортёр', 'editor' => 'Редактор отдела', 'proof' => 'Корректор', 'chief' => 'Главред'] as $k => $title) {
    $m = model('com_users', 'Group');
    must($m->save(['id' => 0, 'title' => $title, 'parent_id' => 2]), $m, "группа $title");
    $groups[$k] = (int) $m->getState('group.id');
}

/* 3. Уровень доступа «Редакция» — видят все четыре группы */
$m = model('com_users', 'Level');
must($m->save(['id' => 0, 'title' => 'Редакция', 'rules' => array_values($groups)]), $m, 'уровень доступа Редакция');
$levelId = (int) $m->getState('level.id');
// добавить группы и в Special (id 3), чтобы видеть неопубликованное с лицевой стороны
$m = model('com_users', 'Level');
$special = $m->getItem(3);
$specialRules = array_values(array_unique(array_merge((array) $special->rules, array_values($groups))));
must($m->save(['id' => 3, 'title' => $special->title, 'rules' => $specialRules]), $m, 'Special расширен');

/* 4. Пользователи */
$users = [];
$people = [
    'reporter' => ['Айгерим Серикова', 'aigerim', 'aigerim@example.kz'],
    'editor'   => ['Тимур Жаксыбеков', 'timur', 'timur@example.kz'],
    'proof'    => ['Лариса Коваль', 'larisa', 'larisa@example.kz'],
    'chief'    => ['Бекзат Нурланов', 'bekzat', 'bekzat@example.kz'],
];
foreach ($people as $k => [$name, $login, $mail]) {
    $m = model('com_users', 'User');
    must($m->save(['id' => 0, 'name' => $name, 'username' => $login, 'email' => $mail,
        'password' => 'Demo-2026!', 'password2' => 'Demo-2026!', 'groups' => [$groups[$k]],
        'block' => 0, 'sendEmail' => 0, 'requireReset' => 0, 'params' => ['language' => 'ru-RU', 'admin_language' => 'ru-RU']]), $m, "пользователь $name");
    $users[$k] = (int) $m->getState('user.id');
}

/* 5. Процесс публикации «Новости» */
$m = model('com_workflow', 'Workflow');
must($m->save(['id' => 0, 'title' => 'Новости', 'description' => 'Репортёр → редактор отдела → корректор → (главред) → публикация',
    'extension' => 'com_content.article', 'published' => 1, 'default' => 0]), $m, 'процесс Новости');
$wf = (int) $m->getState('workflow.id');

$stages = [];
foreach ([['draft', 'Черновик', 1], ['edit', 'На редактуре', 0], ['proof', 'На корректуре', 0], ['approve', 'На утверждении', 0], ['pub', 'Опубликовано', 0]] as [$k, $title, $def]) {
    $m = model('com_workflow', 'Stage');
    must($m->save(['id' => 0, 'title' => $title, 'workflow_id' => $wf, 'published' => 1, 'default' => $def, 'description' => '']), $m, "стадия $title");
    $stages[$k] = (int) $m->getState('stage.id');
}

$G = $groups;
$allow = function (array $yes) use ($G) {
    $r = [];
    foreach ($G as $k => $gid) { $r[(string) $gid] = in_array($k, $yes, true) ? 1 : 0; }
    return ['core.execute.transition' => $r];
};
$transitions = [
    ['Отправить на редактуру', 'draft', 'edit', ['reporter', 'editor', 'chief'], '', '', 'editor', 'Новый материал ждёт редактора отдела.'],
    ['Вернуть автору', 'edit', 'draft', ['editor', 'chief'], '', '', 'reporter', 'Редактор вернул материал на доработку.'],
    ['На корректуру', 'edit', 'proof', ['editor', 'chief'], '', '', 'proof', 'Материал отредактирован и ждёт корректуры.'],
    ['Вернуть редактору', 'proof', 'edit', ['proof', 'chief'], '', '', 'editor', 'Корректор вернул материал редактору.'],
    ['Опубликовать', 'proof', 'pub', ['editor', 'chief'], '1', '', 'reporter', 'Материал опубликован.'],
    ['На утверждение главреду', 'proof', 'approve', ['editor', 'chief'], '', '', 'chief', 'Материал особой важности ждёт решения главного редактора.'],
    ['Вернуть в отдел', 'approve', 'edit', ['chief'], '', '', 'editor', 'Главред вернул материал в отдел.'],
    ['Утвердить и опубликовать', 'approve', 'pub', ['chief'], '1', '1', 'editor', 'Главред утвердил материал; он опубликован и поставлен в избранное.'],
    ['Снять с публикации', 'pub', 'edit', ['chief'], '0', '0', 'editor', 'Материал снят с публикации.'],
];
$trIds = [];
foreach ($transitions as [$title, $from, $to, $roles, $publishing, $featuring, $notifyGroup, $text]) {
    $m = model('com_workflow', 'Transition');
    must($m->save(['id' => 0, 'title' => $title, 'workflow_id' => $wf, 'from_stage_id' => $stages[$from], 'to_stage_id' => $stages[$to],
        'published' => 1, 'description' => '',
        'options' => ['publishing' => $publishing, 'featuring' => $featuring, 'notification_send_mail' => '1',
            'notification_text' => $text, 'notification_groups' => [(string) $groups[$notifyGroup]], 'notification_receivers' => []],
        'rules' => $allow($roles)]), $m, "переход $title");
    $trIds[$title] = (int) $m->getState('transition.id');
}

/* 6. Категория-отдел «Экономика» с этим процессом */
$m = model('com_categories', 'Category');
$m->setState('category.extension', 'com_content');
must($m->save(['id' => 0, 'title' => 'Экономика', 'alias' => 'ekonomika', 'extension' => 'com_content', 'published' => 1, 'parent_id' => 1,
    'access' => 1, 'language' => '*', 'description' => '<p>Отдел экономики.</p>', 'params' => ['workflow_id' => $wf]]), $m, 'категория Экономика');
$catId = (int) $m->getState('category.id');

/* 7. Права: вход в админку, доступ к компонентам, действия в категории */
setRules('root.1', ['core.login.admin' => array_fill_keys(array_values($G), 1)]);
setRules('com_content', ['core.manage' => array_fill_keys(array_values($G), 1)]);
setRules('com_media',   ['core.manage' => [$G['proof'] => 1, $G['editor'] => 1, $G['chief'] => 1], 'core.create' => [$G['proof'] => 1, $G['editor'] => 1, $G['chief'] => 1]]);
setRules('com_categories', ['core.manage' => [$G['editor'] => 1, $G['chief'] => 1]]);
setRules('com_tags', ['core.manage' => [$G['editor'] => 1, $G['chief'] => 1], 'core.create' => [$G['editor'] => 1, $G['chief'] => 1], 'core.edit' => [$G['editor'] => 1, $G['chief'] => 1]]);
setRules('com_content.category.' . $catId, [
    'core.create'     => [$G['reporter'] => 1, $G['editor'] => 1, $G['chief'] => 1],
    'core.edit'       => [$G['editor'] => 1, $G['proof'] => 1, $G['chief'] => 1],
    'core.edit.own'   => [$G['reporter'] => 1],
    'core.edit.state' => [$G['editor'] => 1, $G['chief'] => 1],
    'core.delete'     => [$G['chief'] => 1],
    'core.execute.transition' => [$G['reporter'] => 1, $G['editor'] => 1, $G['proof'] => 1, $G['chief'] => 1],
]);

/* 8. Материалы в разных стадиях */
$texts = [
    ['Биржа открылась ростом: индекс прибавил 1,4 %', 'Торги на Казахстанской фондовой бирже открылись ростом: индекс основных бумаг прибавил 1,4 % на фоне укрепления тенге.', 'reporter', []],
    ['Банки переходят на мгновенные переводы по QR', 'Банки второго уровня тестируют переводы между клиентами разных банков по единому QR-коду.', 'reporter', ['Отправить на редактуру']],
    ['Как устроен тариф на электроэнергию: разбор', 'Разбираем, из чего складывается тариф для домохозяйств и почему он отличается по регионам.', 'reporter', ['Отправить на редактуру', 'На корректуру']],
    ['Нефтяники пересмотрели прогноз добычи на год', 'Крупнейшие недропользователи скорректировали план добычи после ремонтов на месторождениях.', 'reporter', ['Отправить на редактуру', 'На корректуру', 'На утверждение главреду']],
];
foreach ($texts as [$title, $body, $author, $path]) {
    $m = model('com_content', 'Article');
    $data = ['id' => 0, 'title' => $title, 'alias' => '', 'catid' => $catId, 'introtext' => "<p>$body</p>", 'fulltext' => '', 'state' => 0, 'access' => 1,
        'language' => '*', 'created_by' => $users[$author], 'created_by_alias' => '', 'featured' => 0, 'metadata' => [], 'images' => [], 'urls' => [], 'attribs' => [], 'metadesc' => '', 'metakey' => '', 'note' => ''];
    must($m->save($data), $m, "материал $title");
    $id = (int) $m->getState('article.id');
    foreach ($path as $tr) {
        $m2 = model('com_content', 'Article');
        $pk = [$id];
        $ok = $m2->executeTransition($pk, $trIds[$tr]);
        must($ok, $m2, "  переход «$tr» для #$id");
    }
}

/* 9. Пункт меню «Экономика» — блог категории; уровень Public */
$m = model('com_menus', 'Item');
$comContentId = (int) $db->setQuery("SELECT extension_id FROM #__extensions WHERE element='com_content' AND type='component'")->loadResult();
must($m->save(['id' => 0, 'title' => 'Экономика', 'alias' => 'ekonomika', 'menutype' => 'mainmenu', 'type' => 'component',
    'link' => 'index.php?option=com_content&view=category&layout=blog&id=' . $catId, 'component_id' => $comContentId,
    'published' => 1, 'parent_id' => 1, 'level' => 1, 'access' => 1, 'language' => '*', 'client_id' => 0,
    'params' => ['show_description' => 1, 'num_leading_articles' => 1, 'num_intro_articles' => 6, 'show_pagination' => 2]]), $m, 'пункт меню Экономика');

echo "\nГруппы: " . json_encode($groups) . "\nПользователи: " . json_encode($users) . "\nПроцесс: $wf, стадии: " . json_encode($stages) . "\nКатегория: $catId\n";
