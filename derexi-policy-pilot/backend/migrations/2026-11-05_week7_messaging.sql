-- ===========================================================================
-- DeRexi Week 7 — clarification messaging
-- Additive, idempotent. Safe to re-run.
--
-- 1. clarification_reads: per-user read watermark (drives unread counts).
-- 2. Indexes for the messaging read model.
-- 3. Row Level Security for direct Supabase clients.
--
-- The FastAPI backend connects as the Supabase `postgres` role, which has
-- BYPASSRLS. Authorization for the application therefore lives in
-- backend/security.py and backend/messaging.py. These policies are defence in
-- depth for any future client that talks to Supabase directly with a user JWT.
--
-- Identity bridge: Supabase JWT `email` claim -> public.users.email. No new
-- auth users and no schema change to users are required.
-- ===========================================================================

-- 1. Read watermark ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.clarification_reads (
    request_id   bigint NOT NULL
                 REFERENCES public.clarification_requests(id) ON DELETE CASCADE,
    user_id      bigint NOT NULL
                 REFERENCES public.users(id) ON DELETE CASCADE,
    last_read_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (request_id, user_id)
);

-- 2. Indexes ----------------------------------------------------------------
CREATE INDEX IF NOT EXISTS idx_clarification_requests_assignee_status
    ON public.clarification_requests (assigned_to, status, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_clarification_requests_requester
    ON public.clarification_requests (user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_clarification_requests_triage
    ON public.clarification_requests (assigned_to) WHERE assigned_to IS NULL;
CREATE INDEX IF NOT EXISTS idx_clarification_replies_thread
    ON public.clarification_replies (request_id, created_at, id);
CREATE INDEX IF NOT EXISTS idx_clarification_reads_user
    ON public.clarification_reads (user_id);

ALTER TABLE public.clarification_reads ENABLE ROW LEVEL SECURITY;

-- 3. Identity helpers -------------------------------------------------------
-- SECURITY DEFINER so the helper can read public.users / role names without
-- being blocked by the caller's RLS. search_path is pinned.
CREATE OR REPLACE FUNCTION public.current_app_user_id()
RETURNS bigint
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT u.id
    FROM public.users u
    WHERE lower(u.email) = lower(coalesce(auth.jwt() ->> 'email', ''))
    LIMIT 1
$$;

CREATE OR REPLACE FUNCTION public.current_app_role()
RETURNS text
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT r.name
    FROM public.users u
    JOIN public.roles r ON r.id = u.role_id
    WHERE u.id = public.current_app_user_id()
$$;

CREATE OR REPLACE FUNCTION public.can_access_clarification(p_id bigint)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.clarification_requests cr
        WHERE cr.id = p_id
          AND (
              public.current_app_role() = 'System Administrator'
              OR cr.user_id = public.current_app_user_id()
              OR cr.assigned_to = public.current_app_user_id()
              OR EXISTS (
                  SELECT 1
                  FROM public.clarification_replies r
                  WHERE r.request_id = cr.id
                    AND r.sender_id = public.current_app_user_id()
              )
          )
    )
$$;

CREATE OR REPLACE FUNCTION public.can_access_conversation(p_id bigint)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.conversations c
        WHERE c.id = p_id
          AND (
              public.current_app_role() = 'System Administrator'
              OR c.user_id = public.current_app_user_id()
              OR EXISTS (
                  SELECT 1
                  FROM public.clarification_requests cr
                  WHERE cr.conversation_id = c.id
                    AND public.can_access_clarification(cr.id)
              )
          )
    )
$$;

CREATE OR REPLACE FUNCTION public.can_access_message(p_id bigint)
RETURNS boolean
LANGUAGE sql
STABLE
SECURITY DEFINER
SET search_path = public, pg_temp
AS $$
    SELECT EXISTS (
        SELECT 1
        FROM public.messages m
        WHERE m.id = p_id
          AND public.can_access_conversation(m.conversation_id)
    )
$$;

