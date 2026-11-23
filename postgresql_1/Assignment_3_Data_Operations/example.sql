-- DOCUMENTED ONLY / NOT EXECUTED. Local disposable PostgreSQL database ONLY.
-- Requires an isolated copy of the verified public.departments table.
-- Never run this file against Supabase or the normal application database.
-- ROLLBACK is not a live-write safety guarantee: identity sequences can still advance.
BEGIN;
INSERT INTO public.departments (name)
VALUES ('Coursework Demo Department')
RETURNING id, name;
SELECT id, name FROM public.departments
WHERE name = 'Coursework Demo Department'
ORDER BY id;
ROLLBACK;
