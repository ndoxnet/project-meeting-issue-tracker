# Error Code Catalog

> Concept by MrHan (08974747477)
> Codes below are **derived from the source**. Codes the frontend might expect
> but that are **not currently distinct** are listed as *Reserved* with the code
> actually returned today.

Envelope: `{ "error": { "code, message, request_id" } }`. All errors carry a
`request_id`. "Show?" = whether `message` is safe to display directly.

## Authentication / Authorization
| Code | HTTP | Meaning | Frontend behavior | Retry | Show? |
|---|---|---|---|---|---|
| `AUTHENTICATION_FAILED` | 401 | Bad credentials, invalid/expired token, or inactive account (generic on purpose) | Clear token, redirect to login | No | Generic only |
| `AUTHORIZATION_FAILED` | 403 | Role lacks permission | Show "access denied"; hide the action | No | Yes |

> *Reserved (not distinct today):* `INVALID_TOKEN`, `USER_INACTIVE` → currently
> returned as `AUTHENTICATION_FAILED`.

## User
| Code | HTTP | Meaning | Frontend | Retry | Show? |
|---|---|---|---|---|---|
| `NOT_FOUND` | 404 | User (or generic resource) not found | Show not-found | No | Yes |
| `CONFLICT` | 409 | Duplicate username or email (message says which) | Highlight the field | No | Yes |
| `VALIDATION_ERROR` | 422 | Domain rule violation incl. **last-active-admin** guard and password policy | Show message near form | No | Yes |

> *Reserved:* `USER_NOT_FOUND`, `USERNAME_ALREADY_EXISTS`, `EMAIL_ALREADY_EXISTS`,
> `LAST_ADMIN_DEACTIVATION_FORBIDDEN` → today returned as `NOT_FOUND`,
> `CONFLICT`, or `VALIDATION_ERROR` (message disambiguates).

## Issue
| Code | HTTP | Meaning | Frontend | Retry | Show? |
|---|---|---|---|---|---|
| `ISSUE_NOT_FOUND` | 404 | Issue id unknown | Not-found page | No | Yes |
| `ISSUE_ARCHIVED` | 409 | Operation not allowed while archived | Prompt to restore first | No | Yes |
| `ISSUE_ALREADY_CLOSED` | 409 | Edit/close on a closed issue | Prompt to reopen first | No | Yes |
| `ISSUE_NOT_CLOSED` | 409 | Reopen attempted on a non-closed issue | Refresh state | No | Yes |
| `INVALID_STATUS_TRANSITION` | 409 | Not allowed by the state machine (incl. `→CLOSED` via `/status`) | Refresh; offer valid actions | No | Yes |
| `DUE_DATE_BEFORE_RAISED_DATE` | 422 | due/closed date < raised date | Fix the date field | No | Yes |
| `CATEGORY_INACTIVE` | 422 | Category missing/inactive | Pick an active category | No | Yes |
| `RESPONSIBLE_PARTY_INACTIVE` | 422 | Responsible party missing/inactive | Pick active | No | Yes |
| `PIC_USER_INACTIVE` | 422 | PIC user missing/inactive | Pick active user | No | Yes |
| `MEETING_OCCURRENCE_NOT_FOUND` | 404 | Occurrence id unknown | Refresh occurrences | No | Yes |

`POSSIBLE_DUPLICATE` is a **warning** (HTTP 201 create still succeeds), not an error.

## Issue update
| Code | HTTP | Meaning | Frontend | Retry | Show? |
|---|---|---|---|---|---|
| `ISSUE_UPDATE_NOT_FOUND` | 404 | Update id unknown / wrong issue | Refresh timeline | No | Yes |
| `ISSUE_UPDATE_ALREADY_VOIDED` | 409 | Update already voided | Refresh timeline | No | Yes |
| `CURRENT_STATE_NOT_REVERSED` | — | **Warning** on void: current state was not rewound | Prompt for a corrective follow-up | — | Yes |

## Master data
| Code | HTTP | Meaning |
|---|---|---|
| `NOT_FOUND` | 404 | Category/responsible-party/meeting/occurrence/setting not found |
| `CONFLICT` | 409 | Duplicate master-data name |

> *Reserved:* `CATEGORY_NOT_FOUND`, `RESPONSIBLE_PARTY_NOT_FOUND`,
> `MEETING_NOT_FOUND` → returned as `NOT_FOUND` today.

## Attachment
| Code | HTTP | Meaning | Frontend | Retry | Show? |
|---|---|---|---|---|---|
| `ATTACHMENT_NOT_FOUND` | 404 | Missing/removed attachment | Refresh list | No | Yes |
| `ATTACHMENT_TYPE_NOT_ALLOWED` | 415 | MIME not in allow-list | Reject file client-side too | No | Yes |
| `ATTACHMENT_CONTENT_MISMATCH` | 415 | Magic bytes ≠ declared type | Ask for a valid file | No | Yes |
| `ATTACHMENT_TOO_LARGE` | 413 | Exceeds `ATTACHMENT_MAX_MB` | Ask for a smaller file | No | Yes |

## Report
| Code | HTTP | Meaning | Frontend |
|---|---|---|---|
| `EXPORT_LIMIT_EXCEEDED` | 409 | Filtered set exceeds the 10,000-row cap | Ask user to narrow filters |

## Generic
| Code | HTTP | Meaning |
|---|---|---|
| `VALIDATION_ERROR` | 422 | Pydantic request validation or a domain validation |
| `NOT_FOUND` | 404 | Generic not found |
| `CONFLICT` | 409 | Generic state conflict |
| `INTERNAL_ERROR` | 500 | Unexpected server error (no traceback exposed; use `request_id`) |
| `HTTP_ERROR` | 4xx | Fallback for uncategorized HTTP exceptions |
