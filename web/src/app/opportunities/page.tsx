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
    decision_ready_fit: number;
    assessment: string;
    research_status: string;
    human_review_required: boolean;
  };
};

type OpportunitiesResponse = {
  opportunities: Opportunity[];
};

export default function OpportunitiesPage() {
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/opportunities")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load opportunities");
        }
        return response.json();
      })
      .then((data: OpportunitiesResponse) => {
        setOpportunities(data.opportunities);
      })
      .catch(() => {
        setError("Unable to load opportunities.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <main className="detail-page">
      <a className="back-link" href="/">
        ← Overview
      </a>

      <header className="detail-hero">
        <div>
          <p className="eyebrow">Opportunity portfolio</p>
          <h1>Career opportunities</h1>
          <p>
            Review discovered roles using evidence-backed fit, decision-ready
            fit, company research, and human review requirements.
          </p>
        </div>
      </header>

      {loading && <div className="panel">Loading opportunities...</div>}

      {error && <div className="panel">{error}</div>}

      {!loading && !error && opportunities.length === 0 && (
        <div className="panel">
          <h3>No opportunities yet</h3>
          <p>
            CareerOS has not discovered any opportunities in the current
            portfolio.
          </p>
        </div>
      )}

      {!loading && !error && opportunities.length > 0 && (
        <section className="detail-grid opportunity-portfolio">
          {opportunities.map((opportunity) => (
            <a
              className="panel opportunity-card"
              href={`/opportunities/${opportunity.job_id}`}
              key={opportunity.job_id}
            >
              <div className="panel-header">
                <div>
                  <p className="eyebrow">{opportunity.company}</p>
                  <h3>{opportunity.title}</h3>
                </div>

                <span className="badge strong">
                  {opportunity.priority}
                </span>
              </div>

              <p className="opportunity-location">{opportunity.location}</p>

              <div className="detail-metrics">
                <div>
                  <span>Opportunity score</span>
                  <strong>{Math.round(opportunity.opportunity_score)}</strong>
                </div>

                <div>
                  <span>Decision-ready fit</span>
                  <strong>
                    {Math.round(
                      opportunity.company_strategic_fit.decision_ready_fit,
                    )}
                  </strong>
                </div>
              </div>

              <div className="research-row">
                <span>
                  Research: {opportunity.company_strategic_fit.research_status}
                </span>
                <span>
                  {opportunity.company_strategic_fit.assessment}
                </span>
              </div>

              <p className="reason">
                {opportunity.company_strategic_fit.human_review_required
                  ? "Human review required before application action."
                  : "Ready for the next CareerOS workflow stage."}
              </p>
            </a>
          ))}
        </section>
      )}
    </main>
  );
}
