-- create database;
--create database apolo;

-- create account table;
create table if not exists account(
id serial8 primary key,
username text,
gmail text,
account_password text,
account_level int,
team text,
fullname text,
update_time timestamp default now());

-- insert admin username and password level 2;
insert into account(username,account_password,account_level) values('admin','b109f3bbbc244eb82441917ed06d618b9008dd09b3befd1b5e07394c706a8bb980b1d7785e5976ec049b46df5f1326af5a2ea6d103fd07c95385ffab0cacbc86',2);

-- create table first menu for admin only;
create table if not exists admin_first_menu(
id serial8 primary key,
fid int,
menu1 text,
link text,
update_time timestamp default now());
insert into admin_first_menu(fid,menu1,link) values(1,1,'test');
-- create table second menu for admin only;
create table if not exists admin_second_menu(
id serial8 primary key,
first_menu_id int,
menu2 text,
link text,
update_time timestamp default now());
insert into admin_second_menu(first_menu_id,menu2,link) values(0,'','test');

-- create table for user menu;
create table if not exists first_menu(
id serial8 primary key,
fid int,
menu1 text,
link text,
update_time timestamp default now());
insert into first_menu(fid,menu1,link) values(1,1,'test');
-- create table second menu user;

create table if not exists second_menu(
id serial8 primary key,
first_menu_id int,
menu2 text,
link text,
update_time timestamp default now());
insert into second_menu(first_menu_id,menu2,link) values(0,'test','test');
--create table user_report;

create table if not exists user_report(
id serial8 primary key,
agent text,
gmail text,
update_time timestamp default now());
insert into user_report(agent) values('test');
--create querysql table
create table if not exists querysql
(id serial8 primary key,
dowhat text,
querysql text,
detail text,
update_time timestamp default now());
insert into querysql(dowhat) values('test');

--create table list
create table if not exists most_used_table(
id serial8 primary key,
tablename text,
sqlcreated text,
update_time timestamp default now());
insert into most_used_table(tablename) values('test');

--create table settings
create table if not exists settings(
id serial8 unique primary key,
tablename text,
dowhat text,
query text,
sqlcraeted text,
detail text,
update_time timestamp default now());
insert into settings(tablename) values('test');

create table if not exists service_manager (
id serial8 primary key,
file text,
service text,
note text,
update_time timestamp default now());


