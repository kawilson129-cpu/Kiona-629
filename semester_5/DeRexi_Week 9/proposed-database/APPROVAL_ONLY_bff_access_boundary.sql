-- PROPOSAL ONLY. NOT EXECUTED. Requires explicit approval and privilege snapshot.
-- This application's browser uses FastAPI, not the Supabase Data API.
-- Denies direct Data API access to business tables and business identity RPCs.
-- PostgreSQL backend/owner access is unchanged; no records are edited/deleted.
-- Apply AFTER any separately approved Week 8 schema setup, before live onboarding.
-- This intentionally disables future direct-client integrations: approve that scope.
BEGIN;
DO $$
DECLARE object_name text; business_function regprocedure;
BEGIN
  FOREACH object_name IN ARRAY ARRAY[
    'departments','roles','users','policy_categories','policies','policy_versions',
    'conversations','messages','policy_citations','clarification_requests',
    'clarification_replies','clarification_reads','incident_categories',
    'incident_reports','feedback','governance_drafts','governance_events'
  ] LOOP
    IF to_regclass(format('public.%I',object_name)) IS NOT NULL THEN
      EXECUTE format('REVOKE ALL PRIVILEGES ON TABLE public.%I FROM PUBLIC, anon, authenticated',object_name);
    END IF;
  END LOOP;
  FOR business_function IN
    SELECT p.oid::regprocedure FROM pg_proc p JOIN pg_namespace n ON n.oid=p.pronamespace
    WHERE n.nspname='public' AND p.proname IN
      ('current_app_user_id','current_app_role','can_access_clarification',
       'can_access_conversation','can_access_message')
  LOOP
    EXECUTE format('REVOKE EXECUTE ON FUNCTION %s FROM PUBLIC, anon, authenticated',business_function);
  END LOOP;
END $$;
-- First trial: ROLLBACK. A real COMMIT requires separate approval after review.
ROLLBACK;
