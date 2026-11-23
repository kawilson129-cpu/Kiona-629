-- DOCUMENTED ONLY: verbatim existing Week 7 CREATE TABLE, lines 19-26.
-- Already-created table confirmed in the live catalog. DO NOT execute on live Supabase.
CREATE TABLE IF NOT EXISTS public.clarification_reads (
    request_id   bigint NOT NULL
                 REFERENCES public.clarification_requests(id) ON DELETE CASCADE,
    user_id      bigint NOT NULL
                 REFERENCES public.users(id) ON DELETE CASCADE,
    last_read_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (request_id, user_id)
);
