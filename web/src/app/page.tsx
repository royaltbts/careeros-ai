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

type OpportunitiesResponse = {
  generated_at: string;
  total_opportunities: number;
  opportunities: Opportunity[];
};

const signals = [
  "Customer communication",
  "Stakeholder management",
  "Process improvement",
  "People leadership",
];

export default function Home() {
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
        setError("Unable to load CareerOS opportunities.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  return (
    <main className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">C</div>
          <div>
            <strong>CareerOS</strong>
            <span>Career operating system</span>
          </div>
        </div>

        <nav className="nav">
          <a className="nav-item active" href="#">
            Overview
          </a>
          <a className="nav-item" href="#">
            Opportunities
          </a>
          <a className="nav-item" href="#">
            Candidate Truth
          </a>
          <a className="nav-item" href="#">
            Evidence
          </a>
          <a className="nav-item" href="#">
            Applications
          </a>
        </nav>

        <div className="sidebar-footer">
          <span className="status-dot" />
          CareerOS engine connected
        </div>
      </aside>

      <section className="content">
        <header className="topbar">
          <div>
            <p className="eyebrow">Career intelligence</p>
            <h1>Your career command center</h1>
          </div>
          <button className="profile-button">AS</button>
        </header>

        <section className="hero">
          <div>
            <span className="hero-label">CUSTOMER SUCCESS</span>
            <h2>Find the opportunities where your evidence is strongest.</h2>
            <p>
              CareerOS combines your verified experience, job requirements,
              company intelligence, and human review before an application
              moves forward.
            </p>
          </div>
          <button className="primary-button">Discover opportunities</button>
        </section>

        <section className="metrics">
          <article className="metric-card">
            <span>Opportunities</span>
            <strong>{opportunities.length}</strong>
            <small>discovered</small>
          </article>
          <article className="metric-card">
            <span>Strong matches</span>
            <strong>
              {opportunities.filter((item) => item.fit_score >= 80).length}
            </strong>
            <small>evidence-backed</small>
          </article>
          <article className="metric-card">
            <span>Under review</span>
            <strong>
              {
                opportunities.filter(
                  (item) => item.company_strategic_fit.human_review_required,
                ).length
              }
            </strong>
            <small>human decision needed</small>
          </article>
          <article className="metric-card">
            <span>Applications</span>
            <strong>0</strong>
            <small>pending approval</small>
          </article>
        </section>

        <section className="workspace-grid">
          <div className="panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Opportunity intelligence</p>
                <h3>Recommended opportunities</h3>
              </div>
              <a href="#">View all</a>
            </div>

            <div className="opportunity-list">
              {loading && <p>Loading CareerOS opportunities...</p>}

              {error && <p>{error}</p>}

              {!loading &&
                !error &&
                opportunities.map((opportunity) => (
                  <a
                    className="opportunity"
                    key={opportunity.job_id}
                    href={`/opportunities/${opportunity.job_id}`}
                  >
                    <div className="company-mark">
                      {opportunity.company.charAt(0)}
                    </div>

                    <div className="opportunity-main">
                      <strong>{opportunity.title}</strong>
                      <span>
                        {opportunity.company} · {opportunity.location}
                      </span>
                    </div>

                    <div className="fit">
                      <strong>{Math.round(opportunity.fit_score)}</strong>
                      <span>fit</span>
                    </div>

                    <span className="badge strong">
                      {opportunity.priority}
                    </span>
                  </a>
                ))}

              {!loading && !error && opportunities.length === 0 && (
                <p>No opportunities discovered yet.</p>
              )}
            </div>
          </div>

          <div className="panel truth-panel">
            <div className="panel-header">
              <div>
                <p className="eyebrow">Candidate truth</p>
                <h3>Verified strengths</h3>
              </div>
              <span className="verified">VERIFIED</span>
            </div>

            <div className="signal-list">
              {signals.map((signal) => (
                <div className="signal" key={signal}>
                  <span>✓</span>
                  {signal}
                </div>
              ))}
            </div>

            <div className="truth-note">
              <strong>3 evidence gaps</strong>
              <p>
                SaaS experience, CRM expertise, and enterprise account
                ownership are not currently verified.
              </p>
            </div>
          </div>
        </section>

        <section className="review-banner">
          <div>
            <span className="eyebrow">Human-in-the-loop</span>
            <h3>Nothing leaves CareerOS without your approval.</h3>
            <p>
              Review evidence, positioning, and application claims before
              external action is authorized.
            </p>
          </div>
          <button className="secondary-button">Open approval center</button>
        </section>
      </section>
    </main>
  );
}