REVOKE ALL ON FUNCTION public.current_app_user_id() FROM public;
REVOKE ALL ON FUNCTION public.current_app_role() FROM public;
REVOKE ALL ON FUNCTION public.can_access_clarification(bigint) FROM public;
REVOKE ALL ON FUNCTION public.can_access_conversation(bigint) FROM public;
REVOKE ALL ON FUNCTION public.can_access_message(bigint) FROM public;
GRANT EXECUTE ON FUNCTION public.current_app_user_id() TO authenticated;
GRANT EXECUTE ON FUNCTION public.current_app_role() TO authenticated;
GRANT EXECUTE ON FUNCTION public.can_access_clarification(bigint) TO authenticated;
GRANT EXECUTE ON FUNCTION public.can_access_conversation(bigint) TO authenticated;
GRANT EXECUTE ON FUNCTION public.can_access_message(bigint) TO authenticated;

-- 4. Scoped read policies ---------------------------------------------------
DROP POLICY IF EXISTS clarification_requests_select_authenticated
    ON public.clarification_requests;
DROP POLICY IF EXISTS clarification_requests_select_scoped
    ON public.clarification_requests;
CREATE POLICY clarification_requests_select_scoped
    ON public.clarification_requests
    FOR SELECT TO authenticated
    USING (public.can_access_clarification(id));

DROP POLICY IF EXISTS clarification_replies_select_authenticated
    ON public.clarification_replies;
DROP POLICY IF EXISTS clarification_replies_select_scoped
    ON public.clarification_replies;
CREATE POLICY clarification_replies_select_scoped
    ON public.clarification_replies
    FOR SELECT TO authenticated
    USING (public.can_access_clarification(request_id));

DROP POLICY IF EXISTS conversations_select_authenticated
    ON public.conversations;
DROP POLICY IF EXISTS conversations_select_scoped
    ON public.conversations;
CREATE POLICY conversations_select_scoped
    ON public.conversations
    FOR SELECT TO authenticated
    USING (public.can_access_conversation(id));

DROP POLICY IF EXISTS messages_select_authenticated
    ON public.messages;
DROP POLICY IF EXISTS messages_select_scoped
    ON public.messages;
CREATE POLICY messages_select_scoped
    ON public.messages
    FOR SELECT TO authenticated
    USING (public.can_access_message(id));

DROP POLICY IF EXISTS policy_citations_select_authenticated
    ON public.policy_citations;
DROP POLICY IF EXISTS policy_citations_select_scoped
    ON public.policy_citations;
CREATE POLICY policy_citations_select_scoped
    ON public.policy_citations
    FOR SELECT TO authenticated
    USING (public.can_access_message(message_id));

DROP POLICY IF EXISTS feedback_select_authenticated
    ON public.feedback;
DROP POLICY IF EXISTS feedback_select_scoped
    ON public.feedback;
CREATE POLICY feedback_select_scoped
    ON public.feedback
    FOR SELECT TO authenticated
    USING (
        public.current_app_role() = 'System Administrator'
        OR user_id = public.current_app_user_id()
    );

-- Read watermarks: a user may only see and write their own row.
DROP POLICY IF EXISTS clarification_reads_select_own
    ON public.clarification_reads;
CREATE POLICY clarification_reads_select_own
    ON public.clarification_reads
    FOR SELECT TO authenticated
    USING (user_id = public.current_app_user_id());

DROP POLICY IF EXISTS clarification_reads_insert_own
    ON public.clarification_reads;
CREATE POLICY clarification_reads_insert_own
    ON public.clarification_reads
    FOR INSERT TO authenticated
    WITH CHECK (
        user_id = public.current_app_user_id()
        AND public.can_access_clarification(request_id)
    );

DROP POLICY IF EXISTS clarification_reads_update_own
    ON public.clarification_reads;
CREATE POLICY clarification_reads_update_own
    ON public.clarification_reads
    FOR UPDATE TO authenticated
    USING (user_id = public.current_app_user_id())
    WITH CHECK (
        user_id = public.current_app_user_id()
        AND public.can_access_clarification(request_id)
    );
