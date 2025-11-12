import './LegalDisclaimer.css';

interface LegalDisclaimerProps {
  onAccept: () => void;
}

function LegalDisclaimer({ onAccept }: LegalDisclaimerProps) {
  return (
    <div className="disclaimer-overlay">
      <div className="disclaimer-modal">
        <div className="disclaimer-header">
          <h2>Legal Disclaimer & Terms</h2>
        </div>
        
        <div className="disclaimer-content">
          <h3>Project RawHorse</h3>
          <p><strong>Version 1.0.0</strong></p>
          
          <h4>License: GNU AGPL v3</h4>
          <p>
            This application is licensed under the GNU Affero General Public License v3.0. 
            You are free to use, modify, and distribute this software under the terms of this license.
          </p>
          
          <h4>Data Responsibility</h4>
          <p>
            <strong>IMPORTANT:</strong> All data in this application is sourced from publicly available 
            government databases and documents. Users are solely responsible for:
          </p>
          <ul>
            <li>Verifying the accuracy of all data before use</li>
            <li>Compliance with export control regulations (ITAR, EAR)</li>
            <li>Ensuring proper handling of any potentially sensitive information</li>
            <li>Following FOIA procedures and regulations when making requests</li>
            <li>Respecting classification guidelines and security protocols</li>
          </ul>
          
          <h4>No Warranty</h4>
          <p>
            THIS SOFTWARE IS PROVIDED "AS IS" WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. 
            The developers assume no liability for any damages, legal issues, or consequences 
            arising from the use of this application or its data.
          </p>
          
          <h4>Public Data Sources Only</h4>
          <p>
            This application exclusively uses publicly available data from official sources including:
          </p>
          <ul>
            <li>USAspending.gov</li>
            <li>SAM.gov (System for Award Management)</li>
            <li>Federal FOIA reading rooms</li>
            <li>DOE, NASA, DHS, and other agency public databases</li>
          </ul>
          
          <h4>Security & Privacy</h4>
          <p>
            All data processing occurs locally on your machine. No analytics or telemetry data 
            is collected. GitHub API requests are only made when you explicitly choose to contribute data.
          </p>
          
          <h4>By Using This Application, You Acknowledge:</h4>
          <ul>
            <li>You have read and understood this disclaimer</li>
            <li>You accept full responsibility for your use of this data</li>
            <li>You will comply with all applicable laws and regulations</li>
            <li>The developers are not liable for any misuse of data</li>
          </ul>
        </div>
        
        <div className="disclaimer-footer">
          <button className="btn btn-primary" onClick={onAccept}>
            I Understand and Accept
          </button>
        </div>
      </div>
    </div>
  );
}

export default LegalDisclaimer;
