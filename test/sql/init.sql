-- $Id: init.sql,v 1.6 2003/09/24 18:18:44 wrobell Exp $

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


-- association keys testing

-- -- create schema keys;
-- -- 
-- -- create table bsingle (
-- --     __key__      serial,
-- --     b integer,
-- --     primary key(b)
-- -- );
-- -- 
-- -- create table bmulti (
-- --     __key__      serial,
-- --     b1 integer,
-- --     b2 integer,
-- --     b3 integer,
-- --     primary key(b1, b2, b3)
-- -- );
-- -- 
-- -- create table a (
-- --     __key__      serial,
-- --     a integer,
-- --     bs_fkey integer,
-- --     bm1 integer,
-- --     bm2 integer,
-- --     bm3 integer,
-- --     primary key (a),
-- --     foreign key (bs_fkey) references bsingle(b),
-- --     foreign key (bm1, bm2, bm3) references bmulti(b1, b2, b3)
-- -- );
