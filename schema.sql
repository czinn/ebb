create table if not exists currencies (
  id integer primary key,
  code text not null,
  major not null,
  equivalent_usd real not null
);

create table if not exists accounts (
  id integer primary key,
  name text not null,
  currency_id integer not null,
  foreign key (currency_id) references currencies (id)
);

create table if not exists balances (
  id integer primary key,
  account_id integer not null,
  date text not null,
  amount integer not null,
  foreign key (account_id) references accounts (id)
);

create table if not exists categories (
  id integer primary key,
  name text not null,
  parent_id integer,
  default_amortization_type integer,
  default_amortization_length integer,
  foreign key (parent_id) references categories(id)
);

create table if not exists payees (
  id integer primary key,
  name text not null
);

create table if not exists transactions (
  id integer primary key
);

create table if not exists balance_deltas (
  id integer primary key,
  account_id integer not null,
  transaction_id integer not null,
  date text not null,
  amount integer not null,
  foreign key (account_id) references accounts(id),
  foreign key (transaction_id) references transactions(id)
);

create table if not exists flows (
  id integer primary key,
  transaction_id integer not null,
  category_id integer not null,
  payee_id integer not null,
  date text not null,
  description text not null,
  amount integer not null,
  amortization_type integer,
  amortization_length integer,
  foreign key (transaction_id) references transactions(id),
  foreign key (category_id) references categories(id)
);
