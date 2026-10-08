import json
B='http://127.0.0.1:8080'
A=B+'/administrator/index.php'
WF,CAT,TPL,STYLE=2,8,245,245
OUT='/tmp/shots/'

def login(user,pwd):
    js=f"document.getElementById('mod-login-username').value='{user}';document.getElementById('mod-login-password').value='{pwd}';document.getElementById('form-login').submit();"
    return {'url':A,'js':js,'wait':2000,'wait_after_js':3500}
def tab(label):
    # активировать вкладку по подписи (Joomla 5/6: button[role=tab])
    return f"(function(){{var t=[...document.querySelectorAll('button[role=tab]')].find(b=>b.textContent.trim().includes('{label}'));if(t)t.click();window.scrollTo(0,0);}})();"
def page(url,out,js=None,wait=2200,full=True):
    d={'url':url,'out':OUT+out,'wait':wait,'full':full}
    if js:d['js']=js
    return d
def onpage(out,js,wait_js=1200,full=True):
    return {'js':js,'out':OUT+out,'wait_after_js':wait_js,'full':full}
def cancel(task):
    return {'js':f"Joomla.submitbutton('{task}.cancel')",'wait_after_js':2500}

plans={}
plans['admin']={'steps':[login('admin','Admin-Demo-2026!'),
  page(A+'?option=com_cpanel&view=cpanel','01-admin-dashboard.png',full=False),
  page(A+'?option=com_users&view=groups','02-groups.png'),
  page(A+'?option=com_users&view=levels','03-levels.png'),
  page(A+f'?option=com_workflow&view=workflows&extension=com_content.article','04-workflows.png'),
  page(A+f'?option=com_workflow&view=stages&workflow_id={WF}&extension=com_content.article','05-stages.png'),
  page(A+f'?option=com_workflow&view=transitions&workflow_id={WF}&extension=com_content.article','06-transitions.png'),
  page(A+f'?option=com_workflow&task=transition.edit&id=13&workflow_id={WF}&extension=com_content.article','07-transition-edit.png',full=False),
  onpage('08-transition-actions.png',tab('Действия'),full=False),
  onpage('09-transition-notify.png',tab('Письма'),full=False),
  onpage('10-transition-permissions.png',tab('Права'),full=False),
  cancel('transition'),
  page(A+f'?option=com_categories&task=category.edit&id={CAT}&extension=com_content','11-category-workflow.png',js=tab('роцесс'),full=False),
  cancel('category'),
  page(A+'?option=com_content&view=articles','12-articles-admin.png'),
  page(A+'?option=com_content&task=article.edit&id=5','13-article-edit-admin.png',full=False),
  onpage('13b-article-publishing-admin.png',tab('Публикац'),full=False),
  cancel('article'),
  page(A+'?option=com_config&view=component&component=com_content','14-content-options-integration.png',js=tab('Интеграци')+"window.scrollTo(0,0);",full=True),
  page(A+'?option=com_templates&view=templates&client_id=0','15-site-templates.png'),
  page(A+f'?option=com_templates&view=template&id={TPL}','16-template-child-button.png',full=False),
  page(A+'?option=com_templates&view=styles&client_id=0','17-template-styles.png'),
  page(A+'?option=com_menus&task=item.edit&id=102','18-menu-item-template-style.png',full=False),
  cancel('item'),
]}
plans['reporter']={'steps':[login('aigerim','Demo-2026!'),
  page(A+'?option=com_cpanel&view=cpanel','20-reporter-dashboard.png',full=False),
  page(A+'?option=com_content&view=articles','21-reporter-articles.png'),
  page(A+'?option=com_content&task=article.edit&id=2','22-reporter-edit.png',full=False),
  cancel('article')]}
plans['editor']={'steps':[login('timur','Demo-2026!'),
  page(A+'?option=com_cpanel&view=cpanel','30-editor-dashboard.png',full=False),
  page(A+'?option=com_content&view=articles','31-editor-articles.png'),
  page(A+'?option=com_content&task=article.edit&id=4','32-editor-edit.png',full=False),
  cancel('article')]}
plans['proof']={'steps':[login('larisa','Demo-2026!'),
  page(A+'?option=com_cpanel&view=cpanel','40-proof-dashboard.png',full=False),
  page(A+'?option=com_content&task=article.edit&id=4','41-proof-edit.png',full=False),
  cancel('article')]}
plans['chief']={'steps':[login('bekzat','Demo-2026!'),
  page(A+'?option=com_content&view=articles','50-chief-articles.png'),
  page(A+'?option=com_content&task=article.edit&id=5','51-chief-edit.png',full=False),
  cancel('article')]}
# лицевая сторона: вход редактора через модуль, блог категории, форма правки
fjs="(function(){var f=document.getElementById('login-form-16');f.querySelector('[name=username]').value='timur';f.querySelector('[name=password]').value='Demo-2026!';f.submit();})();"
plans['front']={'steps':[{'url':B+'/index.php/ekonomika','js':fjs,'wait':2200,'wait_after_js':3500},
  page(B+'/index.php/ekonomika','60-front-category-editor.png'),
  page(B+'/index.php/ekonomika?option=com_content&task=article.edit&a_id=4&return=aHR0cDovLzEyNy4wLjAuMTo4MDgwL2luZGV4LnBocC9la29ub21pa2E=','61-front-edit-publishing.png',js=tab('Публикац'),full=False),
]}
for k,v in plans.items():
    json.dump(v,open(f'/tmp/plan_{k}.json','w'),ensure_ascii=False)
print('plans:',list(plans))
