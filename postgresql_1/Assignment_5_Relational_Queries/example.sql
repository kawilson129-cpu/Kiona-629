-- VERIFIED live JOIN; no personal names/emails are selected.
BEGIN READ ONLY;
SELECT d.name AS department, r.name AS role, count(u.id) AS user_count
FROM public.users AS u
JOIN public.departments AS d ON d.id = u.department_id
JOIN public.roles AS r ON r.id = u.role_id
GROUP BY d.name, r.name
ORDER BY d.name ASC, r.name ASC;
ROLLBACK;
