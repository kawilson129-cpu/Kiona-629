-- ============================================================================
-- DeRexi Week 7 — Internal Messaging & Supabase Auth
-- ROLLBACK  (PROPOSED — DO NOT APPLY WITHOUT APPROVAL)
--
-- Exact reversal of week7_messaging_auth_migration.sql.
-- Because the forward migration is additive and does not rewrite existing
-- policy/message data, this rollback is lossless for pre-existing records.
-- It DOES drop data introduced by Week 7 (read receipts, notifications,
-- auth_user_id links, thread subject/kind/last_activity_at values — the
-- backfill is inherently reversed by dropping the last_activity_at column).
-- It also restores the two permissive SELECT policies that the forward
-- migration replaced on the thread tables (verbatim original definitions).
-- ============================================================================

begin;

-- ----------------------------------------------------------------------------
-- RLS policies (restore previous posture = RLS enabled, Week 7 policies gone)
-- ----------------------------------------------------------------------------
drop policy if exists clarification_replies_insert_participant on public.clarification_replies;
drop policy if exists clarification_replies_select_participant on public.clarification_replies;

drop policy if exists clarification_requests_update_participant on public.clarification_requests;
drop policy if exists clarification_requests_insert_self on public.clarification_requests;
drop policy if exists clarification_requests_select_participant on public.clarification_requests;

drop policy if exists internal_notifications_update_self on public.internal_notifications;
drop policy if exists internal_notifications_select_self on public.internal_notifications;

drop policy if exists message_reads_insert_self on public.message_reads;
drop policy if exists message_reads_select_self on public.message_reads;

-- Restore the original permissive SELECT policies that the forward migration
-- replaced (recreate verbatim to return to the exact prior posture).
create policy clarification_requests_select_authenticated on public.clarification_requests
    for select to authenticated using (true);
create policy clarification_replies_select_authenticated on public.clarification_replies
    for select to authenticated using (true);

-- ----------------------------------------------------------------------------
-- New tables
-- ----------------------------------------------------------------------------
drop table if exists public.internal_notifications;
drop table if exists public.message_reads;

-- ----------------------------------------------------------------------------
-- Auth helper
-- ----------------------------------------------------------------------------
drop function if exists public.current_user_id();

-- ----------------------------------------------------------------------------
-- clarification_requests extensions
-- ----------------------------------------------------------------------------
drop index if exists public.clarification_requests_last_activity_idx;
drop index if exists public.clarification_requests_kind_idx;

alter table public.clarification_requests
    drop constraint if exists clarification_requests_kind_check;

alter table public.clarification_requests
    drop column if exists last_activity_at,
    drop column if exists subject,
    drop column if exists kind;

-- ----------------------------------------------------------------------------
-- users.auth_user_id
-- ----------------------------------------------------------------------------
alter table public.users
    drop column if exists auth_user_id;

commit;

-- ============================================================================
-- Note: dropping users.auth_user_id discards the Auth<->business-user mapping.
-- Re-link users before re-enabling JWT-guarded endpoints after a rollback.
-- ============================================================================
