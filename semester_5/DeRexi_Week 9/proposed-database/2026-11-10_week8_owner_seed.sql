-- APPROVAL REQUIRED. Run schema migration first. Fictional application profiles only; NO Auth users.
-- The advisory lock and table lock serialize this idempotent seed against concurrent runs.
BEGIN;
SELECT pg_advisory_xact_lock(820261110);
LOCK TABLE public.users IN SHARE ROW EXCLUSIVE MODE;
DO $$
DECLARE d record; c record; missing integer; owner_role bigint;
BEGIN
 SELECT id INTO STRICT owner_role FROM public.roles WHERE name='Policy Owner';
 FOR d IN SELECT id,name FROM public.departments ORDER BY id LOOP
  SELECT greatest(0,2-count(*)) INTO missing FROM public.users WHERE department_id=d.id AND role_id=owner_role;
  FOR c IN SELECT * FROM (VALUES
   ('Compliance','Avery','Morgan','avery.morgan@aurumbank.com','Compliance Policy Manager',1),
   ('Information Technology','Priya','Shah','priya.shah@aurumbank.com','IT Policy Manager',1),
   ('Operations','Noah','Reed','noah.reed@aurumbank.com','Operations Policy Manager',1),
   ('Human Resources','Taylor','Ellis','taylor.ellis@aurumbank.com','HR Policy Manager',1),
   ('Marketing','Morgan','Lee','morgan.lee@aurumbank.com','Marketing Compliance Manager',1),
   ('Marketing','Cameron','Davis','cameron.davis@aurumbank.com','Marketing Policy Manager',2),
   ('Lending','Sofia','Martinez','sofia.martinez@aurumbank.com','Lending Policy Manager',1),
   ('Wealth Management','Ethan','Clarke','ethan.clarke@aurumbank.com','Wealth Policy Manager',1)
  ) AS candidates(department,first_name,last_name,email,job_title,priority)
  WHERE department=d.name ORDER BY priority LOOP
   EXIT WHEN missing <= 0;
   -- Existing matching fictional profiles are never overwritten or duplicated.
   IF NOT EXISTS (SELECT 1 FROM public.users u WHERE lower(u.email)=lower(c.email)
       OR (lower(u.first_name)=lower(c.first_name) AND lower(u.last_name)=lower(c.last_name))) THEN
    INSERT INTO public.users(first_name,last_name,email,department_id,role_id,job_title)
    VALUES(c.first_name,c.last_name,c.email,d.id,owner_role,c.job_title);
    missing := missing-1;
   END IF;
  END LOOP;
  IF missing > 0 THEN RAISE EXCEPTION 'Unfilled owner coverage in department %; review candidates/collisions', d.name; END IF;
 END LOOP;
END $$;
COMMIT;
-- Verify: every department must report >=2. Existing IDs/ownership must match preflight inventory.
SELECT d.name,count(u.id) FILTER(WHERE r.name='Policy Owner') AS owners
FROM public.departments d LEFT JOIN public.users u ON u.department_id=d.id
LEFT JOIN public.roles r ON r.id=u.role_id GROUP BY d.id,d.name ORDER BY d.id;
