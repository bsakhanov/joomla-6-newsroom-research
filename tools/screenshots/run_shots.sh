#!/bin/bash
# держим службы живыми перед каждой серией
pgrep mariadbd >/dev/null || (setsid nohup mariadbd --user=mysql --datadir=/var/lib/mysql --socket=/var/run/mysqld/mysqld.sock --port=3306 --bind-address=127.0.0.1 >/tmp/mariadb.log 2>&1 < /dev/null &); 
pgrep -f "php -S 127.0.0.1:8080" >/dev/null || (cd /var/www/j6 && setsid nohup php -S 127.0.0.1:8080 -t /var/www/j6 >/tmp/php-server.log 2>&1 < /dev/null &)
sleep 3
for r in "$@"; do
  mariadb -uroot joomla -e "UPDATE j_content SET checked_out=NULL, checked_out_time=NULL; UPDATE j_menu SET checked_out=NULL, checked_out_time=NULL" 2>&1 | head -1
  timeout 150 xvfb-run -a -s "-screen 0 1600x1000x24" python3 /tmp/shot.py /tmp/plan_$r.json 2>&1 | grep "^ok\|^ERR" | sed 's|/tmp/shots/||' | tr '\n' ' '
done
echo; pgrep -c mariadbd; pgrep -fc "php -S"
