# Auth, RSVP, and privacy patterns for a small invite-only community site (v0.2)

Research memo for juntar.net's move from static guides (v0.1) to a multi-user platform (v0.2)
with OTP login, RSVPs, and simple messaging. Audience: a few hosts, tens to low hundreds of
friends and school families in California. All sources fetched 2026-09-23 unless noted.
Items without a strong current source are marked UNVERIFIED.

## Top 10 recommendations

1. **Default to email OTP codes, not magic links**, and not SMS, as the v0.2 login factor.
   Codes avoid the "security scanner pre-clicks the link and burns it" failure mode that
   plagues magic links in exactly the audience this site has (parents on school-district and
   corporate email with Defender/Proofpoint/Mimecast link-scanning) — see §1.
2. **Do not offer SMS/phone OTP at launch.** At this scale the deliverability, A2P 10DLC
   registration, per-message cost, and toll-fraud exposure are disproportionate to the benefit;
   collect phone only as a contact field. Revisit if hosts specifically ask for it — see §1.
3. **6-digit numeric email codes, 10–15 minute expiry, single use, rate-limited** — this matches
   NIST SP 800-63B-4 and OWASP guidance and is what most CIAM guidance converges on — see §1.
4. **Skip passkeys for v0.2.** They're mature in 2026 but add real implementation cost for a
   site whose whole login problem is "occasional, low-stakes, from many different devices."
   Revisit only if repeat-login friction becomes a real complaint — see §1.
5. **RSVP states should be Going / Maybe / Can't go**, not a longer taxonomy; add a waitlist
   only for camping/lodging-capacity trips. This matches Partiful, Luma, and Meetup's default
   shapes — see §2.
6. **Support host-entered "proxy" RSVPs with later claim-by-login**, keyed by email/phone —
   this is standard on Punchbowl, Paperless Post, and Partiful and matches how a real trip
   host already operates (tracking replies from a group chat) — see §2.
7. **Make every event invite-only-by-link with an explicit guest list, not a public/searchable
   event**, and let the host toggle whether guests see each other's names — mirrors Facebook
   Events' "Only Invitees" + hide-guest-list pattern and Luma's default — see §2.
8. **Do not build DMs or threaded comments in v0.2.** Ship an ICS-based reminder and a single
   host broadcast/announcement channel; point real conversation at the group's existing chat
   (iMessage/WhatsApp/Signal group). Small RSVP platforms overwhelmingly ship broadcast +
   light reactions, not full messaging — see §2 and §4.
9. **Treat this as CCPA/CPRA-exempt by size but still minimize data and put a one-paragraph
   privacy notice up**: no sale/share of data, no third-party ad trackers, no dark patterns.
   The revenue/record thresholds put a hobby site far outside CCPA/CPRA's "business" definition
   — see §3.
10. **Enforce all guest-list, roster, and PII visibility rules server-side**, never by hiding
    fields in the client, and require login (adult accounts only, no child profiles — kids as
    counts) before any name, email, or phone is served to a browser — see §3 and §4.

---

## 1. Passwordless authentication

