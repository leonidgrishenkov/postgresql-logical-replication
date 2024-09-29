create table public.users (
	id int generated always as identity not null,
	first_name VARCHAR(50),
	last_name VARCHAR(50),
	email VARCHAR(50),
	gender VARCHAR(50),
	ip_address VARCHAR(20),

    constraint users_pk primary key (id)
);
