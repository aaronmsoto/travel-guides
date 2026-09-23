# Auth, RSVP, and privacy patterns for a small invite-only community site (v0.2)

Research memo for juntar.net's move from static guides (v0.1) to a multi-user platform (v0.2)
with OTP login, RSVPs, and simple messaging. Audience: a few hosts, tens to low hundreds of
friends and school families in California. All sources fetched 2026-09-23. Items without a
strong current source are marked UNVERIFIED.

## Top 10 recommendations

1. **Default to email OTP codes, not magic links, and not SMS.** Codes avoid the "security
   scanner pre-clicks the link and burns it" failure that hits exactly this audience (parents on
   school/corporate email with Defender/Proofpoint/Mimecast link-scanning) — §1.
2. **Do not offer SMS/phone OTP at launch.** A2P 10DLC registration cost/timeline, per-message
   fees, and toll-fraud exposure are disproportionate at this scale; keep phone as a contact
   field only — §1.
3. **6-digit numeric email codes, 10–15 min expiry, single use, rate-limited** — matches NIST
   SP 800-63B-4 and OWASP guidance — §1.
4. **Skip passkeys for v0.2.** Mature in 2026, but adds enrollment/recovery cost this low-stakes,
   many-shared-devices use case doesn't need yet — §1.
5. **RSVP states: Going / Maybe / Can't go**, plus a waitlist only where capacity is real
   (camping/lodging) — matches Partiful, Luma, Meetup defaults — §2.
6. **Support host-entered "proxy" RSVPs, claimable by email match on later login** — standard on
   Punchbowl, Paperless Post, Partiful, and matches how hosts already track a group chat — §2.
7. **Make every event invite-only-by-link with a guest list hideable by the host** — mirrors
   Facebook Events' "Only Invitees" + hide-guest-list pattern and Luma's default — §2.
8. **Don't build DMs or threads in v0.2.** Ship ICS reminders and a single host broadcast
   channel; point real conversation at the group's existing chat — §2, §4.
9. **Treat juntar as outside CCPA/CPRA by size, but still post a short plain-language privacy
   note** — no sale/share of data, no ad trackers — §3.
10. **Enforce all PII/roster visibility server-side, never by hiding fields client-side**;
    accounts are adults only, kids are counts, not profiles — §3, §4.

## 1. Passwordless authentication

