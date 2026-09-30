"use client";

import { useEffect, useState } from "react";

type EvidenceItem = {
  id: string;
  capability: string;
  claim: string;
  evidence: string;
  source: string;
  evidence_type: string;
  status: string;
  allowed_use: string[];
};

export default function EvidencePage() {
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/evidence")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load evidence");
        }
        return response.json();
      })
      .then((data: EvidenceItem[]) => {
        setEvidence(data);
      })
      .catch(() => {
        setError("Unable to load Evidence Library.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <main className="detail-page">Loading Evidence Library...</main>;
  }

  if (error) {
    return <main className="detail-page">{error}</main>;
  }

  const direct = evidence.filter(
    (item) => item.evidence_type === "Direct experience",
  );

  const transferable = evidence.filter(
    (item) => item.evidence_type === "Transferable experience",
  );

  return (
    <main className="detail-page">
      <a className="back-link" href="/">
        ← Back to CareerOS
      </a>

      <section className="detail-hero">
        <div>
          <span className="hero-label">EVIDENCE LIBRARY</span>
          <h1>Evidence-backed career claims</h1>
          <p>
            Every important CareerOS claim should trace back to verified
            evidence.
          </p>
        </div>

        <span className="verified">VERIFIED EVIDENCE</span>
      </section>

      <section className="detail-metrics">
        <article className="metric-card">
          <span>Total evidence</span>
          <strong>{evidence.length}</strong>
          <small>verified records</small>
        </article>

        <article className="metric-card">
          <span>Direct experience</span>
          <strong>{direct.length}</strong>
          <small>verified evidence</small>
        </article>

        <article className="metric-card">
          <span>Transferable experience</span>
          <strong>{transferable.length}</strong>
          <small>human-review boundary</small>
        </article>

        <article className="metric-card">
          <span>Verified status</span>
          <strong>{evidence.filter((item) => item.status === "VERIFIED").length}</strong>
          <small>evidence records</small>
        </article>
      </section>

      <section className="panel">
        <p className="eyebrow">Evidence records</p>
        <h2>Verified evidence</h2>

        <div className="evidence-list">
          {evidence.map((item) => (
            <article className="evidence-card" key={item.id}>
              <div className="evidence-header">
                <div>
                  <span className="evidence-id">{item.id}</span>
                  <h3>{item.claim}</h3>
                </div>

                <span
                  className={
                    item.evidence_type === "Direct experience"
                      ? "badge strong"
                      : "badge watch"
                  }
                >
                  {item.evidence_type}
                </span>
              </div>

              <p className="evidence-text">{item.evidence}</p>

              <div className="evidence-meta">
                <span>
                  <strong>Capability:</strong> {item.capability}
                </span>
                <span>
                  <strong>Status:</strong> {item.status}
                </span>
              </div>

              <div className="allowed-use">
                <strong>Allowed use</strong>
                <div className="tag-list">
                  {item.allowed_use.map((use) => (
                    <span className="tag" key={use}>
                      {use}
                    </span>
                  ))}
                </div>
              </div>
            </article>
          ))}
        </div>
      </section>

      <section className="review-banner">
        <div>
          <span className="eyebrow">CareerOS evidence boundary</span>
          <h3>Transferable experience is not direct experience.</h3>
          <p>
            Evidence marked as transferable can support positioning, but it
            must not be converted into a stronger claim than the evidence
            supports.
          </p>
        </div>
      </section>
    </main>
  );
}
