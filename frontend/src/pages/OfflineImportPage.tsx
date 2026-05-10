import { useMemo, useState } from 'react';
import { Download, UploadCloud } from 'lucide-react';
import { getOfflineImportTemplate, uploadOfflineImportFile } from '../services/api';
import type { OfflineImportResult } from '../types';
import './OfflineImportPage.css';

const IMPORT_TYPES = [
  { value: 'entities', label: 'Entities' },
  { value: 'relationships', label: 'Relationships' },
  { value: 'contracts', label: 'Contracts' },
  { value: 'foia', label: 'FOIA Targets' },
];

function OfflineImportPage() {
  const [dataType, setDataType] = useState('entities');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [result, setResult] = useState<OfflineImportResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const canSubmit = useMemo(() => Boolean(selectedFile) && !loading, [selectedFile, loading]);

  const handleDownloadTemplate = async () => {
    try {
      setError(null);
      const template = await getOfflineImportTemplate(dataType);
      const csv = `${template.columns.join(',')}\n`;
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${dataType}_template.csv`;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      setError('Failed to download template.');
      console.error(err);
    }
  };

  const runImport = async (dryRun: boolean) => {
    if (!selectedFile) {
      setError('Please choose a CSV or JSON file first.');
      return;
    }
    try {
      setError(null);
      setLoading(true);
      const response = await uploadOfflineImportFile({
        dataType,
        file: selectedFile,
        dryRun,
      });
      setResult(response);
    } catch (err: any) {
      setError(err?.response?.data?.detail || 'Import request failed.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="offline-import-page fade-in" role="main" aria-label="Offline data import">
      <div className="page-header">
        <h1>Offline Import</h1>
        <p>Import local CSV/JSON files with validation preview before writing to the database.</p>
      </div>

      <div className="offline-import-card card">
        <div className="offline-import-controls">
          <label>
            Data Type
            <select value={dataType} onChange={(e) => setDataType(e.target.value)}>
              {IMPORT_TYPES.map((type) => (
                <option key={type.value} value={type.value}>
                  {type.label}
                </option>
              ))}
            </select>
          </label>

          <button type="button" className="btn btn-secondary" onClick={handleDownloadTemplate}>
            <Download size={16} />
            Download Template
          </button>
        </div>

        <label className="offline-import-file">
          <UploadCloud size={18} />
          <span>{selectedFile ? selectedFile.name : 'Choose CSV/JSON file'}</span>
          <input
            type="file"
            accept=".csv,.json"
            onChange={(e) => setSelectedFile(e.target.files?.[0] || null)}
          />
        </label>

        <div className="offline-import-actions">
          <button type="button" className="btn btn-secondary" disabled={!canSubmit} onClick={() => runImport(true)}>
            Validate Preview
          </button>
          <button
            type="button"
            className="btn btn-primary"
            disabled={!canSubmit}
            onClick={() => runImport(false)}
          >
            Import to Database
          </button>
        </div>

        {error && <div className="alert alert-error">{error}</div>}
      </div>

      {result && (
        <div className="offline-import-report card">
          <h3>Import Report ({result.dry_run ? 'Dry Run' : 'Committed'})</h3>
          <p>
            Total rows: <strong>{result.total_rows}</strong> | Valid: <strong>{result.valid_rows}</strong> | Inserted:{' '}
            <strong>{result.inserted}</strong> | Skipped: <strong>{result.skipped}</strong>
          </p>
          {result.errors.length > 0 && (
            <>
              <h4>Errors</h4>
              <ul className="offline-import-errors">
                {result.errors.slice(0, 20).map((item, idx) => (
                  <li key={`${item}-${idx}`}>{item}</li>
                ))}
              </ul>
            </>
          )}
          <h4>Preview</h4>
          <pre>{JSON.stringify(result.preview.slice(0, 5), null, 2)}</pre>
        </div>
      )}
    </div>
  );
}

export default OfflineImportPage;
