"use client";

import { useEffect, useState } from "react";

type Opportunity = {
  job_id: string;
  company: string;
  title: string;
  location: string;
  source_url: string;
  fit_score: number;
  opportunity_score: number;
  priority: string;
  company_strategic_fit: {
    score: number;
    strategic_alignment: number;
    research_confidence: number;
    research_coverage: number;
    research_evidence_confidence: number;
    research_quality: number;
    decision_ready_fit: number;
    assessment: string;
    research_status: string;
    direct_matches: string[];
    related_matches: string[];
    risk_penalty: number;
    reason: string;
    human_review_required: boolean;
  };
  critical_gaps: string[];
  core_gaps: string[];
};

export default function OpportunityPage({
  params,
}: {
  params: Promise<{ jobId: string }>;
}) {
  const [opportunity, setOpportunity] = useState<Opportunity | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    params.then(({ jobId }) =>
      fetch(`/api/opportunities/${jobId}`)
        .then((response) => {
          if (!response.ok) {
            throw new Error("Opportunity not found");
          }
          return response.json();
        })
        .then((data: Opportunity) => {
          setOpportunity(data);
        })
        .catch(() => {
          setError("Unable to load this opportunity.");
        })
        .finally(() => {
          setLoading(false);
        }),
    );
  }, [params]);

  if (loading) {
    return <main className="detail-page">Loading opportunity...</main>;
  }

  if (error || !opportunity) {
    return <main className="detail-page">{error || "Opportunity not found."}</main>;
  }

  const fit = opportunity.company_strategic_fit;

  return (
    <main className="detail-page">
      <a className="back-link" href="/">
        ← Back to CareerOS
      </a>

      <section className="detail-hero">
        <div>
          <span className="hero-label">OPPORTUNITY INTELLIGENCE</span>
          <h1>{opportunity.title}</h1>
          <p>
            {opportunity.company} · {opportunity.location}
          </p>
        </div>

        <span className="badge strong">{opportunity.priority}</span>
      </section>

      <section className="detail-metrics">
        <article className="metric-card">
          <span>Opportunity score</span>
          <strong>{opportunity.opportunity_score}</strong>
          <small>ranked opportunity</small>
        </article>

        <article className="metric-card">
          <span>Decision-ready fit</span>
          <strong>{fit.decision_ready_fit}</strong>
          <small>evidence + research</small>
        </article>

        <article className="metric-card">
          <span>Strategic alignment</span>
          <strong>{fit.strategic_alignment}%</strong>
          <small>career strategy</small>
        </article>

        <article className="metric-card">
          <span>Research confidence</span>
          <strong>{fit.research_confidence}%</strong>
          <small>{fit.research_status}</small>
        </article>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <div className="panel-header">
            <div>
              <p className="eyebrow">Evidence alignment</p>
              <h2>Why CareerOS matched this role</h2>
            </div>
          </div>

          <h3>Direct matches</h3>
          <div className="signal-list">
            {fit.direct_matches.map((match) => (
              <div className="signal" key={match}>
                <span>✓</span>
                {match}
              </div>
            ))}
          </div>

          <h3 className="detail-section-title">Related matches</h3>
          <div className="signal-list">
            {fit.related_matches.map((match) => (
              <div className="signal" key={match}>
                <span>→</span>
                {match}
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <p className="eyebrow">Research quality</p>
          <h2>Company intelligence</h2>

          <div className="research-row">
            <span>Coverage</span>
            <strong>{fit.research_coverage}%</strong>
          </div>

          <div className="research-row">
            <span>Evidence confidence</span>
            <strong>{fit.research_evidence_confidence}%</strong>
          </div>

          <div className="research-row">
            <span>Research quality</span>
            <strong>{fit.research_quality}%</strong>
          </div>

          <p className="reason">{fit.reason}</p>
        </div>
      </section>

      <section className="review-banner">
        <div>
          <span className="eyebrow">Human-in-the-loop</span>
          <h3>Human review required.</h3>
          <p>
            CareerOS will not authorize external application activity without
            human approval.
          </p>
        </div>

        <a
          className="secondary-button"
          href={opportunity.source_url}
          target="_blank"
          rel="noreferrer"
        >
          View original job
        </a>
      </section>
    </main>
  );
}
