# Senior DevSecOps Engineer Interview Script (Nordic Style)

A model interview for a senior DevSecOps role at a Nordic company. Tone: calm, team-first, understated, concrete. Use "we", include timeframes, avoid boasting, and end answers with a short reflection. The stories are models: replace the details with your own real examples before the interview.

**Interviewers:** Elin (Engineering Manager) and Mikael (Head of Security) **Candidate:** Hasith

---

## 1. Warm-up and introduction

**Elin:** Thanks for joining. How has your week been?

**Hasith:** Thanks for having me. Busy but steady, and I'm looking forward to this.

**Elin:** Could you introduce yourself?

**Hasith:** Of course. I'm a DevOps engineer with several years of experience, and over time my focus has moved towards building security into delivery pipelines: secrets management, supply chain integrity, and secure Kubernetes platforms. I like making the secure way the easy way, so teams adopt it willingly. What draws me to this role is that you treat security as a shared responsibility rather than a gate at the end.

---

## 2. Philosophy: what DevSecOps means

**Mikael:** What does DevSecOps mean to you?

**Hasith:** Security built into every stage of delivery, owned by the whole team, not handed to one department. In practice that means automated checks early in the pipeline, secure defaults in the platform, and fast feedback to developers. The goal is to reduce risk without slowing teams down, because security that people route around doesn't protect anyone.

**Mikael:** How do you balance security and delivery speed?

**Hasith:** By making checks fast, accurate, and actionable. A scan that takes thirty minutes and produces hundreds of false positives gets ignored. So we tune rules, block only on high-confidence critical findings, and report the rest as tracked work. Paved roads help too: a standard pipeline template with security already built in.

---

## 3. Pipeline security

**Mikael:** Walk us through the security controls in your delivery pipeline.

**Hasith:** I think in layers, matching the stages. Before commit, secret scanning and pre-commit hooks catch leaked credentials. In CI, we run static analysis on the code, dependency scanning for known vulnerable libraries, and linting of infrastructure code with policy-as-code rules. We build the artifact once, scan the container image, generate a software bill of materials, and sign the artifact so later stages can verify it came from our pipeline. Only signed, scanned images are admitted to the cluster, enforced by an admission controller. In staging, we add dynamic testing against the running application. In production, we monitor runtime behaviour and alert on anomalies.

**Mikael:** Why sign artifacts?

**Hasith:** It proves integrity and origin. If someone compromises a registry or slips in a modified image, the cluster refuses to run it because the signature doesn't verify. It's one of the most effective supply chain controls.

---

## 4. Supply chain security

**Mikael:** How do you handle third-party dependency risk?

**Hasith:** We pin dependency versions, scan continuously rather than only at build time, since new vulnerabilities appear after release, and keep a bill of materials for every artifact so we can answer "are we affected?" within minutes when a major vulnerability is announced. We also use a trusted internal registry mirror, and we protect the pipeline itself: least-privilege build identities, short-lived credentials, and reviewed pipeline changes, because the pipeline is a high-value target.

---

## 5. Secrets and identity

**Mikael:** How do you manage secrets?

**Hasith:** Centralised in a secrets manager, separated per environment, with identity-based access instead of static passwords. Workloads authenticate with their own identity and receive short-lived, narrowly scoped credentials. We rotate automatically, log every access, and have a clear revocation process for departed people and retired services. Plain configuration stays separate from secrets, and secrets never go into environment variables that can leak through logs or crash dumps.

---

## 6. Kubernetes and container security

**Mikael:** How would you secure a Kubernetes platform?

**Hasith:** Several layers. Least-privilege access control for people and workloads. Network policies so pods only talk to what they need, which limits lateral movement. Pod security standards: no privileged containers, no running as root, read-only filesystems where possible. Admission policies that enforce these rules and verify image signatures. Minimal base images to shrink the attack surface. Secrets from a manager rather than plain objects. And runtime monitoring to detect unexpected behaviour, like a container suddenly spawning a shell.

---

## 7. Vulnerability management

**Mikael:** A critical vulnerability is announced in a widely used library. What do you do?

**Hasith:** First, assess exposure: using the bill of materials, find which services use the affected version, and whether the vulnerable code is actually reachable and internet-facing. Second, prioritise by real risk, not just the score. Third, mitigate fast: patch and redeploy through the normal pipeline, or apply a temporary control like a firewall rule if a patch isn't ready. Fourth, communicate clearly to affected teams and management. Fifth, verify the fix and review afterwards what slowed us down.

