create database if not exists dovecot;
grant all on dovecot.* to 'dovecot'@'%' identified by 'toto';
create database if not exists postfix;
grant all on postfix.* to 'postfix'@'%' identified by 'toto';
