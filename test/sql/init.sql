-- $Id: init.sql,v 1.9 2003/10/16 17:59:38 wrobell Exp $

create sequence order_seq;
create table "order" (
    __key__      integer,
-- --     __key__      integer default nextval('order_seq'),
    no           integer not null unique,
    finished     boolean not null,
    created      timestamp not null default current_timestamp,
    primary key (__key__)
);

create sequence employee_seq;
create table employee (
    __key__      integer,
-- --     __key__      integer default nextval('employee_seq'),
    name         varchar(10) not null,
    surname      varchar(20) not null,
    phone        varchar(12) not null,
    unique (name, surname),
    primary key (__key__)
);

create sequence article_seq;
create table article (
    __key__      integer,
-- --     __key__      integer default nextval('article_seq'),
    name         varchar(20) not null,
    price        numeric(10,2) not null,
    unique (name),
    primary key (__key__)
);

create sequence order_item_seq;
create table order_item (
    __key__      integer,
-- --     __key__      integer default nextval('order_item_seq'),
    order_fkey   integer,
    pos          integer not null,
    article_fkey integer not null,
    quantity     numeric(10,3) not null,
    primary key (__key__),
    unique (order_fkey, pos),
    foreign key (order_fkey) references "order"(__key__),
    foreign key (article_fkey) references article(__key__)
);

create table employee_orders (
    employee         integer,
    "order"          integer,
    primary key (employee, "order"),
    foreign key (employee) references employee(__key__),
    foreign key ("order") references "order"(__key__)
);

create sequence boss_seq;
create table boss (
    __key__     integer,
-- --     __key__     integer default nextval('boss_seq'),
    dep_fkey     integer,
    primary key (__key__)
--  see below
--    foreign key (dep_fkey) references department(__key__) initially deferred
);


create sequence department_seq;
create table department (
    __key__     integer,
-- --     __key__     integer default nextval('department_seq'),
    boss_fkey    integer,
    primary key (__key__),
    foreign key (boss_fkey) references boss(__key__) initially deferred
);

alter table boss add foreign key (dep_fkey) references department(__key__) initially deferred;