---

## 8. Incident story

**Mikael:** Tell us about a security-relevant incident you handled.

**Hasith:** *(Model answer, replace with your own.)* During a routine review we found that a credential had been committed to a repository by mistake. We rotated it immediately, checked the access logs to confirm it hadn't been used, and removed it from history. Within the following two weeks we added secret scanning in pre-commit hooks and in CI, so the same mistake is blocked before it reaches the repository. We ran a blameless review, since the real issue was the missing guardrail, not the person.

---

## 9. Learning from a mistake

**Elin:** Tell us about a mistake you made.

**Hasith:** *(Model answer, replace with your own.)* I once introduced a blocking vulnerability scan with strict rules, and it started failing many builds over low-risk findings. Teams got frustrated and began working around it. I listened, we tuned the rules to block only critical, exploitable findings, and the rest became tracked work. Adoption improved within a few weeks. What I took from it is that a control people resent is a control people bypass, so involve the teams early.

---

## 10. Unpopular decision

**Elin:** Tell us about an unpopular decision you drove.

**Hasith:** *(Model answer, replace with your own.)* I proposed replacing long-lived deployment credentials with short-lived, identity-based ones. Some colleagues pushed back, because the existing setup worked and migration meant effort. We ran a trial on one service, measured the effort and the reduction in exposed credentials, and walked through the risk of a leaked long-lived key together. The team agreed, and we migrated the rest over about three months. In hindsight, I'd involve the sceptics earlier in designing the trial.

---

## 11. Culture and influence

**Mikael:** How do you get developers to care about security?

**Hasith:** By making it easy and relevant. I give fast, clear feedback in their normal tools, explain the why with real examples, and fix the pipeline rather than blame people. A security champions network helps: one interested engineer per team, who becomes a trusted local voice. I also celebrate good catches instead of treating findings as failures.

**Mikael:** And when a team resists a security requirement?

**Hasith:** I first understand their constraint. Often there's a way to meet the goal with less friction. If the risk is genuinely high, I explain it plainly, agree a timeline, and escalate only as a last step. The aim is to keep the relationship working.

---

## 12. Compliance and regulation

**Mikael:** How do you approach compliance in a Nordic and EU context?

**Hasith:** I aim for compliance as a by-product of good engineering. Requirements such as GDPR, NIS2, and ISO 27001 ask for things like access control, audit trails, change management, and incident handling. If our pipeline already records who approved what, enforces policy automatically, and keeps immutable logs, we produce evidence continuously instead of scrambling before an audit. For data protection, I care about data minimisation, encryption in transit and at rest, and keeping data in approved regions.

---

## 13. Threat modelling and incident response

**Mikael:** How do you approach threat modelling?

**Hasith:** Early and lightweight. For a new service, the team and I sketch the data flows, ask what could go wrong at each step, and decide what controls matter most. A one-hour session before building often prevents weeks of rework.

**Mikael:** What does good incident response look like?

**Hasith:** Preparation, clear roles, and calm execution. Contain first, preserve evidence, investigate, recover, then communicate openly and run a blameless review with concrete follow-ups. Regular practice, like tabletop exercises, matters, because the first time shouldn't be a real incident.

---

## 14. On-call and sustainability

**Elin:** How do you think about on-call and work-life balance?

**Hasith:** On-call should be sustainable: alerts that page only when users or security are genuinely affected, runbooks, fair rotation, and recurring pages turned into engineering work. A tired team makes more mistakes, and in security that matters even more.

---

## 15. Closing

**Mikael:** Any questions for us?

**Hasith:** A few. How do security and engineering teams collaborate day to day? How do you prioritise security work against feature work? And what would a good first six months look like in this role?

**Elin:** Great questions. Thanks, Hasith.

**Hasith:** Thank you both, I enjoyed it.

---

## Quick-reference: key phrases to remember

- "Make the secure way the easy way."
- "Build once, scan, sign, verify before admit."
- "Block on critical and exploitable; track the rest."
- "Short-lived, identity-based credentials, not static secrets."
- "Compliance as a by-product of good engineering."
- "A control people resent is a control people bypass."

## Coaching notes

- Lead with the concrete story, finish with a one-line reflection.
- Use "we" for team results, and keep claims modest.
- Include a timeframe in every result.
- Pause before answering; silence is comfortable in Nordic interviews.
- Be ready for follow-ups: "how would you prove that?" and "what would you do differently?"
