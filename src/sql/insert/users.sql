-- sqlfluff:dialect:postgres
INSERT INTO public.users (first_name, last_name, gender, email, country, address, ip_address, phone_number) VALUES
    (:first_name, :last_name, :gender, :email, :country, :address, :ip_address, :phone_number);
