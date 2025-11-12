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
          <li><strong>Backend:</strong> FastAPI (Python) with SQLite database</li>
          <li><strong>Frontend:</strong> React with TypeScript</li>
          <li><strong>Data Visualization:</strong> D3.js, Recharts</li>
          <li><strong>GitHub Integration:</strong> PyGithub for automated PR creation</li>
        </ul>
      </div>

      <div className="card">
        <h3>Features</h3>
        <ul>
          <li>Local-first data processing (no external servers)</li>
          <li>Comprehensive data browsing and filtering</li>
          <li>Interactive network visualizations</li>
          <li>Multiple export formats (CSV, JSON, PDF)</li>
          <li>Community contributions via GitHub PR automation</li>
          <li>Cross-platform desktop application</li>
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
