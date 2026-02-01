function About() {
  return (
    <div className="about">
      <div className="page-header">
        <h2>About</h2>
        <p>Project RawHorse - Open Source Research Tool</p>
      </div>

      <div className="card">
        <h3>Project Overview</h3>
        <p>
          Project RawHorse is an open-source application for exploring and analyzing publicly 
          available data related to Unidentified Anomalous Phenomena (UAP) research, federal 
          contracting, and related entities.
        </p>
      </div>

      <div className="card">
        <h3>Data Sources and Attribution</h3>
        <p>
          This project incorporates research and analysis from the following sources. We are deeply 
          grateful to the researchers whose work has made this project possible.
        </p>
        <div style={{ marginTop: '16px' }}>
          <h4 style={{ marginBottom: '8px', color: 'var(--text-secondary)' }}>UAPGerb</h4>
          <p style={{ marginBottom: '12px' }}>
            Channel dedicated to investigating UFO legacy program operations within the U.S. 
            Department of Defense and Intelligence community. Entity relationships, organizational 
            structures, and FOIA targets derived from in-depth transcript analysis.
          </p>
          <ul>
            <li>
              <strong>"The Hidden Wing"</strong> - US Air Force UFO Reverse Engineering Programs (2026)
              <br />
              <a 
                href="https://www.youtube.com/watch?v=-IXSZe4xVv4" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ color: 'var(--primary-color)' }}
              >
                Watch on YouTube
              </a>
              <span style={{ color: 'var(--text-muted)', marginLeft: '8px' }}>
                - Air Force SAF hierarchy, RCO, AFTE, sensitive activities
              </span>
            </li>
            <li style={{ marginTop: '8px' }}>
              <strong>Previous Research (2025)</strong> - NRO, CIA DS&T, FFRDCs, Office of Global Access
            </li>
          </ul>
          <p style={{ marginTop: '12px' }}>
            <a 
              href="https://www.youtube.com/@uapgerb" 
              target="_blank" 
              rel="noopener noreferrer"
              style={{ color: 'var(--primary-color)' }}
            >
              Visit UAPGerb YouTube Channel
            </a>
          </p>
        </div>
        <div style={{ marginTop: '20px' }}>
          <h4 style={{ marginBottom: '8px', color: 'var(--text-secondary)' }}>Government Data Sources</h4>
          <ul>
            <li>USAspending.gov - Federal contract and award data</li>
            <li>SAM.gov - System for Award Management solicitations</li>
            <li>SEC EDGAR - Corporate filings and disclosures</li>
            <li>FOIA Reading Rooms - Declassified documents</li>
          </ul>
        </div>
      </div>

      <div className="card">
        <h3>License</h3>
        <p>
          This project is licensed under the <strong>GNU Affero General Public License v3.0 (AGPL-3.0)</strong>.
        </p>
        <p>
          The AGPL ensures that this software remains free and open source, and that any modifications 
          or network services using this code must also be made available under the same license.
        </p>
      </div>

      <div className="card">
        <h3>Technology Stack</h3>
        <ul>
          <li><strong>Backend:</strong> FastAPI (Python) with SQLite/PostgreSQL database support</li>
          <li><strong>Frontend:</strong> React 18+ with TypeScript and Vite</li>
          <li><strong>Data Visualization:</strong> D3.js, Recharts, react-force-graph-2d</li>
          <li><strong>NLP Processing:</strong> spaCy for entity recognition and extraction</li>
          <li><strong>Data Enrichment:</strong> Web scraping with BeautifulSoup, DuckDuckGo search</li>
          <li><strong>Authentication:</strong> JWT token-based authentication</li>
          <li><strong>Deployment:</strong> Docker Compose with Caddy reverse proxy</li>
          <li><strong>Caching:</strong> Redis for production environments</li>
          <li><strong>GitHub Integration:</strong> PyGithub for automated PR creation</li>
        </ul>
      </div>

      <div className="card">
        <h3>Features</h3>
        <ul>
          <li>Local-first data processing (no external servers required)</li>
          <li>Comprehensive data browsing with advanced filtering</li>
          <li>Interactive network graph visualization (force-directed)</li>
          <li>Sankey flow diagrams for money/relationship flows</li>
          <li>Intelligence Stack hierarchy filter (6 levels)</li>
          <li>Automated entity extraction from transcripts</li>
          <li>Financial flow and materials transfer enrichment</li>
          <li>Source credibility scoring and validation</li>
          <li>Multiple export formats (CSV, JSON, PDF)</li>
          <li>Community contributions via GitHub PR automation</li>
          <li>Cross-platform desktop application</li>
          <li>Production-ready Docker deployment</li>
        </ul>
      </div>

      <div className="card">
        <h3>Contributing</h3>
        <p>
          We welcome contributions from the community! You can contribute by:
        </p>
        <ul>
          <li>Adding new data entries through the Contribute page</li>
          <li>Reporting issues on GitHub</li>
          <li>Submitting code improvements</li>
          <li>Improving documentation</li>
        </ul>
      </div>

      <div className="card">
        <h3>Disclaimer</h3>
        <p>
          This application uses only publicly available data from official government sources. 
          Users are responsible for verifying accuracy and compliance with all applicable laws 
          and regulations.
        </p>
      </div>
    </div>
  );
}

export default About;
