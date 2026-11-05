-- Rollback for 2026-11-05_week7_messaging.sql
-- Restores the pre-Week-7 permissive authenticated SELECT policies and removes
-- the read-watermark table. Run only if you need to revert the migration.

DROP POLICY IF EXISTS clarification_requests_select_scoped ON public.clarification_requests;
CREATE POLICY clarification_requests_select_authenticated
    ON public.clarification_requests FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS clarification_replies_select_scoped ON public.clarification_replies;
CREATE POLICY clarification_replies_select_authenticated
    ON public.clarification_replies FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS conversations_select_scoped ON public.conversations;
CREATE POLICY conversations_select_authenticated
    ON public.conversations FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS messages_select_scoped ON public.messages;
CREATE POLICY messages_select_authenticated
    ON public.messages FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS policy_citations_select_scoped ON public.policy_citations;
CREATE POLICY policy_citations_select_authenticated
    ON public.policy_citations FOR SELECT TO authenticated USING (true);

DROP POLICY IF EXISTS feedback_select_scoped ON public.feedback;
CREATE POLICY feedback_select_authenticated
    ON public.feedback FOR SELECT TO authenticated USING (true);

DROP TABLE IF EXISTS public.clarification_reads;

DROP FUNCTION IF EXISTS public.can_access_message(bigint);
DROP FUNCTION IF EXISTS public.can_access_conversation(bigint);
DROP FUNCTION IF EXISTS public.can_access_clarification(bigint);
DROP FUNCTION IF EXISTS public.current_app_role();
DROP FUNCTION IF EXISTS public.current_app_user_id();

DROP INDEX IF EXISTS public.idx_clarification_requests_assignee_status;
DROP INDEX IF EXISTS public.idx_clarification_requests_requester;
DROP INDEX IF EXISTS public.idx_clarification_requests_triage;
DROP INDEX IF EXISTS public.idx_clarification_replies_thread;
