-- $Id: init.sql,v 1.7 2003/09/29 18:36:53 wrobell Exp $

create sequence order_seq;
create table "order" (
    __key__      integer,
    no           integer,
    finished     boolean not null,
    created      timestamp not null default current_timestamp,
    unique (no),
    primary key (__key__)
);

create sequence employee_seq;
create table employee (
    __key__      integer,
    name         varchar(10),
    surname      varchar(20),
    phone        varchar(12),
    unique (name, surname),
    primary key (__key__)
);

create sequence article_seq;
create table article (
    __key__      integer,
    name         varchar(20),
    price        numeric(10,2) not null,
    unique (name),
    primary key (__key__)
);

create sequence order_item_seq;
create table order_item (
    __key__      integer,
    order_fkey   integer,
    pos          integer,
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

create table boss (
    __key__     integer,
    dep_key     integer,
    primary key (__key__)
--  see below
--    foreign key (dep_key) references department(__key__) initially deferred
);


create table department (
    __key__     integer,
    boss_key    integer,
    primary key (__key__),
    foreign key (boss_key) references boss(__key__) initially deferred
);

alter table boss add foreign key (dep_key) references department(__key__) initially deferred;