**Email OTP vs. magic links.** OWASP treats OTP codes and magic links as roughly equivalent in
security; both need short-lived (~15 min), CSPRNG tokens (≥128 bits), hashed server-side,
invalidated on first use.
[OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
The deciding factor is operational: corporate/school email security gateways (Microsoft Defender
Safe Links, Mimecast, Proofpoint) and some client previews **pre-fetch links before the user
opens them**, silently burning single-use magic links and producing a confusing "expired link"
error — a recurring 2025–2026 issue across auth libraries, and exactly the population (school
district / corporate email) juntar targets.
[better-auth discussion #6985](https://github.com/better-auth/better-auth/discussions/6985) ·
[Supabase discussion #41618](https://github.com/orgs/supabase/discussions/41618)
Codes also work cross-device (read on phone, type on laptop) where links tie the click to the
device that opened the email. **Default to a 6-digit email code**, single use, 10–15 min expiry,
rate-limited resend.

**SMS OTP.** US 2026 headline pricing: Twilio ≈$0.0079/outbound SMS, AWS SNS ≈$0.0065–0.007
(100 free/month), Vonage ≈$0.00846 — before carrier surcharges.
[Twilio US pricing](https://www.twilio.com/en-us/sms/pricing/us) ·
[AWS SNS pricing](https://aws.amazon.com/sns/sms-pricing/) ·
[SNS vs Vonage benchmark](https://knock.app/sms-api-benchmarks/compare/amazon-sns-vs-vonage)
**A2P 10DLC registration is mandatory** for standard US 10-digit numbers: brand fee (~$4 sole
proprietor, $48+ vetted brand) + campaign fee (~$15–17) + monthly per-campaign fee (~$1.50–10) +
per-message carrier surcharge (~$0.003–0.005); carriers have blocked unregistered A2P traffic
since February 2025; approval takes 1–4 weeks end-to-end.
[A2P 10DLC fees](https://www.ghlscaleup.com/blog/a2p-10dlc-fees-explained) ·
[10DLC guide 2026](https://textbolt.com/blog/10dlc-compliance/)
**Toll-free numbers** skip 10DLC brand/campaign registration for a simpler verification step, but
per-message rates run higher; Twilio Verify can be used for OTP without full 10DLC if SMS OTP is
the only use case.
[Toll-free vs 10DLC](https://www.telgorithm.com/news/toll-free-vs-10dlc) ·
[10DLC-to-toll-free](https://www.twilio.com/en-us/blog/swap-10dlc-numbers-toll-free)
**SMS pumping/toll fraud** is a real risk on any public phone-number input tied to OTP; Twilio's
Verify Fraud Guard (automatic, included with Verify) reports $62.7M saved June 2022–Oct 2024,
with tunable aggressiveness.
[SMS pumping fraud](https://www.twilio.com/docs/glossary/what-is-sms-pumping-fraud) ·
[Verify Fraud Guard](https://www.twilio.com/en-us/blog/twilio-verify-fraud-guard-a-powerful-defense-against-sms-pumping-fraud)
**NIST SP 800-63B-4 now classifies SMS/PSTN OTP as a "restricted authenticator"** — permitted,
but only with a documented risk assessment, migration plan, and user risk notification (SIM
swap, porting, MITM). NIST also does not permit email as an out-of-band channel, so neither
option is a NIST-blessed authenticator — both are convenience factors, not compliant MFA.
[SMS restricted authenticator](https://blog.typingdna.com/nist-sp-800-63b-rev-4-sms-otp-is-now-a-restricted-authenticator-but-we-have-the-fix/) ·
[SP 800-63B authenticators](https://pages.nist.gov/800-63-4/sp800-63b/authenticators/)
**Recommendation:** phone as contact field only for v0.2. The $15–50+ setup cost, weeks-long
approval, ongoing fees, fraud exposure, and NIST's "restricted" framing outweigh the benefit when
email already reaches this audience (UNVERIFIED against juntar's actual user base — confirm with
host before ruling out permanently).

**Passkeys/WebAuthn.** 2026 sources describe passkeys as mainstream (FIDO Alliance: 15B+ eligible
accounts, 1B+ activations; Microsoft default for new consumer accounts since May 2025);
`SimpleWebAuthn` is the practical open-source library, workable in a few hundred lines.
[Passkeys 2026 guide](https://kanopylabs.com/blog/passkeys-webauthn-passwordless-auth-guide) ·
[SimpleWebAuthn note](https://www.hirenodejs.com/blog/nodejs-passkeys-webauthn-2026)
**Recommendation:** skip for v0.2 — occasional, low-stakes, many-shared-device logins don't need
it; revisit only if login friction becomes a real complaint.

**Session handling.** Guidance converges on short-lived access tokens with no sensitive payload,
refresh tokens in `HttpOnly`/`Secure` cookies, a separate revocable/rotating "remember me" token
rather than extending the primary session, and tracking idle timeout separately from absolute
lifetime.
[Cookies vs JWT vs refresh](https://appmaster.io/blog/session-management-cookies-jwt-refresh) ·
[Remember-me token design](https://medium.com/@sonishubham65/remember-me-in-web-applications-how-it-works-and-why-it-matters-77f0335f2ccd)
**Recommendation:** plain server-side session cookies (`HttpOnly`, `Secure`, `SameSite=Lax`) —
JWT's cross-service benefit doesn't apply to a single small app. A 30–90 day "remember me" cookie
is a reasonable judgment call for this low-risk case (UNVERIFIED — no source gives a single
authoritative figure for "community app"). Provide "log out everywhere" (revoke all
sessions/refresh tokens) as the natural recovery path given there's no password to reset.

**Rate limiting.** Best practice layers **per-identifier** limits (~3–5 codes/email/hour) with
**per-IP** limits (~10–20/hour, burst ~3/60s), since per-IP alone is defeated by botnets
rotating IPs and per-identifier alone doesn't stop enumeration from one IP.
[Ratelimiting OTP endpoints](https://www.unkey.com/blog/ratelimiting-otp) ·
[OTP endpoint abuse protection](https://securityboulevard.com/2026/03/protecting-otp-magic-link-endpoints-from-abuse-ip-reputation-rate-limiting-and-suspicious-ip-throttling/)
NIST caps consecutive failed attempts at 100 and *mandates* rate limiting whenever authenticator
output is under 64 bits — true of any 6-digit code (~20 bits), so this isn't optional.
[NIST rate-limiting guide](https://identitychallengecard.avatier.com/en/blog/otp-nist-800-63b-defense-2026)
Return identical timing/response for existent vs. non-existent accounts to prevent enumeration
(OWASP, above). **Recommendation:** ~5 code requests/hour per email, ~10 failed attempts per code
before forcing a new one, plus a per-IP ceiling; log/alert rather than hard-block given juntar's
tiny expected volume.

## 2. RSVP product patterns

**States, party size, capacity, waitlists.** Meetup, Luma, and Partiful all use a small state
set — **Going / Maybe / Can't go / Waitlist** — not a long taxonomy; waitlists auto-activate at
capacity and auto-promote with a notification.
[Luma waitlist](https://help.luma.com/p/waitlist) ·
[Meetup waitlist](https://help.meetup.com/hc/en-us/articles/360003883411-Enable-a-Waitlist-for-your-Meetup-event)
Paperless Post and Punchbowl both support "+N guests" — a toggle for additional-guest count per
invite, with the RSVP-ing guest naming their own additions. This is the right model for kids too:
collect a count, not a child profile.
[Paperless Post +1s](https://paperlesspost.zendesk.com/hc/en-us/articles/360022154372-Allow-guests-to-RSVP-for-1s) ·
[Punchbowl guest additions](https://help.punchbowl.com/article/129-how-do-my-guests-add-additional-guests)

**Proxy/"ghost" RSVPs.** Established pattern: Punchbowl's "Connect" feature, Partiful's manual-add,
and RSVPify's "Quick-Add RSVP" all let a host add someone who replied off-platform.
[Partiful manual add](https://help.partiful.com/hc/en-us/articles/26502966982427-How-can-I-manually-add-guests-to-my-party) ·
[RSVPify guest list app](https://rsvpify.com/guest-list-app/)
None of the sources found document a polished claim/merge flow when that person later logs in —
a gap across the category, not unique to juntar (UNVERIFIED beyond the existence of manual-add
features generally). **Recommendation:** key proxy RSVPs by email so a matching login
auto-attaches the record instead of duplicating it — a design inference, not an observed
industry pattern.

**Guest list visibility.** Facebook's "Only Invitees" event is invisible outside the guest list;
within it, a separate toggle hides the guest list itself (organizers always see the full list).
[Facebook private event controls](https://www.itgeared.com/who-can-see-a-private-event-on-facebook/) ·
[Messenger event controls](https://www.messenger.com/help/208747122499067)
Partiful adds finer controls (hide count, anonymize list, hide activity timestamps, request-to-
join gate);
[Partiful guest-list management](https://help.partiful.com/hc/en-us/sections/30470926071195--Managing-Guest-List)
Luma defaults to showing the list for social proof but lets hosts hide it.
[Luma guest list](https://help.luma.com/p/managing-your-guest-list)
**Recommendation:** invite-only-by-link, guest list visible to *other invited guests* by first
name only (not contact info), host toggle to hide entirely; contact info visible to hosts/
co-hosts only — matches all three products above and this repo's existing "no contact fields"
rule.

**Invitation mechanics.** Facebook's "Only Invitees" and Gathio's link-only/no-account model both
fit "small pre-vetted group, no discovery wanted"; Gathio events are accessible only by direct
link, never listed, no account required, email optional (used only for the edit password).
Mobilizon similarly supports anonymous RSVP.
[Gathio docs](https://docs.gath.io/) ·
[Mobilizon review](https://wbcomdesigns.com/mobilizon-review/)
**Recommendation:** unlisted, invite-only-by-link events; no directory; no approval gate needed
at this trust level, though a join code or host-approval step is a reasonable v0.3 addition if
links get forwarded beyond the intended group.

**Messaging.** Partiful ships host→guest broadcast "text blasts" plus lightweight reactions, not
threaded messaging.
[Partiful review](https://party.pro/partiful/)
Meetup gates group chat to confirmed attendees and separately sends structured update
notifications to Yes/Maybe/Waitlist.
[Meetup event chats](https://help.meetup.com/hc/en-us/articles/48377254200589-Joining-event-chats-and-third-party-messaging-on-Meetup) ·
[Meetup notifications](https://help.meetup.com/hc/en-us/articles/40708711774221-What-notifications-Meetup-can-send)
Gathio and Mobilizon lean on comments/updates, not DMs. **No platform surveyed ships full private
messaging as a core feature** — the pattern is broadcast + comments/reactions, with real
conversation pushed to existing chat apps. **Recommendation:** one host→all-guests broadcast
(email, maybe an in-app feed) plus optional reactions/RSVP notes; no DMs or threads in v0.2 —
link to the group's existing chat instead.

**Calendar.** Practice is to offer both a static `.ics` and "Add to calendar" links, since ICS
renders slightly differently per client and links reduce support friction; `VALARM`/`TRIGGER`
sets an in-file reminder offset.
[ICS vs Add-to-Calendar links](https://www.addevent.com/blog/ics-files-vs-add-to-calendar-links-which-is-better)
**Recommendation:** matches juntar's existing `trip.ics` output; consider a host-configurable
`VALARM` reminder lead time if not already present (unverified against current `tools/build.py`
— outside this research pass's scope).

## 3. Privacy and legal (US / California)

**CCPA/CPRA.** Applies only if a business crosses one of three thresholds: **annual gross
revenue over $26,625,000** (2026 figure), **or** buys/sells/shares PI of 100,000+ CA
consumers/households/year, **or** derives 50%+ of revenue from selling/sharing PI. A hobby site
with a few hosts and low hundreds of users meets none of these.
[CCPA applicability 2026](https://www.clym.io/blog/ccpa-applicability-guide) ·
[CCPA for small business](https://getuptocode.com/guides/ccpa-state-privacy-small-business)
Caveat: 2026 regulations added narrower activity-based triggers for high-risk processing
regardless of size (UNVERIFIED whether OTP/RSVP/broadcast messaging would plausibly qualify — on
the facts given, almost certainly not, but this is a legal judgment, not a research finding).
[CCPA audit rule / SMBs](https://www.swktech.com/how-ccpa-audit-rule-affects-smb-2026/)
**Recommendation:** no legal requirement to post a CCPA notice, but a short plain-language notice
(what's collected, why, who sees it, never sold, how to request deletion) is cheap and good
practice regardless.

**COPPA.** Applies to operators directed at children under 13 or with actual knowledge they're
collecting a under-13's personal information; most general sites simply exclude under-13
accounts rather than build compliance (verifiable parental consent, specific notices).
[FTC COPPA overview](https://www.ftc.gov/legal-library/browse/rules/childrens-online-privacy-protection-rule-coppa) ·
[COPPA 2026 requirements](https://usercentrics.com/us/knowledge-hub/coppa-compliance/)
**Confirmed for juntar's plan:** accounts are adults only, kids are attendance counts, never
profiles or logins — this avoids COPPA rather than complying with it, consistent with this
repo's "never infer/attach names to people in photos" rule.

**TCPA/CAN-SPAM.** TCPA: transactional messages (including OTP) need only **prior express**
consent (lower bar) vs. the **written** consent marketing texts require; adding any promotional
content to an OTP message pushes it into the higher bar, so templates must stay code-only. As of
April 2025, opt-outs must be honored via *any* reasonable method within 10 business days, not
just "STOP".
[TCPA SMS 2026 guide](https://www.idtexpress.com/blog/tcpa-compliance-for-sms-in-2026-the-complete-guide-for-us-businesses/) ·
[TCPA consent revocation](https://activeprospect.com/blog/tcpa-text-messages/)
CAN-SPAM: transactional/relationship email (OTP codes, account notices) is **exempt** from the
unsubscribe-link mandate; only commercial/marketing email needs it (functional 30+ days, honored
within 10 business days).
[FTC CAN-SPAM guide](https://www.ftc.gov/business-guidance/resources/can-spam-act-compliance-guide-business) ·
[CAN-SPAM 2025 guide](https://securiti.ai/what-is-can-spam-act/)
**Recommendation:** OTP emails/SMS need no unsubscribe link; event-broadcast emails are closer to
relationship content but including a simple preferences/unsubscribe link is good practice anyway.
Since phone OTP isn't recommended for v0.2, TCPA SMS mechanics are moot for now; if added later,
keep OTP texts template-only (code + expiry, nothing else).

**Data minimization, retention, server-side authorization.** General PII guidance: collect only
what's needed, and never let the client filter what the server would otherwise expose —
authorize/filter server-side before the response is built.
[PII handling in web apps](https://blog.logrocket.com/how-to-handle-pii-websites-web-apps/) ·
[Secure PII system design](https://medium.com/@legedith/a-practical-guide-to-designing-a-secure-pii-system-b5611cd2cc15)
**Recommendation (design inference, no external retention norm found):** allow self-service
account/data deletion; let hosts export a roster (CSV); no automatic retention timer for past
trips given the site's archival purpose, but support manual deletion on request. Every route that
can return email/phone/roster data must check the caller's session and role server-side, not just
hide fields in the UI — a hard requirement given minors' attendance data is involved.

**Photo consent.** No single authoritative norm for informal community sites exists; most US
parents surveyed post their own kids' photos without formal consent, while school/organizational
contexts increasingly expect explicit opt-in.
[FOSI kids'-photos guide](https://fosi.org/picture-perfect-privacy-a-guide-to-responsible-sharing-of-your-kids-photos/) ·
[APA Monitor survey](https://www.apa.org/monitor/2026/06/parents-children-sharing-online)
**Recommendation:** juntar's existing "uploading is opting in, public by default, `private: true`
to opt out" model is reasonable for this small, closed, pre-vetted group, though looser than
school/org conventions — a host judgment call, not a compliance requirement (UNVERIFIED as a
recommended best practice; evidence shows only that it matches common informal parent behavior).

## 4. Where the client's plan may be wrong — candid notes

- **Phone OTP at launch is likely not worth it.** 10DLC cost/timeline, toll-fraud risk, and
  NIST's "restricted" framing all point toward email-only at launch, with phone kept as a
  contact field.
- **Publicly showing first names (to anyone, not just invited guests) would be out of step**
  with every product surveyed — Facebook, Partiful, and Luma all gate guest-list visibility
  behind invited status at minimum. Visibility should default to invited-guests-only.
- **Building DMs/threads in v0.2 is probably premature.** Partiful, Meetup, and Gathio all ship
  broadcast + light reactions, not full messaging, and route real conversation to existing chat
  apps — which this friend group almost certainly already has. Recommend host broadcasts + RSVP
  notes only, linking to the existing group chat for everything else.
- **The proxy-RSVP claim/merge flow needs real design attention**, not a copy-paste — it's a
  known pattern (Punchbowl/Partiful/RSVPify all support host-entered guests) but no surveyed
  product documents a clean claim UX, so budget time for "what happens when Aaron adds Jane by
  email, and Jane later logs in with that email."
- **If CCPA/CPRA compliance is currently planned as a major v0.2 line item, it's likely
  overbuilt** for the site's actual size — the thresholds put it well outside the statute. A
  short plain-language notice is proportionate; a full compliance program is not.

## Sources

All fetched 2026-09-23.

- [OWASP Forgot Password Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Forgot_Password_Cheat_Sheet.html)
- [Magic Link token consumed by scanners — better-auth #6985](https://github.com/better-auth/better-auth/discussions/6985)
- [Magic links/reset tokens consumed by scanners — Supabase #41618](https://github.com/orgs/supabase/discussions/41618)
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
