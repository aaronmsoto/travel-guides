# Backend options for juntar.net v0.2 (multi-user RSVP features)

Research memo. Today: 2026-09-23. Current v0.1: fully static, `tools/build.py` renders
`guides/<slug>/guide.json` into self-contained HTML, deployed by `.github/workflows/pages.yml` to
GitHub Pages at `juntar.net`; client is vanilla `shared/engine.js` (~250 lines, localStorage only,
no framework/bundler). Goal for v0.2: add passwordless auth, RSVPs, proxy RSVPs, event-scoped
visibility, messaging, and email/SMS notifications, without abandoning the declarative guide
pipeline. Scale: a few hosts, tens–low hundreds of users, a handful of events/year. Budget:
$0–$10/month. Maintainer: one person working mostly through AI coding agents.

## 1. Candidate stacks

| Stack | Hosting fit w/ GH Pages | Auth (email/SMS OTP) | AuthZ model | DB | Functions | Email/SMS | Free tier | First paid tier | Pause/inactivity | Lock-in | AI-agent fit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **Supabase** | Keep GH Pages; call `*.supabase.co` from a JS island | Email OTP/magic link built in & free; phone OTP via Twilio/MessageBird/Vonage (BYO account, billed by provider, not Supabase) [1] | Postgres **RLS** (SQL policies) | Postgres | Edge Functions (Deno) | Custom SMTP (bring Resend/Postmark) for email; BYO SMS provider | 2 projects, 50k MAU, 500MB DB, 5GB egress, 1GB storage [1] | Pro $25/mo [1] | **Free projects pause after 7 days of no DB activity** [1] | Just Postgres — `pg_dump` anytime | High — CLI, SQL migrations, local Docker stack, declarative schema |
| **Firebase** | Keep GH Pages; call Firebase from a JS island (or move to Firebase Hosting) | Email link built in & free; phone auth billed per-SMS once on Blaze [2][3] | Firestore **security rules** (declarative but not SQL) | Firestore (NoSQL) | Cloud Functions **require Blaze** (usage-based, still free at this scale) [2][3] | No first-party transactional email; phone SMS billed ~$0.01–0.06/verification depending on region [3] | Spark: 50k MAU, 1GiB Firestore, 50k reads/20k writes/day, 10GB hosting [2] | Blaze = pay-as-you-go, first ~2M fn calls/mo free [2] | No pause; idle Spark projects just sit at $0 | Firestore export exists but NoSQL shape is Firebase-specific | Medium — rules DSL less relational; harder to express "roster joins" declaratively |
| **Cloudflare Pages/Workers + D1 + KV** | Would **replace** GH Pages (or keep GH Pages static + Workers API only) | No built-in auth — hand-roll with KV/D1 sessions + Turnstile for bot protection | Custom middleware in Worker code | D1 (SQLite) | Workers (edge) | MailChannels free bridge is **deprecated (Aug 2024)**; Cloudflare's own Email API is public beta; Resend via HTTP fetch is the documented path [4] | Workers: 100k req/day; KV: 100k reads/1k writes/day, 1GB; D1 usage billed beyond free row quota [5] | Workers Paid $5/mo (10M req) [5]; D1 $0.001/M rows read, $1/M rows written | No pause — always on | SQLite file is portable; Worker code is CF-specific | High raw capability, but **no RLS** — authorization is only as good as the code you write |
| **PocketBase** | Keep GH Pages; PocketBase runs on your own box, called by a JS island | Built-in **email OTP** since recent releases (8-digit code, rate-limited, auto-expiring) [6]; SMS not built in | Per-collection **API rules** (expression language) | SQLite (embedded) | JS/Go hooks in the same binary | None built in — call Resend/Twilio yourself from hooks | N/A — it's a single binary you host | Hosting cost only | You run it — no platform pause, but you own uptime | Total — it's your SQLite file, self-hosted | High for a single binary + hooks, but **you are the ops team** (patching, backups, TLS) |
| Convex | Would replace GH Pages hosting for the app portion (or hybrid) | No built-in passwordless OTP primitive out of the box; typically paired with Clerk/Auth.js | Function-level code, not row policies | Document store + reactive functions | Built-in ("mutations/queries") | BYO | 1M function calls/mo, 0.5GB storage free [7] | Professional $25/dev/mo [7] | No pause | Convex-specific query language; moderate lock-in | Medium — great DX, but reactive-document model is a bigger conceptual shift than SQL |
| Appwrite | Self-host or Appwrite Cloud; GH Pages stays static, call Appwrite API | Built-in email OTP, magic URL, phone (Twilio/MSG91/Vonage) auth | Collection-level permissions (rules) | MariaDB-backed document API | Appwrite Functions | BYO SMTP; BYO SMS provider | 5GB bandwidth, 2GB storage, 750k executions, 75k MAU [8] | Pro $25/mo [8] | Cloud: no stated pause | Self-hostable (Docker) — low lock-in | Medium — good CLI, permissions model less SQL-native than RLS |
| Nhost | Keep GH Pages; call Nhost (Postgres+Hasura+Auth) | Built-in email OTP/magic link, phone OTP (Twilio) | Hasura **permissions** on top of Postgres (RLS-adjacent) | Postgres (via Hasura GraphQL) | Serverless functions | BYO SMTP | 1GB DB/storage, 5GB bandwidth [9] | Pro $25/mo [9] | UNVERIFIED — check before committing | Postgres underneath — low lock-in | Medium-High — Postgres + declarative Hasura permissions, smaller ecosystem than Supabase |
| **Custom: Cloudflare Worker/Deno Deploy + Turso/D1 + Resend + Twilio Verify, Better Auth** | Keep GH Pages entirely; Worker is a pure API | Better Auth ships **email-OTP** and **phone-number** plugins (phone plugin OTP storage/consistency still being polished as of Sep 2026) [10] | Hand-written middleware, or thin RLS-like checks in SQL views | Turso (libSQL, hosted SQLite) or D1 | Worker/Deno function | Resend (email) + Twilio Verify (SMS) | Effectively $0 at this scale (see §3) | Pay-as-you-go, no forced tier | No pause | Minimal — plain SQL + a small Worker | High effort but full control; more code for AI agents to get right on auth |
| Neon + Auth.js/Better Auth on Vercel/Netlify | Keep GH Pages, or move to Vercel/Netlify for both static+API | Auth.js/Better Auth handle OTP via your own email/SMS sender | You write the authorization checks (or add Postgres RLS yourself against Neon) | Neon Postgres (serverless, branchable) | Vercel/Netlify functions | BYO | Neon free: 0.5GB storage, 100 compute-hrs/mo [11]; Netlify free: 125k function invocations, 100GB bandwidth | Neon Launch ~$0.106/CU-hr + $0.35/GB-mo, no minimum since Dec 2025 [11] | No pause | Postgres underneath — low lock-in | High — Postgres + Git-branchable DB is very agent-friendly, but you assemble Auth.js/Better Auth yourself |

