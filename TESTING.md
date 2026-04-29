# Local testing plan

## 1. Build and start

```bash
make meacoffee        # build images, start stack, load test data, tail logs
```

Expected: server starts on port 8080 with no crash-loop, test data loaded
(4 categories, 15 types, 30 issues).

## 2. Automated suite

```bash
make test             # 39 acceptance tests must pass
make check            # black + flake8 must be clean
```

## 3. Public interface — http://localhost:8080/getitfixed/issues

| What to check | Expected |
|---|---|
| Issues list loads | HTTP 200, map shows Swiss basemap |
| Map tiles visible | Swiss map renders (no ORB console errors) |
| Click **New issue** | Form with map widget opens |
| Place point on map, fill category/type/description, submit | Redirects to confirmation, email captured at `:8082` |
| View an existing issue (`/issues/9`) | Map shows marker, no JS errors |

## 4. Admin interface — http://localhost:8080/getitfixed_admin/issues

| What to check | Expected |
|---|---|
| Issues grid loads | Table with 30 rows, sortable columns |
| Click an issue → Edit | Form opens with map widget and all fields |
| Change status → Save | Status updated, email sent if applicable |
| Add an event/comment | Event appears in the issue's history |

## 5. Private interface — link-only, no list page

Reporters access their issue via the direct link in the confirmation email.
After submitting a public issue (step 3), copy the link from the webmail
(`http://localhost:8082`) and open it — it resolves to
`http://localhost:8080/getitfixed_private/issues/{hash}`.

| What to check | Expected |
|---|---|
| Direct link from email opens | HTTP 200, read-only issue view with status |
| Add an event via the form | Event saved, status update email sent |

## 6. Email flow — http://localhost:8082/webmail/?_task=mail&_mbox=INBOX

Submit a new public issue and verify the confirmation email arrives.
Transition an issue in admin and verify the update email arrives.

## 7. i18n

Click the `fr` label in the footer. Page text switches to French.

## 8. Database

```bash
make psql
```

```sql
SELECT count(*) FROM getitfixed.issue;    -- expect 30
SELECT count(*) FROM getitfixed.category; -- expect 4
```

## 9. Teardown check

```bash
make cleanall         # containers, images, .env removed cleanly
```
