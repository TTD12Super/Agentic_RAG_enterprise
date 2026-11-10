# Authorization matrix — MVP uses PUBLIC/INTERNAL; higher-sensitivity rows are future policy examples

| Action/resource | System Admin | Website Manager | Chairman | Employee | Anonymous |
|---|---|---|---|---|---|
| `document:create` | Yes | Yes | No | No | No |
| `document:update` | Yes | Yes | No | No | No |
| `document:delete` | Yes, subject to retention/legal hold | Yes, subject to retention/legal hold | No | No | No |
| `document:approve` / `document:publish` | Yes | Yes | No | No | No |
| Read published PUBLIC | Yes | Yes | Yes | Yes | Yes |
| Read published INTERNAL | Yes | Yes | All, subject to explicit deny | Assigned documents only | No |
| Website management | Yes | Yes | No | No | No |
| Code/system operations | Yes | No | No | No | No |
| Other users' conversation bodies | No | No | No | No | No |

**Identity, classification, tenant, resource, purpose and document version matter.** This is a product-design example, not a substitute for final policy. Test denial and policy outage.

Authenticated users may read their own conversation. Published PUBLIC documents are accessible by default, subject to the existing explicit-deny and current-version rules.

`CONFIDENTIAL` and `RESTRICTED` remain future classification examples, not MVP UI values. The final PDP still evaluates department rules, document ACLs and explicit deny precedence.

## Owner-provided policy correction

The matrix is evaluated with default deny and explicit deny precedence. Chairman has broad published-document read capability, but an explicit document/tenant/policy deny wins. Website Manager and System Admin may administer documents according to action-specific permissions; System Admin's operational rights do not grant access to user conversation bodies. Employee onboarding requires administrator approval. The final policy remains subject to the approved authorization contract.
