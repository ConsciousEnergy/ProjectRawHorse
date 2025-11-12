import { 
  exportEntitiesCSV, 
  exportMoneyFlowsCSV, 
  exportAwardsCSV,
  exportEntitiesJSON,
  exportSummaryPDF
} from '../services/api';

function Export() {
  return (
    <div className="export">
      <div className="page-header">
        <h2>Export Data</h2>
        <p>Download data in various formats</p>
      </div>

      <div className="card">
        <h3>Export to CSV</h3>
        <p>Download data in comma-separated values format, compatible with Excel and other spreadsheet software.</p>
        <div className="export-buttons">
          <button onClick={exportEntitiesCSV} className="btn btn-primary">
            Export Entities (CSV)
          </button>
          <button onClick={exportMoneyFlowsCSV} className="btn btn-primary">
            Export Money Flows (CSV)
          </button>
          <button onClick={exportAwardsCSV} className="btn btn-primary">
            Export Awards (CSV)
          </button>
        </div>
      </div>

      <div className="card">
        <h3>Export to JSON</h3>
        <p>Download data in JSON format for programmatic access and integration with other tools.</p>
        <div className="export-buttons">
          <button onClick={exportEntitiesJSON} className="btn btn-primary">
            Export Entities (JSON)
          </button>
        </div>
      </div>

      <div className="card">
        <h3>Export Reports (PDF)</h3>
        <p>Generate formatted PDF reports with summary statistics and visualizations.</p>
        <div className="export-buttons">
          <button onClick={exportSummaryPDF} className="btn btn-primary">
            Export Summary Report (PDF)
          </button>
        </div>
      </div>

      <div className="card">
        <h3>Export Tips</h3>
        <ul>
          <li>CSV files can be opened in Excel, Google Sheets, or any spreadsheet software</li>
          <li>JSON files are ideal for importing into databases or custom applications</li>
          <li>PDF reports provide a formatted overview for sharing and presentations</li>
          <li>All exports reflect the current state of the database</li>
          <li>Large exports may take a few moments to generate</li>
        </ul>
      </div>
    </div>
  );
}

export default Export;