### Email OTP vs. magic links
- OWASP's Forgot Password / Authentication cheat sheets treat OTP codes and magic links as
  roughly equivalent in security, with the real difference being UX and operational risk, not
  cryptographic strength — tokens should be short-lived (~15 min), CSPRNG-generated with
  ≥128 bits entropy, stored server-side as a hash, and invalidated on first successful use.
  [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
- The practical failure mode that tips the scale toward codes: corporate/school email security
  gateways (Microsoft Defender for Office 365 Safe Links, Mimecast, Proofpoint) and some email
  client previews **pre-fetch every link in an email before the human ever opens it**, which
  silently consumes a single-use magic link and produces a confusing "invalid/expired link"
  error for the real user. This is a documented, recurring issue across multiple auth libraries
  in 2025–2026 discussions (better-auth, Supabase, others).
  [Magic Link token consumed by scanners – better-auth discussion](https://github.com/better-auth/better-auth/discussions/6985) ·
  [Magic links/reset tokens consumed by scanners in institutional environments – Supabase](https://github.com/orgs/supabase/discussions/41618)
  Given the audience is school families — exactly the population behind district/corporate
  email security — this failure mode is not theoretical. Mitigations exist (allow N attempts
  within the expiry window instead of true single-use; or make the emailed GET a non-mutating
  confirmation page and require an explicit POST to actually consume the link), but they add
  complexity that a typed-in 6-digit code sidesteps entirely.
  [GitHub discussion on mitigations](https://github.com/better-auth/better-auth/discussions/6985)
- Codes also work better cross-device (type a code seen on your phone into a laptop tab you
  already had open) — magic links tie the click to the device/browser that opened the email,
  which is a common complaint pattern in the same threads above.
- **Recommendation:** default to a 6-digit numeric email code, single use, 10–15 minute expiry,
  rate-limited resend. This lines up with NIST's stated 6-digit/short-window norm even though
  NIST's own restricted-channel rules are written for SMS/PSTN, not email (see below).

### SMS OTP: cost, registration, fraud, and NIST's stance
- **Pricing (US, 2026, headline rates):** Twilio ≈ $0.0079 outbound / $0.0075 inbound per SMS
  before surcharges; AWS SNS ≈ $0.0065–0.007 per outbound SMS with a 100-message/month free
  tier; Vonage ≈ $0.00846 per outbound SMS. All three still layer on carrier surcharges and (in
  the US) A2P 10DLC fees.
  [Twilio SMS pricing US](https://www.twilio.com/en-us/sms/pricing/us) ·
  [AWS SNS SMS pricing](https://aws.amazon.com/sns/sms-pricing/) ·
  [Amazon SNS vs Vonage benchmark](https://knock.app/sms-api-benchmarks/compare/amazon-sns-vs-vonage)
- **A2P 10DLC registration is mandatory** for US application-to-person SMS on a standard
  10-digit number: brand registration (~$4 for a sole proprietor, $48+ for a standard/vetted
  brand) plus campaign registration (~$15–17, sometimes $15 per additional campaign) plus
  monthly per-campaign fees (~$1.50–10) plus per-message carrier surcharges (~$0.003–0.005).
  Since February 2025 major US carriers block unregistered A2P traffic outright. End-to-end
  approval commonly takes 1–4 weeks.
  [A2P 10DLC fees explainer](https://www.ghlscaleup.com/blog/a2p-10dlc-fees-explained) ·
  [10DLC registration guide 2026](https://textbolt.com/blog/10dlc-compliance/)
- **Toll-free SMS is a real alternative** that skips 10DLC brand/campaign registration in favor
  of a simpler toll-free verification step, but per-message toll-free rates run *higher* than
  10DLC, and providers note **Twilio Verify specifically can be used for OTP without full 10DLC
  registration** if that's the only SMS use case.
  [Toll-free vs 10DLC](https://www.telgorithm.com/news/toll-free-vs-10dlc) ·
  [10DLC to toll-free onboarding – Twilio](https://www.twilio.com/en-us/blog/swap-10dlc-numbers-toll-free)
- **SMS pumping / toll fraud** is a live risk for any public phone-number input tied to OTP
  delivery: fraudsters harvest revenue share from a mobile network operator by triggering mass
  OTP sends to numbers they control. Twilio's Verify Fraud Guard (automatic, included in Verify
  pricing) claims to have saved customers $62.7M between June 2022 and October 2024, and offers
  tunable aggressiveness (Basic/Standard/Max) trading block rate against false positives.
  [What is SMS pumping fraud – Twilio](https://www.twilio.com/docs/glossary/what-is-sms-pumping-fraud) ·
  [Verify Fraud Guard](https://www.twilio.com/en-us/blog/twilio-verify-fraud-guard-a-powerful-defense-against-sms-pumping-fraud)
- **NIST SP 800-63B-4 now formally classifies SMS/PSTN OTP as a "restricted authenticator"** —
  the first time NIST has created that category. It's still permitted, but only with a
  documented risk assessment, a migration plan away from it, and user notification of the risk
  (SIM swap, number porting, MITM/relay). NIST does **not** permit email as an out-of-band
  authentication channel either, so neither channel is a "blessed" NIST authenticator in the
  strict sense — both are best understood as convenience factors, not NIST-compliant MFA.
  [NIST SP 800-63B-4 SMS restricted authenticator](https://blog.typingdna.com/nist-sp-800-63b-rev-4-sms-otp-is-now-a-restricted-authenticator-but-we-have-the-fix/) ·
  [SP 800-63B authenticators (NIST pages)](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)
- **Recommendation:** phone should be a **contact field only** at v0.2, not a login factor.
  The combination of $15–50+ upfront registration, weeks-long approval, ongoing per-message and
  monthly fees, toll-fraud exposure, and NIST's now-explicit "restricted" framing is a lot of
  surface area for a "tens to low hundreds of friends and family" app where email already
  reaches everyone. Revisit only if hosts report meaningful numbers of guests without reliable
  email (uncommon in this demographic) — this judgment is UNVERIFIED against juntar's actual
  user base and should be confirmed with the host before ruling it out permanently.

### Passkeys / WebAuthn
- 2026 sources describe passkeys as mainstream: FIDO Alliance reports 15B+ accounts can use
  passkeys and 1B+ activations; Microsoft made passkeys the default for new consumer accounts
  in May 2025; sign-in success/latency numbers are cited as meaningfully better than passwords.
  `SimpleWebAuthn` is called out as the practical open-source library for both server and
  browser sides, with a full flow achievable in a few hundred lines.
  [Passkeys/WebAuthn 2026 guide](https://kanopylabs.com/blog/passkeys-webauthn-passwordless-auth-guide) ·
  [SimpleWebAuthn usage note](https://www.hirenodejs.com/blog/nodejs-passkeys-webauthn-2026)
- **Recommendation:** don't build passkeys into v0.2. The library maturity is real, but the
  juntar use case (occasional login, many shared/family devices, low security stakes) doesn't
  need it, and it adds an enrollment UX and recovery-path burden disproportionate to the value
  for this size of app. Treat as an "optional upgrade later" item as the CLAUDE.md style guide
  already implies for other renderer-only-change features.

### Session handling
- Community guidance converges on: short-lived access tokens (minutes) with no sensitive data
  embedded; refresh tokens in `HttpOnly`, `Secure` cookies; a **separate, revocable, rotating**
  "remember me" token rather than just extending the primary session cookie's lifetime, because
  a long-lived primary session token is a bigger blast radius if leaked; and tracking idle
  timeout separately from absolute session lifetime.
  [Session cookies vs JWT / refresh strategy](https://appmaster.io/blog/session-management-cookies-jwt-refresh) ·
  [Remember-me token design](https://medium.com/@sonishubham65/remember-me-in-web-applications-how-it-works-and-why-it-matters-77f0335f2ccd)
- **Recommendation:** plain server-side session cookies (`HttpOnly`, `Secure`, `SameSite=Lax`)
  are simpler and sufficient at this scale — JWTs mainly earn their complexity when multiple
  independent services need to verify a token without a shared session store, which does not
  describe a single small Node/Python app. A "remember me" cookie can reasonably run 30–90 days
  for this low-risk, invite-only use case (UNVERIFIED exact figure — no source gives a single
  authoritative number for "community app" specifically; treat 30–90 days as a judgment call,
  not a cited norm). Provide a "log out everywhere" action that revokes all sessions/refresh
  tokens for the account, which is a natural complement to OTP-only login (no password to reset
  as a recovery path).

### Rate limiting and abuse controls
- Best-practice OTP-endpoint rate limiting layers **per-identifier** limits (e.g., 3–5 codes per
  email/phone per hour) with **per-IP** limits (e.g., 10–20 requests/hour, burst cap ~3/60s),
  because per-IP alone is defeated by botnets rotating across many IPs, and per-identifier alone
  doesn't stop an attacker enumerating many identifiers from one IP.
  [Ratelimiting OTP endpoints – Unkey](https://www.unkey.com/blog/ratelimiting-otp) ·
  [OTP endpoint abuse protection](https://securityboulevard.com/2026/03/protecting-otp-magic-link-endpoints-from-abuse-ip-reputation-rate-limiting-and-suspicious-ip-throttling/)
- NIST requires verifiers to cap consecutive failed attempts against a single authenticator at
  no more than 100 before disabling it, and mandates rate limiting whenever the authenticator
  output is under 64 bits of entropy — which a 6-digit numeric code always is (~20 bits), so
  rate limiting is not optional for this design.
  [NIST OTP rate-limiting guide](https://identitychallengecard.avatier.com/en/blog/otp-nist-800-63b-defense-2026)
- Return identical responses/timing for "account exists" vs. "account doesn't exist" on the
  send-code step to avoid user enumeration, per OWASP's forgot-password guidance cited above.
- **Recommendation:** cap at roughly 5 code requests/hour per email and 10 failed verification
  attempts per code/session before forcing a fresh code; add a simple per-IP ceiling; log and
  alert (not block) on unusual patterns given the tiny expected traffic volume.

## 2. RSVP product patterns

### RSVP states, party size, capacity, waitlists
- Meetup, Luma, and Partiful all use a small state set — commonly **Going / Maybe / Can't
  go / Waitlist** — rather than a long taxonomy. Waitlists activate automatically once a
  numeric capacity is reached and promote people automatically as spots free up, with a
  notification on promotion.
  [Luma waitlist](https://help.luma.com/p/waitlist) ·
  [Meetup waitlist](https://help.meetup.com/hc/en-us/articles/360003883411-Enable-a-Waitlist-for-your-Meetup-event)
- Party-size / "+N guests" handling is standard: Paperless Post lets a host toggle "allow
  guests to bring additional guests" and cap group size per invite, with the RSVP-ing guest
  optionally naming their additional guests; Punchbowl similarly lets guests "RSVP for people
  they plan to bring." This is the right model for "kids counts" too — collect a number, not a
  child's name/profile.
  [Paperless Post +1 settings](https://paperlesspost.zendesk.com/hc/en-us/articles/360022154372-Allow-guests-to-RSVP-for-1s) ·
  [Punchbowl guest additions](https://help.punchbowl.com/article/129-how-do-my-guests-add-additional-guests)

### Proxy / "ghost" RSVPs entered by the host
- This is an established pattern, not a novelty: Punchbowl's "Connect" feature and Partiful's
  manual-add flow both let a host add a guest who replied off-platform, and the guest shows up
  as "Invited"/pending until they engage; RSVPify markets a "Quick-Add RSVP" tool for the same
  purpose.
  [Partiful manual guest add](https://help.partiful.com/hc/en-us/articles/26502966982427-How-can-I-manually-add-guests-to-my-party) ·
  [RSVPify guest list app](https://rsvpify.com/guest-list-app/)
- None of the sources found describe a polished "claim this proxy RSVP by logging in" merge
  flow in detail — this is a design gap across the category, not just for juntar
  (UNVERIFIED beyond the general existence of manual-add features). **Recommendation:** key
  proxy RSVPs by email (and optionally phone) so that when that person later logs in with a
  matching email, the app auto-attaches their existing proxy RSVP rather than creating a
  duplicate guest record — this is a reasonable, low-risk design inference rather than an
  observed industry pattern.

### Guest list visibility
- Facebook Events: a "Private"/"Only Invitees" event doesn't appear in search and is visible
  only to invitees; within that, hosts can separately toggle showing the guest list on/off
  (defaults to visible to invitees, hideable via an "Only me" style control); organizers always
  see the full list regardless.
  [Facebook private event guest list controls](https://www.itgeared.com/who-can-see-a-private-event-on-facebook/) ·
  [Control who sees/joins a Facebook event](https://www.messenger.com/help/208747122499067)
- Partiful gives finer-grained controls: hide guest count, anonymize the guest list, hide
  Activity Feed timestamps, and a separate "Guest Approval" (request-to-join) gate.
  [Partiful guest-list management](https://help.partiful.com/hc/en-us/sections/30470926071195--Managing-Guest-List)
- Luma defaults to showing the guest list (for social proof) but lets hosts hide it per event.
  [Luma guest list privacy](https://help.luma.com/p/managing-your-guest-list)
- **Recommendation for juntar:** invite-only-by-link event, guest list visible to other invited
  guests by first name only (not full name, not contact info) by default, with a host toggle to
  hide it entirely; contact info (email/phone) visible to hosts/co-hosts only, never to other
  guests — matches the pattern across all three commercial products above and the "roster lists
  only what the host states" / no-contact-fields rule already in this repo's CLAUDE.md.

### Invitation mechanics for a private, invite-only group
- Facebook's "Only Invitees" option and Gathio's link-only, no-account, no-search model are the
  two cleanest fits for "small friends/family group, no public discovery wanted." Gathio in
  particular is explicit that its events are accessible only by direct link and are never
  listed or searchable, with no account required to RSVP; email is optional and used only to
  send the host an edit password. Mobilizon similarly supports anonymous/no-registration RSVP.
  [Gathio overview](https://docs.gath.io/) ·
  [Mobilizon RSVP/privacy](https://wbcomdesigns.com/mobilizon-review/)
- **Recommendation:** unlisted, invite-only-by-link events; no public event directory; no
  approval-required gate needed at this trust level (the group is small and pre-vetted by the
  host), though a lightweight join-code or host-approval step is a reasonable v0.3 addition if
  links get forwarded beyond the intended group. This matches the existing CLAUDE.md rule that
  joining is coordinated with the host, with no RSVP forms.

### Messaging: what small platforms actually ship
- Partiful ships host-to-guest "text blasts" plus lightweight reactions ("boops") — a broadcast
  and reaction model, not peer-to-peer threaded messaging.
  [Partiful features](https://party.pro/partiful/)
- Meetup gates a group chat to confirmed ("Going") attendees, opening automatically when a
  waitlisted member is promoted, and separately sends structured notifications (onsite/email/
  push) for event updates to Yes/Maybe/Waitlist members and hosts.
  [Meetup event chats](https://help.meetup.com/hc/en-us/articles/48377254200589-Joining-event-chats-and-third-party-messaging-on-Meetup) ·
  [Meetup notifications](https://help.meetup.com/hc/en-us/articles/40708711774221-What-notifications-Meetup-can-send)
- Gathio and Mobilizon lean on comments/updates rather than DMs; none of the platforms surveyed
  ship full private messaging as a core RSVP-app feature — the pattern is **broadcast +
  comments/reactions**, with real back-and-forth pushed to existing chat apps or platform-
  native group chat features.
- **Recommendation:** build a single host → all-guests announcement/broadcast (email, maybe
  with an in-app feed) plus optional guest reactions/RSVP notes. Do not build direct messaging
  or threaded comments in v0.2 — link out to the group's existing chat thread instead. This is
  both what the evidence shows small platforms actually ship and the cheaper build.

### Calendar integration
- Practice is to offer **both** a static `.ics` attachment and "Add to calendar" links (Google/
  Outlook/Apple/Yahoo), because ICS files render slightly differently across calendar clients
  and link-based flows reduce support friction; `VALARM`/`TRIGGER` fields set a reminder offset
  (e.g., 15 minutes before) inside the ICS itself.
  [ICS vs Add-to-Calendar links](https://www.addevent.com/blog/ics-files-vs-add-to-calendar-links-which-is-better)
- **Recommendation:** this matches juntar's existing `trip.ics` output — keep generating ICS,
  and consider adding host-configurable reminder lead time via `VALARM` if not already present
  (implementation detail to confirm against `tools/build.py`, not verified in this research
  pass since it's outside web-search scope).

## 3. Privacy and legal (US / California)

### CCPA/CPRA applicability
- CCPA/CPRA applies to a "business" only if it crosses at least one threshold: **annual gross
  revenue over $26,625,000** (2026 inflation-adjusted figure), **or** buys/sells/shares personal
  information of 100,000+ CA consumers/households per year, **or** derives 50%+ of revenue from
  selling/sharing personal information. A hobby site with a handful of hosts and low hundreds of
  users falls under none of these and is squarely outside the statute's "business" definition.
  [CCPA applicability guide 2026](https://www.clym.io/blog/ccpa-applicability-guide) ·
  [CCPA for small business 2026](https://getuptocode.com/guides/ccpa-state-privacy-small-business)
- Caveat: 2026 CPRA regulations added narrower **activity-based** triggers that can pull in
  smaller companies engaged in specific high-risk processing (e.g., automated decision-making,
  large-scale profiling) regardless of size — UNVERIFIED whether any of juntar's planned
  features (OTP login, RSVP, broadcast messages) would plausibly qualify; on the facts
  described, they almost certainly would not, but this is a legal judgment, not a research
  finding, and isn't a substitute for counsel if the site ever monetizes or scales up sharply.
  [CCPA audit rule effect on SMBs 2026](https://www.swktech.com/how-ccpa-audit-rule-affects-smb-2026/)
- **Recommendation:** juntar is not legally required to post a CCPA notice, but a short, plain
  privacy note (what's collected, why, who sees it, that it's never sold, how to request
  deletion) is good practice regardless and cheap to write.

### COPPA
- COPPA applies to operators that are either directed at children under 13 or have actual
  knowledge they're collecting personal information from a child under 13; the compliance
  burden (verifiable parental consent, specific notices) is heavy enough that most general
  sites simply exclude under-13 users from having accounts at all rather than complying.
  [FTC COPPA overview](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa) ·
  [COPPA compliance requirements 2026](https://usercentrics.com/us/knowledge-hub/coppa-compliance/)
- **Confirmed for juntar's plan:** accounts should be adults only (parents/hosts), kids
  represented only as attendance counts (no child names, no child profiles, no child login) —
  this sidesteps COPPA entirely rather than trying to comply with it, and matches the existing
  CLAUDE.md rule about never inferring/attaching names to people in photos.

### TCPA / CAN-SPAM for OTP and notifications
- TCPA: transactional messages (including authentication OTP) need only **prior express
  consent** (lower bar — can be established just by the user supplying their number for that
  purpose), not the **written** consent required for marketing texts. The instant any
  promotional content is added to that message it becomes a marketing message needing the
  higher consent bar — so OTP/transactional SMS templates must stay strictly functional (code
  only, no "check out our new trip!" line). As of April 2025, opt-outs must be honored via *any*
  reasonable method (not just "STOP"), processed within 10 business days.
  [TCPA SMS guide 2026](https://www.idtexpress.com/blog/tcpa-compliance-for-sms-in-2026-the-complete-guide-for-us-businesses/) ·
  [TCPA consent revocation update](https://activeprospect.com/blog/tcpa-text-messages/)
- CAN-SPAM: transactional/relationship emails (which includes OTP codes and account
  notifications) are **exempt from the unsubscribe-link requirement**; only genuinely
  commercial/marketing email needs the opt-out mechanism, functional for 30+ days, honored
  within 10 business days, no fee or extra info required to opt out.
  [FTC CAN-SPAM compliance guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) ·
  [CAN-SPAM 2025 guide](https://securiti.ai/what-is-can-spam-act/)
- **Recommendation:** OTP emails/SMS need no unsubscribe link (they're transactional), but
  event-broadcast emails ("new trip posted," "reminder") are closer to relationship/informational
  content sent to an opted-in list — include a simple unsubscribe/notification-preferences link
  on those anyway as good practice, even though CAN-SPAM's strict unsubscribe mandate applies
  to *commercial* email specifically. Since phone OTP isn't recommended for v0.2, TCPA SMS
  consent mechanics are moot for now; if phone is ever added, keep OTP texts template-only
  (code + expiry, nothing else) to stay on the low-consent-bar side of TCPA.

### Data minimization, retention, deletion, export
- No single source above gives a "community app" specific retention norm; general PII-handling
  guidance is simply: collect only what's needed, minimize what's stored, and never let the
  client filter what the server would otherwise expose.
  [PII handling in web apps](https://blog.logrocket.com/how-to-handle-pii-websites-web-apps/)
- **Recommendation (design inference, not a cited external norm):** let any user delete their
  own account and data on request; let hosts export a roster (CSV) since they already do this
  informally; don't set an automatic retention/deletion timer for past trips given the site's
  archival/memory-keeping purpose, but do offer manual deletion.

### Server-side authorization ("never show PII to unauthenticated users")
- The consistent security guidance: don't return full objects and hide fields client-side;
  filter/authorize on the server before the response is built; treat any server-only token or
  PII-bearing field as something that must never reach client-side code or storage.
  [API security / PII best practices](https://medium.com/@legedith/a-practical-guide-to-designing-a-secure-pii-system-b5611cd2cc15) ·
  [Client-side security considerations](https://dev.to/armstrong2035/5-considerations-for-client-side-security-5fk6)
- **Recommendation:** every API/route that can return a guest's email, phone, or full roster
  must check the caller's session and role server-side before querying/serializing that data —
  not just omit it in the UI. This is a hard requirement, not a nice-to-have, given the
  audience includes minors' attendance data.

### Photo consent
- No single, authoritative consent-form-by-default norm exists for informal/community sites;
  practice ranges widely, and most parents in surveyed US samples post photos of their own kids
  without formal consent, while community/organizational contexts (schools, sports orgs)
  increasingly expect an explicit opt-in, and privacy advocates recommend asking the child too
  as they get older.
  [FOSI guide to sharing kids' photos](https://fosi.org/picture-perfect-privacy-a-guide-to-responsible-sharing-of-your-kids-photos/) ·
  [Parent photo-sharing survey / APA](https://www.apa.org/monitor/2026/06/parents-children-sharing-online)
- **Recommendation:** juntar's existing "uploading is opting in, public by default, `private:
  true` to opt out later" model (per CLAUDE.md host decisions) is reasonable for a small,
  closed, pre-vetted group of families who know each other — this is consistent with observed
  parental norms, though it is looser than what schools/orgs increasingly expect; the memo
  flags this as a judgment call for the host, not a compliance requirement, since the group
  isn't a school or organization subject to those stricter conventions. UNVERIFIED: no source
  directly validates an "opt-out by default" model as best practice; the evidence shows only
  that it's common informal parent behavior, not that it's recommended.

## 4. Where the client's plan may be wrong — candid notes

- **Phone OTP at launch is likely not worth it.** The evidence (10DLC cost/timeline, toll-fraud
  risk, NIST's new "restricted" framing for SMS) all points toward skipping it, and nothing in
  the brief suggests juntar's users lack email. If the plan currently assumes phone OTP is a
  launch feature, reconsider — start email-only, keep phone as a contact field.
- **Showing first names publicly (to anyone, not just invited guests) would be out of step**
  with every commercial pattern surveyed (Facebook, Partiful, Luma all gate guest-list
  visibility behind "invited" status at minimum). If any part of the plan exposes names to
  unauthenticated visitors, that's worth revisiting — visibility should be invited-guests-only
  by default, with host controls to loosen or tighten further.
- **Building messaging (DMs/threads) in v0.2 is probably premature.** Every small-scale
  platform surveyed (Partiful, Meetup, Gathio) ships broadcast + light reactions, not full
  messaging, and directs real conversation to existing chat apps. For a friend group that
  almost certainly already has a group chat, building DMs is meaningful extra surface area
  (spam/abuse handling, notification design, moderation) for a feature the audience likely
  won't use over their existing thread. Recommend linking to the group chat instead and
  shipping only host broadcasts + RSVP-note fields in v0.2.
- **The proxy-RSVP "claim on login" flow needs explicit design attention** — it's a known
  pattern in the category (Punchbowl/Partiful/RSVPify all support host-entered guests) but none
  of the surveyed products document a clean claim/merge UX, so juntar can't just copy an
  existing flow; budget real design time for "what happens when Aaron adds Jane by email, and
  Jane later logs in with that email" rather than treating it as a trivial lookup.
- **If CCPA/CPRA compliance work is currently planned as a big v0.2 line item, it's likely
  overbuilt** for the site's actual size — the thresholds put it well outside the statute. A
  short plain-language privacy note is proportionate; a full CCPA compliance program is not.

---

## Sources

All fetched 2026-09-23.

- [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [Magic Link token consumed by scanners — better-auth discussion #6985](https://github.com/better-auth/better-auth/discussions/6985)
- [Magic links/reset tokens consumed by scanners in institutional environments — Supabase discussion #41618](https://github.com/orgs/supabase/discussions/41618)
- [OTP Security & NIST 800-63B: 2026 Rate-Limiting Guide](https://identitychallengecard.avatier.com/en/blog/otp-nist-800-63b-defense-2026)
- [NIST SP 800-63B-4 Authenticators (official)](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)
- [NIST SP 800-63B-4: SMS OTP is now a Restricted Authenticator — TypingDNA](https://blog.typingdna.com/nist-sp-800-63b-rev-4-sms-otp-is-now-a-restricted-authenticator-but-we-have-the-fix/)
- [Twilio SMS Pricing (US)](https://www.twilio.com/en-us/sms/pricing/us)
- [Amazon SNS SMS Pricing (official)](https://aws.amazon.com/sns/sms-pricing/)
- [Amazon SNS vs Vonage — SMS API benchmarks, Knock](https://knock.app/sms-api-benchmarks/compare/amazon-sns-vs-vonage)
- [A2P 10DLC Fees Explained — GHL Scale Up](https://www.ghlscaleup.com/blog/a2p-10dlc-fees-explained)
- [10DLC Registration: Steps, Costs & Approval Time (2026)](https://textbolt.com/blog/10dlc-compliance/)
- [Toll Free vs. 10DLC — Telgorithm](https://www.telgorithm.com/news/toll-free-vs-10dlc)
- [10DLC Campaign to Programmatic Toll-Free Onboarding — Twilio](https://www.twilio.com/en-us/blog/swap-10dlc-numbers-toll-free)
- [What is SMS Pumping Fraud — Twilio](https://www.twilio.com/docs/glossary/what-is-sms-pumping-fraud)
- [Twilio Verify Fraud Guard](https://www.twilio.com/en-us/blog/twilio-verify-fraud-guard-a-powerful-defense-against-sms-pumping-fraud)
- [Passkeys and WebAuthn: Passwordless Auth Guide for Apps 2026 — Kanopy](https://kanopylabs.com/blog/passkeys-webauthn-passwordless-auth-guide)
- [Node.js Passkeys & WebAuthn in 2026 — HireNodeJS](https://www.hirenodejs.com/blog/nodejs-passkeys-webauthn-2026)
- [Session management for web apps: cookies vs JWTs vs refresh — AppMaster](https://appmaster.io/blog/session-management-cookies-jwt-refresh)
- [Remember Me in Web Applications — Medium](https://medium.com/@sonishubham65/remember-me-in-web-applications-how-it-works-and-why-it-matters-77f0335f2ccd)
- [Ratelimiting OTP endpoints — Unkey](https://www.unkey.com/blog/ratelimiting-otp)
- [Protecting OTP & Magic Link Endpoints from Abuse](https://securityboulevard.com/2026/03/protecting-otp-magic-link-endpoints-from-abuse-ip-reputation-rate-limiting-and-suspicious-ip-throttling/)
- [Luma Waitlist help doc](https://help.luma.com/p/waitlist)
- [Luma Managing Your Guest List](https://help.luma.com/p/managing-your-guest-list)
- [Meetup — Enable a Waitlist](https://help.meetup.com/hc/en-us/articles/360003883411-Enable-a-Waitlist-for-your-Meetup-event)
- [Meetup — Joining event chats](https://help.meetup.com/hc/en-us/articles/48377254200589-Joining-event-chats-and-third-party-messaging-on-Meetup)
- [Meetup — What notifications Meetup can send](https://help.meetup.com/hc/en-us/articles/40708711774221-What-notifications-Meetup-can-send)
- [Partiful App Review — party.pro](https://party.pro/partiful/)
- [Partiful — Managing Guest List help section](https://help.partiful.com/hc/en-us/sections/30470926071195--Managing-Guest-List)
- [Partiful — How can I manually add guests to my party?](https://help.partiful.com/hc/en-us/articles/26502966982427-How-can-I-manually-add-guests-to-my-party)
- [Paperless Post — Allow guests to RSVP for +1s](https://paperlesspost.zendesk.com/hc/en-us/articles/360022154372-Allow-guests-to-RSVP-for-1s)
- [Punchbowl — Can my guests RSVP for people they plan to bring?](https://help.punchbowl.com/article/129-how-do-my-guests-add-additional-guests)
- [RSVPify — Guest List App](https://rsvpify.com/guest-list-app/)
- [Facebook/Messenger — Control who sees or joins your event](https://www.messenger.com/help/208747122499067)
- [Who Can See a Private Event on Facebook — ITGeared](https://www.itgeared.com/who-can-see-a-private-event-on-facebook/)
- [Rallly — self-hosted meeting scheduler](https://www.blackvoid.club/rallly-self-hosted-meeting-schedule-platform/)
- [Gathio documentation](https://docs.gath.io/)
- [Mobilizon review — Wbcom Designs](https://wbcomdesigns.com/mobilizon-review/)
- [ICS files vs Add to Calendar links — AddEvent](https://www.addevent.com/blog/ics-files-vs-add-to-calendar-links-which-is-better)
- [CCPA Applicability 2026: Thresholds and Rules — Clym](https://www.clym.io/blog/ccpa-applicability-guide)
- [CCPA for Small Business: Who's Covered (2026)](https://getuptocode.com/guides/ccpa-state-privacy-small-business)
- [How the CCPA Audit Rule Affects SMBs in 2026 — SWK Technologies](https://www.swktech.com/how-ccpa-audit-rule-affects-smb-2026/)
- [FTC — Children's Online Privacy Protection Rule (COPPA)](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa)
- [COPPA Compliance: key requirements for 2026 — Usercentrics](https://usercentrics.com/us/knowledge-hub/coppa-compliance/)
- [TCPA Compliance for SMS in 2026 — IDT Express](https://www.idtexpress.com/blog/tcpa-compliance-for-sms-in-2026-the-complete-guide-for-us-businesses/)
- [TCPA text messages: Rules and regulations guide for 2026 — ActiveProspect](https://activeprospect.com/blog/tcpa-text-messages/)
- [FTC — CAN-SPAM Act Compliance Guide for Business](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business)
- [What is the CAN-SPAM Act? 2025 Compliance Guide — Securiti](https://securiti.ai/what-is-can-spam-act/)
- [How to handle PII in websites and web apps — LogRocket](https://blog.logrocket.com/how-to-handle-pii-websites-web-apps/)
- [A Practical Guide to Designing a Secure PII System — Medium](https://medium.com/@legedith/a-practical-guide-to-designing-a-secure-pii-system-b5611cd2cc15)
- [Picture-Perfect Privacy: sharing kids' photos — FOSI](https://fosi.org/picture-perfect-privacy-a-guide-to-responsible-sharing-of-your-kids-photos/)
- [What you need to know before sharing your child's life online — APA Monitor](https://www.apa.org/monitor/2026/06/parents-children-sharing-online)