**Email providers** (transactional, for the notification piece):
- **Resend** — free: 3,000 emails/mo, 100/day, 1 verified domain; SPF/DKIM/DMARC on every tier including free; paid starts $20/mo for 50k [12].
- **Postmark** — free: 100 emails/mo (no card, doesn't expire); Basic $15/mo for 10k, then ~$1.30–1.80/1k overage [13]. Best-in-class deliverability reputation, but the free tier is too small for anything beyond testing.
- **Amazon SES** — cheapest at volume ($0.10/1,000 sent) but free tier is now just "$200 AWS credit for new accounts" (the old 62,000-emails-free-from-EC2 tier is gone for post-July-2025 signups) [14]; requires manual SPF/DKIM/DMARC + "production access" request to leave the sandbox (new accounts start sandboxed and can only send to verified addresses).
- **Brevo** — free: 300 emails/day (~9,000/mo), up to 100k contacts; Starter $9/mo for 5k/mo [15]. Most generous free tier of the four, but marketing-ESP-flavored rather than a dev-first transactional API.

**SMS**:
- **Twilio Verify** (OTP-specific) — $0.05 per successful verification + the underlying message cost (~$0.0083 for US SMS) ≈ **$0.058/verification**, plus number rental (~$1.15/mo) and **A2P 10DLC registration**: ~$1.50–$10/mo campaign fee (a "low-volume" campaign is the cheap tier), ~$1/mo per number, one-time T-Mobile fee (currently waived) [16][17]. Toll-free numbers are an alternative registration path with sometimes-faster approval [16].
- **Twilio programmable SMS** (raw, no OTP orchestration) is cheaper per-message but you build the code/rate-limit/retry logic yourself — Verify is the better fit for a low-volume hobby OTP flow.
- **AWS SNS** — $0.00645/message to US numbers, first 100/mo free; **also requires A2P 10DLC registration** for US sends (~$10/mo regular campaign or ~$2/mo low-volume, ~$1/mo number) [18]. Comparable total cost to Twilio at this volume; SNS has no OTP-specific verification wrapper (Twilio Verify or Amazon's own "End User Messaging" service does).
- **A2P 10DLC / toll-free is unavoidable overhead for any US SMS sender in 2026**, Twilio or AWS — budget ~$3–12/month in carrier/campaign fees on top of per-message cost, and note the campaign approval can take **1–3 business days**, which matters if you want SMS live for a specific trip.
- Every BaaS in the table above **still requires you to bring your own Twilio/MessageBird/Vonage account for phone OTP** — none of them absorb the carrier fees; they just relay through your credentials.

## 2. Architecture patterns: static site + dynamic islands

**Recommended pattern**: keep `tools/build.py` → GitHub Pages exactly as-is, and add one small script
(`shared/island.js`) that the trip tab loads and that talks directly to the backend's public HTTPS
API using a **bearer token stored client-side by the SDK** (e.g., `supabase-js`, which keeps the
session in `localStorage` and refreshes it automatically), not cookies:

- **Cross-domain cookies avoided entirely.** `supabase-js` calls `https://<project-ref>.supabase.co`
  directly from `juntar.net`; the request carries an `Authorization: Bearer <jwt>` header, not a
  cookie, so there is no `SameSite`/`Domain=.juntar.net` negotiation and no CSRF surface for
  state-changing requests (a third-party page cannot forge the header). The trade-off is **XSS risk**:
  a token in `localStorage` is readable by any script that runs on the page, so the same discipline
  already implied by the CSP-friendly, no-inline-script style of `engine.js` (SRI-pinned Leaflet from
  cdnjs, no other third-party JS) matters more once real credentials are in play.
- **If a cookie-based backend is chosen instead** (e.g., the custom Worker stack), `juntar.net` and
  an `api.juntar.net` subdomain are same-site (same registrable eTLD+1), so `SameSite=Lax` (or
  `Strict`) cookies with `Domain=.juntar.net` *do* travel on `fetch(..., {credentials:'include'})`
  calls from the guide pages — this is not the classic cross-site case. CORS still needs
  `Access-Control-Allow-Origin: https://juntar.net` (not `*`) with `Allow-Credentials: true`. Add a
  CSRF header check (e.g., require a custom `X-Requested-With` header the browser won't attach
  cross-site) as belt-and-suspenders even though SameSite already blocks most forgery.
- **SEO / `noindex`**: unchanged — guides stay `noindex` per `site.json`, and personalized data
  (who's RSVP'd, contact info) must never be rendered into the static HTML server-side; it is fetched
  client-side, post-load, so it never touches the GitHub Pages cache or a search index.
- **Caching of personalized data**: fetch RSVP/roster data with `cache: 'no-store'`; the public
  "counts only" aggregate can be fetched the same way (cheap enough at this scale) or with a short
  `max-age` if traffic ever grows. Never bake per-viewer state into a `<script>` block the way
  `#mapdata`/`#rsvpdata` currently only carry non-personal photo/map data.
- **Progressive enhancement when the API is down**: the island must fail closed to "read-only local
  guide" behavior, matching the existing defensive style (`try{...}catch(e){}` around every
  `localStorage` call in `engine.js`). If the backend is unreachable or a Supabase free project is
  paused, the RSVP widget should show a static message ("Can't reach the guest list right now — text
  the host") rather than break the page; "My picks" and the packing checklist, which are pure
  client-state today, keep working exactly as they do now regardless of API health.

**Is a framework migration (Astro/SvelteKit/Next) worth it?** No, not at this scale. The value a
framework adds — component reuse, SSR for SEO, routing — doesn't address the actual gap (auth +
RLS + notifications), and the project already has a working, fast, dependency-free renderer
(`tools/build.py` + `engine.js`, ~250 lines) tuned to this exact declarative-JSON workflow that AI
agents already operate well (`new-trip`, `update-trip` skills). A framework would mean a Node
toolchain, a bundler, and re-deriving the same island pattern anyway, for no capability the current
stack lacks. Revisit only if the product grows into needing server-rendered per-user pages (e.g., a
host dashboard that must be crawlable or shareable via server-rendered link previews) — not needed
here since all personalized views are behind login.

## 3. Recommended shortlist

**Primary: Supabase (Postgres + Auth + RLS + Edge Functions), email-OTP first, SMS added later.**

Why it wins for *this* project specifically:
- **RLS is the single best match for "declarative + AI-agent-operated."** The site already treats
  `tools/schema.md` as a contract that agents extend before touching code; Postgres RLS policies are
  the same idea applied to authorization — versionable SQL, reviewable in a diff, testable locally.
  Firestore rules and Hasura permissions are declarative too, but less naturally relational for
  "roster joins across events/hosts/rsvps" than SQL + RLS.
- **Zero new hosting to manage.** GitHub Pages stays exactly as-is; `supabase-js` is called directly
  from the browser with no cookie/subdomain complexity (see §2). No server for the maintainer to
  patch, unlike PocketBase or the custom-Worker option.
- **Email OTP is free and built in**; phone OTP is opt-in and billed at cost through your own Twilio
  account, so SMS can be deferred to a later milestone without any architecture change.
- **Low lock-in**: it's Postgres. `supabase db dump`/`pg_dump` gets you a portable database any time;
  the CLI, migrations, and local dev (`supabase start`, a local Docker Postgres+Auth+Studio stack)
  are all declarative-config-first, matching the maintainer's stated preference.

**Secondary: Cloudflare Worker + D1 (or Turso) + Better Auth + Resend + Twilio Verify** (the "custom
minimal stack"). Choose this instead if avoiding *any* BaaS vendor matters more than development
speed, or if the project later needs true edge-latency reads. Trade-off: no RLS — all authorization
(the "hosts see everything for their own events only," "RSVP'd users see roster w/o contact info"
rules) has to be hand-written and hand-tested in Worker code, which is more security-critical code
for a single maintainer + AI agents to get exactly right than declaring it in SQL policies. Better
Auth's phone-OTP plugin was still being aligned with its email-OTP plugin's security options as of
September 2026 [10] — worth re-checking before relying on it for SMS.

Runner-up not shortlisted: **Nhost** (Postgres + Hasura + Auth) is architecturally close to Supabase
and would be the fallback if Supabase's free-tier terms change unfavorably; **PocketBase** is
compelling for lock-in-avoidance but fails the "low ops burden" requirement (Fly.io's free tier is
gone as of Oct 2024 [19]; you're paying ~$5/mo for a Hetzner box and are your own SRE for
patching/backups/TLS). **Firebase** is ruled out primarily because Firestore's document model and
security-rules DSL fit this relational roster/visibility problem worse than Postgres+RLS, not
because of cost.

### Estimated monthly cost

Assumptions: ~20 OTP logins/week (~87/month), ~200 notification emails/month, ~50 SMS/month if SMS
is enabled.

| | 100 users | 500 users |
|---|---|---|
| Supabase (DB+Auth+Edge Fn) | $0 — free tier (50k MAU, 500MB DB) covers this by orders of magnitude [1] | $0 — still far under free-tier caps |
| Email (Resend, custom SMTP) | $0 — 200/mo is well under 3,000/mo free (100/day) cap [12] | $0 — unchanged, notification volume is event-driven, not per-user |
| SMS (Twilio Verify, if enabled) | ~$2.90 messages + ~$1.15 number + ~$2–10 A2P campaign fee ≈ **$6–14/mo** [16][17] | same — volume assumption (50/mo) unchanged |
| **Total, email-only** | **$0/month** | **$0/month** |
| **Total, with SMS** | **~$6–14/month** | **~$6–14/month** |

The one real risk to the "$0" line: Supabase's **free-project pause after 7 days with no database
activity** [1]. With only a handful of events/year, weeks can pass with no logins. Mitigate with a
scheduled GitHub Actions job (the repo already runs Actions) that pings a lightweight read-only query
weekly to keep the project active — no cost, no new infra, reuses the CI the project already trusts.
If that's judged too fragile, Supabase Pro ($25/mo) removes the pause and adds backups — still inside
a "step up from hobby" budget if the host later wants it, but not the default recommendation given
the stated $0–$10/month target.

## 4. Sketch: Supabase implementation

### Data model

```sql
-- Auth users live in Supabase's built-in auth.users; this is the app-facing profile.
create table public.profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  first_name text not null,
  email_norm text unique,        -- lower(trim(email)), null if phone-only signup
  phone_norm text unique,        -- E.164, null if email-only signup
  created_at timestamptz not null default now()
);

-- One row per trip; slug is the same slug as guides/<slug> — the link between
-- the static content pipeline and the dynamic RSVP data.
create table public.events (
  id uuid primary key default gen_random_uuid(),
  slug text unique not null,             -- == guides/<slug>/guide.json "slug"
  title text not null,
  status text not null check (status in ('potential','planning','confirmed')),
  start_date date not null,
  end_date date not null,
  created_at timestamptz not null default now()
);

create table public.event_hosts (
  event_id uuid not null references public.events(id) on delete cascade,
  user_id uuid not null references public.profiles(id) on delete cascade,
  role text not null default 'host' check (role in ('host','cohost')),
  primary key (event_id, user_id)
);

create table public.rsvps (
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  user_id uuid references public.profiles(id) on delete set null,  -- null until claimed
  status text not null check (status in ('going','maybe','cant')),
  party_size int not null default 1 check (party_size >= 1),
  kids_count int not null default 0 check (kids_count >= 0),
  is_proxy boolean not null default false,       -- host entered this on someone's behalf
  proxy_name text,                                -- shown until claimed
  proxy_contact_email text,                       -- normalized; used to match on claim
  proxy_contact_phone text,                       -- normalized E.164
  entered_by uuid references public.profiles(id), -- which host entered a proxy RSVP
  claimed_at timestamptz,                          -- set when a real login matches
  note text,
  updated_at timestamptz not null default now(),
  unique (event_id, user_id)                       -- one real RSVP per user per event
);

create table public.messages (         -- event-level announcements
  id uuid primary key default gen_random_uuid(),
  event_id uuid not null references public.events(id) on delete cascade,
  author_id uuid not null references public.profiles(id),
  body text not null,
  created_at timestamptz not null default now()
);

create table public.notifications (    -- outbox for email/SMS sends
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.profiles(id) on delete cascade,
  event_id uuid references public.events(id) on delete cascade,
  channel text not null check (channel in ('email','sms')),
  kind text not null,                   -- rsvp_confirmation | announcement | reminder
  payload jsonb,
  status text not null default 'queued' check (status in ('queued','sent','failed')),
  created_at timestamptz not null default now(),
  sent_at timestamptz
);

create table public.audit_log (
  id bigint generated always as identity primary key,
  actor_id uuid references public.profiles(id),
  event_id uuid references public.events(id),
  action text not null,                 -- 'rsvp.upsert' | 'rsvp.proxy_create' | 'message.post' ...
  detail jsonb,
  created_at timestamptz not null default now()
);
```

### Authorization policies (RLS)

```sql
alter table public.profiles enable row level security;
alter table public.events enable row level security;
alter table public.event_hosts enable row level security;
alter table public.rsvps enable row level security;
alter table public.messages enable row level security;

-- Events: public metadata (no PII on this table) is readable by anyone, incl. anon.
create policy events_public_read on public.events for select using (true);

-- Profiles: a user reads/updates only their own row.
create policy profiles_self_rw on public.profiles
  for all using (id = auth.uid()) with check (id = auth.uid());

-- Profiles: a host can read (not write) the profile of anyone who has RSVP'd
-- to one of that host's events — satisfies "hosts see everything for their own events."
create policy profiles_host_read on public.profiles for select using (
  exists (
    select 1 from public.rsvps r join public.event_hosts h
      on h.event_id = r.event_id
    where r.user_id = profiles.id and h.user_id = auth.uid()
  )
);

-- RSVPs: a host has full read/write over rsvps on events they host
-- (covers proxy RSVP entry + editing).
create policy rsvps_host_all on public.rsvps for all using (
  exists (select 1 from public.event_hosts h
          where h.event_id = rsvps.event_id and h.user_id = auth.uid())
) with check (
  exists (select 1 from public.event_hosts h
          where h.event_id = rsvps.event_id and h.user_id = auth.uid())
);

-- RSVPs: a logged-in user manages their own row directly.
create policy rsvps_self_rw on public.rsvps for all using (
  user_id = auth.uid()
) with check (user_id = auth.uid());

-- Messages: only hosts of the event may post; anyone who is going/maybe may read.
create policy messages_host_write on public.messages for insert with check (
  exists (select 1 from public.event_hosts h
          where h.event_id = messages.event_id and h.user_id = auth.uid())
);
create policy messages_attendee_read on public.messages for select using (
  exists (select 1 from public.event_hosts h
          where h.event_id = messages.event_id and h.user_id = auth.uid())
  or exists (select 1 from public.rsvps r
             where r.event_id = messages.event_id and r.user_id = auth.uid()
               and r.status in ('going','maybe'))
);
```

"RSVP'd users see the roster for events they're in, without contact info" needs to expose *other*
people's rows with columns hidden — RLS alone is row-level, not column-level, so this is a
**security-definer function** (the platform's normal pattern for controlled column exposure):

```sql
create or replace function public.event_roster(p_event_id uuid)
returns table (
  rsvp_id uuid, display_name text, status text,
  party_size int, kids_count int, is_proxy boolean,
  contact_email text, contact_phone text     -- null unless caller hosts this event
)
language sql security definer set search_path = public as $$
  select r.id, coalesce(p.first_name, r.proxy_name), r.status, r.party_size,
         r.kids_count, r.is_proxy,
         case when exists (select 1 from event_hosts h
                            where h.event_id = p_event_id and h.user_id = auth.uid())
              then r.proxy_contact_email end,
         case when exists (select 1 from event_hosts h
                            where h.event_id = p_event_id and h.user_id = auth.uid())
              then r.proxy_contact_phone end
  from rsvps r left join profiles p on p.id = r.user_id
  where r.event_id = p_event_id
    and (
      exists (select 1 from event_hosts h where h.event_id = p_event_id and h.user_id = auth.uid())
      or exists (select 1 from rsvps me where me.event_id = p_event_id
                 and me.user_id = auth.uid() and me.status in ('going','maybe'))
    )
$$;
grant execute on function public.event_roster(uuid) to authenticated;
```

"Public sees no personal info, counts only":

```sql
create or replace function public.event_public_counts(p_event_id uuid)
returns table (going_count int, maybe_count int, going_people int)
language sql security definer set search_path = public as $$
  select count(*) filter (where status='going'),
         count(*) filter (where status='maybe'),
         coalesce(sum(party_size) filter (where status='going'), 0)
  from rsvps where event_id = p_event_id
$$;
grant execute on function public.event_public_counts(uuid) to anon, authenticated;
```

### OTP login + proxy-RSVP claim flow

1. The trip-tab island renders an email (and optionally phone) field.
2. `supabase.auth.signInWithOtp({ email })` — Supabase mails a 6-digit code via your configured SMTP
   (custom SMTP = Resend, to avoid the very low default rate limit on Supabase's built-in mailer).
3. User enters the code; `supabase.auth.verifyOtp({ email, token, type: 'email' })` returns a session;
   `supabase-js` stores the access/refresh JWT in `localStorage` and auto-refreshes it.
4. A Postgres trigger on `auth.users` insert upserts `public.profiles` (normalizing email to
   `lower(trim(...))`, phone to E.164).
5. **Claim on first login**: the same trigger (or a follow-up RPC called right after login) runs:
   ```sql
   update public.rsvps
      set user_id = new_profile_id, claimed_at = now()
    where user_id is null
      and (proxy_contact_email = new_profile.email_norm
           or proxy_contact_phone = new_profile.phone_norm);
   ```
   This links any host-entered proxy RSVP (someone who replied "we're in!" over text before ever
   creating an account) to their real account the moment they first log in, matched on normalized
   email/phone — exactly the "claim on first login" flow requested.

### Static build stays the source of truth

- `guide.json` (content: attractions, stay, trip narrative) remains the only thing the `new-trip`/
  `update-trip` skills and `tools/build.py` touch — unchanged.
- `events.slug` in Postgres **equals** the `guides/<slug>` folder name; that's the entire link
  between the two systems — the island reads `document.body.dataset.slug` (already emitted by
  `build.py` today) and passes it as the key for every RSVP/roster/message call.
- A small `tools/sync_events.py` (new, mirrors the existing tools' style) reads `trip.slug/title/
  status/start/end` out of each `guide.json` and upserts the corresponding row in `public.events` —
  keeping `guide.json` authoritative for trip *content* while the database is authoritative for
  *who's coming*. Run it as one more step in the `publish` skill, after `validate.py`/`build.py`.

### Local dev, migrations, CI (agent-operable)

- `supabase init` + `supabase start` gives a local Postgres+Auth+Storage+Studio stack in Docker —
  no cloud account needed for day-to-day schema work.
- Schema changes are plain `.sql` files under `supabase/migrations/`; an agent runs
  `supabase migration new <name>`, edits the generated file (or `supabase db diff -f <name>` after
  changing the local DB interactively), and commits it — the same "edit the declarative file, then
  run the tool" loop the project already uses for `guide.json`/`tools/build.py`.
- CI: add a workflow alongside `pages.yml` that runs `supabase db push --dry-run` (or
  `supabase db lint`) against a preview branch database on pull requests, and `supabase db push` to
  the real project on merge to `main`, using `SUPABASE_ACCESS_TOKEN`/`SUPABASE_DB_PASSWORD` repo
  secrets — mirrors the existing "validate → build → deploy" gate pattern in `pages.yml` rather than
  introducing a new mental model.

## Sources

Fetched 2026-09-23.

1. Supabase Pricing — https://supabase.com/pricing
2. Firebase Pricing — https://firebase.google.com/pricing
3. "Firebase Authentication Pricing 2026" (phone/SMS billing summary) — https://blog.logto.io/firebase-authentication-pricing
4. Cloudflare Workers docs, "Send Emails With Resend" (successor to the deprecated MailChannels free bridge) — https://developers.cloudflare.com/workers/tutorials/send-emails-with-resend/
5. Cloudflare Workers Platform Pricing — https://developers.cloudflare.com/workers/platform/pricing/
6. PocketBase OTP authentication docs — https://pocketbase-pocketbase.mintlify.app/auth/otp
7. Convex pricing summary — https://www.saasodds.com/blog/convex-pricing
8. Appwrite Pricing — https://appwrite.io/pricing
9. Nhost Pricing — https://nhost.io/pricing
10. Better Auth — Email OTP plugin (https://better-auth.com/docs/plugins/email-otp) and Phone Number plugin (https://better-auth.com/docs/plugins/phone-number); open alignment issue — https://github.com/better-auth/better-auth/issues/11297
11. Neon Pricing — https://neon.com/pricing
12. Resend pricing summary — https://nuntly.com/resend-pricing (cross-checked against https://www.resend.com/)
13. Postmark pricing summary — https://costbench.com/software/email-api/postmark/
14. Amazon SES Free Tier — https://aws.amazon.com/blogs/messaging-and-targeting/the-amazon-ses-free-tier/ ; SES Pricing — https://aws.amazon.com/ses/pricing/
15. Brevo Pricing — https://www.brevo.com/pricing/
16. Twilio Verify Pricing — https://www.twilio.com/en-us/verify/pricing ; cost breakdown — https://www.engagelab.com/blog/twilio-verify-pricing-what-100-000-verifications-really-cost
17. A2P 10DLC fee breakdown — https://textbee.dev/blog/twilio-pricing-real-cost-breakdown
18. AWS SNS SMS Pricing — https://aws.amazon.com/sns/sms-pricing/ ; 10DLC origination for SNS — https://aws.amazon.com/blogs/compute/provisioning-and-using-10dlc-origination-numbers-with-amazon-sns
19. Fly.io free tier removal (Oct 2024) — https://www.saaspricepulse.com/blog/flyio-free-tier-2026

**UNVERIFIED / worth re-checking before committing**: Nhost's exact inactivity/pause policy;
Cloudflare's own native Email Send API's public-beta limits (50-recipient cap cited by a
secondary source, not confirmed against Cloudflare's own docs page); exact current A2P 10DLC
campaign-approval turnaround time; whether Supabase's free-tier pause can be prevented by a
scheduled read-only query versus requiring a write (the docs describe it as "database activity"
without specifying read vs. write) — test this empirically before relying on the GitHub Actions
keep-alive mitigation in §3.
