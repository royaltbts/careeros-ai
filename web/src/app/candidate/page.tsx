"use client";

import { useEffect, useState } from "react";

type Candidate = {
  career_direction: {
    primary: string;
    target_roles: string[];
    geography: string;
  };
  experience: {
    years: string;
    current_background: string;
    people_management: boolean;
    project_management: boolean;
    lean_six_sigma: boolean;
  };
  customer_experience: {
    external_clients: {
      company: string;
      relationship: string;
      scope: string;
    }[];
    customer_facing_activities: string[];
    customer_issues_handled: string[];
  };
  customer_success_metrics: string[];
  improvement_experience: {
    initiative: string;
    problem: string;
    action: string[];
    objective: string;
  }[];
  strengths: string[];
  excluded_skills: string[];
  truth_rules: string[];
};

export default function CandidatePage() {
  const [candidate, setCandidate] = useState<Candidate | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetch("/api/candidate")
      .then((response) => {
        if (!response.ok) {
          throw new Error("Failed to load candidate truth");
        }
        return response.json();
      })
      .then((data: Candidate) => {
        setCandidate(data);
      })
      .catch(() => {
        setError("Unable to load Candidate Truth.");
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) {
    return <main className="detail-page">Loading Candidate Truth...</main>;
  }

  if (error || !candidate) {
    return <main className="detail-page">{error}</main>;
  }

  return (
    <main className="detail-page">
      <a className="back-link" href="/">
        ← Back to CareerOS
      </a>

      <section className="detail-hero">
        <div>
          <span className="hero-label">CANDIDATE TRUTH</span>
          <h1>{candidate.career_direction.primary}</h1>
          <p>{candidate.experience.current_background}</p>
        </div>

        <span className="verified">VERIFIED PROFILE</span>
      </section>

      <section className="detail-metrics">
        <article className="metric-card">
          <span>Experience</span>
          <strong>{candidate.experience.years}</strong>
          <small>professional experience</small>
        </article>

        <article className="metric-card">
          <span>People management</span>
          <strong>{candidate.experience.people_management ? "Yes" : "No"}</strong>
          <small>verified profile attribute</small>
        </article>

        <article className="metric-card">
          <span>Project management</span>
          <strong>{candidate.experience.project_management ? "Yes" : "No"}</strong>
          <small>verified profile attribute</small>
        </article>

        <article className="metric-card">
          <span>Lean Six Sigma</span>
          <strong>{candidate.experience.lean_six_sigma ? "Yes" : "No"}</strong>
          <small>verified profile attribute</small>
        </article>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <p className="eyebrow">Career direction</p>
          <h2>Target roles</h2>

          <div className="signal-list">
            {candidate.career_direction.target_roles.map((role) => (
              <div className="signal" key={role}>
                <span>→</span>
                {role}
              </div>
            ))}
          </div>
        </div>

        <div className="panel">
          <p className="eyebrow">Customer success</p>
          <h2>Core metrics</h2>

          <div className="signal-list">
            {candidate.customer_success_metrics.map((metric) => (
              <div className="signal" key={metric}>
                <span>✓</span>
                {metric}
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="panel">
        <p className="eyebrow">Verified strengths</p>
        <h2>Evidence-backed capabilities</h2>

        <div className="signal-list">
          {candidate.strengths.map((strength) => (
            <div className="signal" key={strength}>
              <span>✓</span>
              {strength}
            </div>
          ))}
        </div>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <p className="eyebrow">Customer experience</p>
          <h2>External client projects</h2>

          {candidate.customer_experience.external_clients.map((client) => (
            <div className="research-row" key={client.company}>
              <div>
                <strong>{client.company}</strong>
                <p>{client.scope}</p>
              </div>
              <span>{client.relationship}</span>
            </div>
          ))}
        </div>

        <div className="panel">
          <p className="eyebrow">Customer-facing work</p>
          <h2>Activities</h2>

          <div className="signal-list">
            {candidate.customer_experience.customer_facing_activities.map(
              (activity) => (
                <div className="signal" key={activity}>
                  <span>✓</span>
                  {activity}
                </div>
              ),
            )}
          </div>
        </div>
      </section>

      <section className="detail-grid">
        <div className="panel">
          <p className="eyebrow">Customer experience</p>
          <h2>Issues handled</h2>
          <div className="signal-list">
            {candidate.customer_experience.customer_issues_handled.map(
              (issue) => (
                <div className="signal" key={issue}>
                  <span>✓</span>
                  {issue}
                </div>
              ),
            )}
          </div>
        </div>

        <div className="panel">
          <p className="eyebrow">Continuous improvement</p>
          <h2>Improvement initiatives</h2>
          {candidate.improvement_experience.map((initiative) => (
            <div className="improvement-item" key={initiative.initiative}>
              <strong>{initiative.initiative}</strong>
              <p>{initiative.problem}</p>
              <div className="improvement-actions">
                {initiative.action.map((action) => (
                  <span key={action}>{action}</span>
                ))}
              </div>
              <small>{initiative.objective}</small>
            </div>
          ))}
        </div>
      </section>

      <section className="panel truth-boundary-panel">
        <div className="truth-boundary-header">
          <div>
            <p className="eyebrow">Truth boundary</p>
            <h2>Excluded skills</h2>
          </div>
          <span className="boundary-badge">DO NOT CLAIM</span>
        </div>

        <p className="truth-boundary-description">
          These capabilities are explicitly excluded from Candidate Truth and
          must not be presented as expertise.
        </p>

        <div className="excluded-skill-list">
          {candidate.excluded_skills.map((skill) => (
            <span className="excluded-skill" key={skill}>
              × {skill}
            </span>
          ))}
        </div>
      </section>

      <section className="review-banner">
        <div>
          <span className="eyebrow">CareerOS guardrails</span>
          <h3>Candidate Truth is the source of truth.</h3>
          <p>
            CareerOS must not fabricate experience, convert short-term projects
            into account ownership, or claim excluded skills as expertise.
          </p>
        </div>
      </section>
    </main>
  );
}
