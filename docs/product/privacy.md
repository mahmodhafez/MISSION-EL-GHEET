# Prototype data and consent assumptions

**Read this if…** you're handling speech, scenario storage, hosting or any user data.

Status: Draft assumptions,  · Owner: Amr + Yahya. Last reviewed .

. This documents existing architecture constraints and implementation assumptions. It neither implements storage controls nor certifies compliance with Egyptian or other law. Real farmer records, account connections, speech-provider selection and deployment remain separately gated.

| Data | Minimum purpose and handling assumption | Retention / consent boundary |
| --- | --- | --- |
| Synthetic scenario | Locale, generic Sakha site ID, area/unit, four-season intentions, commitments, relevant soil/water facts with unknowns, revision/evidence references. Use fictional field IDs. | Local synthetic snapshots may support reproducible demonstration; remote session expiry and deletion duration require Amr/Yahya approval before hosting. No indefinite real-data retention is approved. |
| Identity and location | No name, phone, national ID, contact list, herd identity, precise parcel coordinates or GPS is needed for UH-001. The public POWER research point is sufficient. | Do not collect these by default. A real-field study requires a separately justified scope and participant agreement. |
| Speech input | After explaining provider, destination, purpose and applicable retention, request microphone permission and a separate informed choice to transmit. Transcripts propose fields; explicit fact confirmation is distinct. | Raw recordings/transcript retention off by default. Only transient processing is assumed; actual provider handling must be checked for the selected configuration. Browser permission alone does not authorize research recording or third-party retention. Touch/picture recovery remains available. |
| Research participation | Use fictional cases. Explain voluntary participation, purpose, use of observations and how to stop. Recording permission is separate from participation. | Prefer minimal non-identifying observation notes. Agree owner, storage, access and deletion date before collection; no participants or recording consent have been obtained by this audit. |
| Saved results / takeaway audio | Store only references needed for the exact scenario, plan, data and template version. Retain review-draft status. Approved-plan confirmation is distinct from privacy consent. | Synthetic saved evidence can remain reproducible. A future real-data policy must reconcile deletion requests with historical snapshots, backups and audio caches before collection; immutable versioning is not permission to retain personal data forever. |
| Logs | Operational error code, request ID, method/version and anonymous synthetic session scope where necessary. | No raw audio, transcripts, secrets, precise parcel locations or full scenario bodies in routine logs. Set a finite duration before remote operation; enforcement is not yet implemented. |

Before a hosted or real-participant trial, Amr/Yahya must approve collection scope, authorized access, provider/region and transmission terms, concrete session/log/backup retention, deletion behavior and the spoken Arabic/English consent wording. Provider promises must be verified for the chosen service rather than inferred from a general speech document. No service call or personal-data processing was performed here. The approved [architecture](../backend/architecture.md) and [API](../backend/api-contracts.md) remain unchanged.
