-- sqlfluff:dialect:postgres
CREATE TABLE public.users (
	id BIGINT GENERATED ALWAYS AS IDENTITY NOT NULL PRIMARY KEY,
	first_name VARCHAR(100),
	last_name VARCHAR(100),
	gender VARCHAR(50),
	email VARCHAR(100),
	country VARCHAR(100),
	address VARCHAR(200),
	ip_address VARCHAR(20),
	phone_number VARCHAR(100)
);
