-- $Id: init.sql,v 1.3 2003/09/03 22:52:23 wrobell Exp $

create table "order" (
    no           integer,
    finished     boolean not null,
    created      timestamp not null default current_timestamp,
    primary key (no)
);

create table employee (
    name         varchar(10),
    surname      varchar(20),
    phone        varchar(12),
    primary key (name, surname)
);

create table article (
    name         varchar(20),
    price        numeric(10,2) not null,
    primary key (name)
);

create table order_item (
    "order"      integer,
    pos          integer,
    article_fkey varchar(20) not null,
    quantity     numeric(10,3) not null,
    primary key ("order", pos),
    foreign key ("order") references "order"(no),
    foreign key (article_fkey) references article(name)
);

create table employee_orders (
    employee_name    varchar(10),
    employee_surname varchar(20),
    "order"          integer,
    primary key (employee_name, employee_surname, "order"),
    foreign key (employee_name, employee_surname) references employee(name, surname),
    foreign key ("order") references "order"(no)
);
