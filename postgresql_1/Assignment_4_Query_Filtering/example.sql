-- VERIFIED live SELECT only; transaction rolled back.
BEGIN READ ONLY;
SELECT id, title, status FROM public.policies WHERE status = 'approved' ORDER BY title ASC, id ASC LIMIT 5;
ROLLBACK;
