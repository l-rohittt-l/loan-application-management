// What this loan type needs, what has been uploaded, and what is still missing.
// Staff can mark a document as verified; anyone who may see the application can add one.

import { useState } from "react";
import { api, errorMessage } from "../api/client";
import { useAuth } from "../auth/AuthContext";
import ErrorBanner from "./ErrorBanner";
import { DOCUMENT_TYPES, checkFileName } from "../utils/validation";
import { formatDate, label } from "../utils/format";

export default function DocumentChecklist({ applicationId, data, onChange }) {
  const { isStaff } = useAuth();
  const [docType, setDocType] = useState("id_proof");
  const [fileName, setFileName] = useState("");
  const [fieldError, setFieldError] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  const { items = [], required = [], missing = [] } = data || {};
  const uploadedTypes = new Set(items.map((d) => d.doc_type));

  async function addDocument(e) {
    e.preventDefault();
    const problem = checkFileName(fileName);
    setFieldError(problem);
    if (problem) return;
    setBusy(true);
    setError("");
    try {
      await api.post(`/applications/${applicationId}/documents`, { doc_type: docType, file_name: fileName.trim() });
      setFileName("");
      onChange?.();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  async function verify(docId) {
    setBusy(true);
    setError("");
    try {
      await api.patch(`/applications/${applicationId}/documents/${docId}/verify`);
      onChange?.();
    } catch (err) {
      setError(errorMessage(err));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div>
      <ErrorBanner message={error} onClose={() => setError("")} />

      <h3 style={{ margin: "0 0 0.5rem" }}>Required for this loan</h3>
      <ul className="checklist">
        {required.map((t) => (
          <li key={t}>
            {uploadedTypes.has(t) ? <span className="tick">✓</span> : <span className="cross">✗</span>}
            <span>{label(t)}</span>
            {missing.includes(t) && <span className="pill">missing</span>}
          </li>
        ))}
      </ul>

      <h3 style={{ margin: "1rem 0 0.5rem" }}>Uploaded</h3>
      {items.length === 0 ? (
        <p className="muted">Nothing uploaded yet.</p>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Type</th><th>File</th><th>Uploaded</th><th>Verified</th>{isStaff && <th />}
              </tr>
            </thead>
            <tbody>
              {items.map((d) => (
                <tr key={d.id}>
                  <td>{label(d.doc_type)}</td>
                  <td>{d.file_name}</td>
                  <td>{formatDate(d.uploaded_at)}</td>
                  <td>{d.verified ? <span className="tick">✓ yes</span> : <span className="muted">not yet</span>}</td>
                  {isStaff && (
                    <td>
                      {!d.verified && (
                        <button type="button" className="btn btn-sm btn-ok" disabled={busy} onClick={() => verify(d.id)}>
                          Mark verified
                        </button>
                      )}
                    </td>
                  )}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <form onSubmit={addDocument} noValidate style={{ marginTop: "1rem" }}>
        <div className="filters">
          <label>
            Document type
            <select value={docType} onChange={(e) => setDocType(e.target.value)}>
              {DOCUMENT_TYPES.map((t) => (
                <option key={t} value={t}>{label(t)}</option>
              ))}
            </select>
          </label>
          <label>
            File name
            <input value={fileName} onChange={(e) => setFileName(e.target.value)} placeholder="aadhaar.pdf" />
          </label>
          <button type="submit" className="btn btn-primary" disabled={busy}>Add document</button>
        </div>
        {fieldError && <span className="field-error">{fieldError}</span>}
        <span className="hint">Phase 1 records the file name only. PDF, JPG or PNG.</span>
      </form>
    </div>
  );
}
