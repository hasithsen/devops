# Senior DevOps Engineer Interview Script (Nordic Style)

A model interview for a senior DevOps role at a Nordic company. Tone: calm, team-first, understated, concrete. Use "we", include timeframes, avoid boasting, and end answers with a short reflection.

**Interviewers:** Elin (Engineering Manager) and Anders (Platform Lead) **Candidate:** Hasith

---

## 1. Warm-up and introduction

**Elin:** Thanks for joining. Before we start, how has your week been?

**Hasith:** Thanks for having me. It's been a good week, busy but steady. I'm looking forward to the conversation.

**Elin:** Could you introduce yourself and what you do today?

**Hasith:** Of course. I'm a DevOps engineer with several years of experience, most recently leading a small platform team. Our focus is CI/CD, Kubernetes, and secrets management, and keeping releases boring and reliable. I enjoy mentoring and building practices a team can sustain. What drew me here is your focus on sustainable engineering and ownership by the teams themselves.

---

## 2. Incident leadership

**Anders:** Tell us about a production incident you handled.

**Hasith:** A client reported that some values from our API gateway were being represented incorrectly in production. We first checked logs to confirm the scope, then traced it to a change from a third-party team's code. We coordinated with them, and a fix was deployed the same day. Afterwards we ran a blameless post-mortem and added a validation check to the pipeline, so that class of issue is caught before release.

**Anders:** How did you communicate during it?

**Hasith:** We kept one channel for updates, posted short status notes at regular intervals, and told the client early what we knew and didn't know. Clear communication reduced the pressure on everyone.

---

## 3. Technical disagreement

**Elin:** Tell us about a time you disagreed with your team on a technical decision.

**Hasith:** I proposed Go for a new microservice, and the team was hesitant because of familiarity and the existing stack. Instead of arguing, we compared the trade-offs together: concurrency, memory use, and learning curve, using a small prototype. Once we reviewed the numbers together, the team aligned, and we now use the same evaluation approach for stack choices.

---

## 4. Learning from a mistake

**Anders:** Tell us about a mistake you made.

**Hasith:** I once proposed Java for a service to stay consistent with our stack. During testing we saw the memory overhead and garbage collection behaviour weren't a good fit for that workload. We switched to Go early, before production, and it has been our default for similar services since. What I took from it is to test assumptions with the real workload before committing.

---

## 5. Mentoring and people

**Elin:** How do you support less experienced engineers?

**Hasith:** One junior engineer was technically strong but anxious about on-call. I shadowed him first, then we swapped, so he led while I observed. Within about two weeks he handled on-call independently. He later helped other juniors with the same worry, which I'm proud of, because the confidence spread beyond one person.

**Elin:** And when someone is underperforming?

**Hasith:** I start with a private conversation to understand what's going on. In one case a colleague had a personal issue lasting about a week. The team redistributed work without sharing private details, and he got back up to speed and stayed with us. People need to be treated like people.

---

## 6. Technical deep-dive: delivery pipeline

**Anders:** Walk us through how a change gets from commit to production.

**Hasith:** A developer pushes to a feature branch and CI runs unit tests, static analysis, and dependency scans. After review, merging to main builds the artifact once, tags it with the commit hash, and pushes it to a shared registry. CI then updates the dev CD repository with the new tag, and the CD tool deploys it, where we run smoke and integration tests. If they pass, a promotion pull request updates staging, which gets end-to-end, load, and security tests. Production follows the same pattern with senior approval and a canary rollout, monitored, with automatic rollback. Rollback is simply reverting a commit. The principle throughout is build once, promote the same artifact, and keep git as the source of truth.

**Anders:** How do you handle secrets?

**Hasith:** Centralised in a secrets manager, separated per environment, with identity-based access instead of static passwords, short-lived credentials, rotation, audit logging, and a clear process for revoking access.

**Anders:** What about database changes in a canary?

**Hasith:** We use expand and contract: add backward-compatible changes first, switch code in a later release, and remove old structures only when nothing uses them, so rollback stays safe.

---

## 7. Kubernetes troubleshooting

**Anders:** A pod keeps restarting in production. What do you do?

**Hasith:** I check status and events first, since the last termination reason and exit code usually point to a crash on startup, a memory limit kill, or a failing liveness probe. Then logs, including the previous container's logs. If there are none, I check the node for pressure. I fix the cause, confirm stability, and add an alert on restart counts.

---

## 8. On-call and sustainability

**Elin:** How do you think about on-call and work-life balance?

**Hasith:** On-call should be sustainable. Alerts should page only when users are affected, runbooks should exist, load should be shared fairly, and recurring pages should become engineering work to remove the cause. A tired team makes more mistakes.

---

## 9. Unpopular decision

**Elin:** Tell us about an unpopular technical decision.

**Hasith:** Our senior engineers were spending roughly a day a week on self-managed Kubernetes upgrades. I proposed a managed service, and some colleagues pushed back because of the tuning effort they'd invested. We ran a four-week trial on a non-critical cluster with agreed measures. Upgrade effort dropped from days to hours, and cluster-related pages fell over six months. The team agreed to migrate. In hindsight, I'd involve the sceptics earlier in designing the trial.

---

## 10. Closing

**Anders:** Any questions for us?

**Hasith:** Yes, a few. How is on-call organised and shared? How do teams decide on tooling? And what does a good first six months look like in this role?

**Elin:** Great questions. Thanks, Hasith.

**Hasith:** Thank you both, I enjoyed it.

---

## Coaching notes

- Lead with the concrete story, finish with a one-line reflection.
- Use "we" for team results, and keep claims modest.
- Include a timeframe in every result.
- Pause before answering; silence is comfortable in Nordic interviews.
- Replace the model details with your own real examples before the interview.
