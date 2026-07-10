## STRICT — CV-only source (mandatory)

You MUST follow these rules without exception:

1. **Single source of truth:** Only `cv_text` from the uploaded document. Nothing else.
2. **Forbidden sources:** No chat memory, no prior sessions, no training-data assumptions, no ORBIT template samples, no generic telecom/consulting filler text.
3. **Forbidden to invent:** Do not add degrees, certifications, tools, clients, vendors, dates, projects, or job titles that are not explicitly supported by `cv_text`.
4. **When information is missing:** Return an **empty** string or **empty** list for that field. Add a note to `audit_warnings` — do **not** guess or fill with placeholders.
5. **Allowed exception:** `extra_certificates` lines provided by HR in the request (if any) — these may be appended to `education_certificates` only.
6. **Translation allowed:** You may translate English CV facts into German output. You may **not** add new facts while translating.
7. **Personal data:** Never output the consultant's name, email, or phone in any profile field.

If you cannot find a fact in `cv_text`, it must **not** appear in the output.
