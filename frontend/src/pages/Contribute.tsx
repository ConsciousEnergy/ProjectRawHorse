import { useState } from 'react';
import { submitContribution } from '../services/api';

type ContributionType = 'entity' | 'money_flow' | 'award' | 'foia_target';

function Contribute() {
  const [contributionType, setContributionType] = useState<ContributionType>('entity');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ success: boolean; message: string } | null>(null);

  const [entityData, setEntityData] = useState({
    entity_id: '',
    display_name: '',
    normalized_name: '',
    entity_type: '',
  });

  const [moneyFlowData, setMoneyFlowData] = useState({
    source: '',
    target: '',
    relationship: '',
    amount_usd: '',
    start_date: '',
    source_citation: '',
  });

  const [awardData, setAwardData] = useState({
    award_id: '',
    recipient_name: '',
    awarding_agency: '',
    award_amount: '',
    award_date: '',
    description: '',
  });

  const [foiaData, setFoiaData] = useState({
    target_entity: '',
    agency: '',
    topic: '',
    priority: '',
    notes: '',
  });

  const [contributorName, setContributorName] = useState('');
  const [contributorEmail, setContributorEmail] = useState('');
  const [notes, setNotes] = useState('');

  const resetForms = () => {
    setEntityData({ entity_id: '', display_name: '', normalized_name: '', entity_type: '' });
    setMoneyFlowData({ source: '', target: '', relationship: '', amount_usd: '', start_date: '', source_citation: '' });
    setAwardData({ award_id: '', recipient_name: '', awarding_agency: '', award_amount: '', award_date: '', description: '' });
    setFoiaData({ target_entity: '', agency: '', topic: '', priority: '', notes: '' });
    setNotes('');
  };

  const getCurrentData = (): Record<string, unknown> => {
    if (contributionType === 'entity') return { ...entityData };
    if (contributionType === 'money_flow') {
      return { ...moneyFlowData, amount_usd: moneyFlowData.amount_usd ? parseFloat(moneyFlowData.amount_usd) : undefined };
    }
    if (contributionType === 'award') {
      return { ...awardData, award_amount: awardData.award_amount ? parseFloat(awardData.award_amount) : undefined };
    }
    return { ...foiaData };
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setResult(null);

    try {
      const response = await submitContribution({
        contribution_type: contributionType,
        data: getCurrentData(),
        contributor_name: contributorName || undefined,
        contributor_email: contributorEmail || undefined,
        notes: notes || undefined,
      });
      setResult(response);
      if (response.success) resetForms();
    } catch (error: unknown) {
      const msg = error instanceof Error ? error.message : 'Error submitting contribution';
      setResult({ success: false, message: msg });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="contribute">
      <div className="page-header">
        <h2>Contribute Data</h2>
        <p>Submit new data for review — no account required</p>
      </div>

      <div className="card">
        <h3>Select Contribution Type</h3>
        <div className="tabs">
          <button className={contributionType === 'entity' ? 'active' : ''} onClick={() => setContributionType('entity')}>Entity</button>
          <button className={contributionType === 'money_flow' ? 'active' : ''} onClick={() => setContributionType('money_flow')}>Money Flow</button>
          <button className={contributionType === 'award' ? 'active' : ''} onClick={() => setContributionType('award')}>Award</button>
          <button className={contributionType === 'foia_target' ? 'active' : ''} onClick={() => setContributionType('foia_target')}>FOIA Target</button>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="card">
          <h3>
            {contributionType === 'entity' && 'New Entity'}
            {contributionType === 'money_flow' && 'New Money Flow'}
            {contributionType === 'award' && 'New Federal Award'}
            {contributionType === 'foia_target' && 'New FOIA Target'}
          </h3>

          {contributionType === 'entity' ? (
            <>
              <div className="input-group">
                <label>Entity ID *</label>
                <input type="text" value={entityData.entity_id} onChange={(e) => setEntityData({ ...entityData, entity_id: e.target.value })} required />
              </div>
              <div className="input-group">
                <label>Display Name *</label>
                <input type="text" value={entityData.display_name} onChange={(e) => setEntityData({ ...entityData, display_name: e.target.value })} required />
              </div>
              <div className="input-group">
                <label>Normalized Name *</label>
                <input type="text" value={entityData.normalized_name} onChange={(e) => setEntityData({ ...entityData, normalized_name: e.target.value })} required />
              </div>
              <div className="input-group">
                <label>Entity Type</label>
                <input type="text" value={entityData.entity_type} onChange={(e) => setEntityData({ ...entityData, entity_type: e.target.value })} />
              </div>
            </>
          ) : contributionType === 'money_flow' ? (
            <>
              <div className="input-group">
                <label>Source Entity *</label>
                <input type="text" value={moneyFlowData.source} onChange={(e) => setMoneyFlowData({ ...moneyFlowData, source: e.target.value })} required />
              </div>
              <div className="input-group">
                <label>Target Entity *</label>
                <input type="text" value={moneyFlowData.target} onChange={(e) => setMoneyFlowData({ ...moneyFlowData, target: e.target.value })} required />
              </div>
              <div className="input-group">
                <label>Relationship Type</label>
                <input type="text" value={moneyFlowData.relationship} onChange={(e) => setMoneyFlowData({ ...moneyFlowData, relationship: e.target.value })} placeholder="e.g., M&A, Contract, Investment" />
              </div>
              <div className="input-group">
                <label>Amount (USD)</label>
                <input type="number" value={moneyFlowData.amount_usd} onChange={(e) => setMoneyFlowData({ ...moneyFlowData, amount_usd: e.target.value })} />
              </div>
              <div className="input-group">
                <label>Date</label>
                <input type="date" value={moneyFlowData.start_date} onChange={(e) => setMoneyFlowData({ ...moneyFlowData, start_date: e.target.value })} />
              </div>
              <div className="input-group">
                <label>Source Citation</label>
                <input type="text" value={moneyFlowData.source_citation} onChange={(e) => setMoneyFlowData({ ...moneyFlowData, source_citation: e.target.value })} placeholder="URL or document reference" />
              </div>
            </>
          ) : contributionType === 'award' ? (
            <>
              <div className="input-group">
                <label>Award ID *</label>
                <input type="text" value={awardData.award_id} onChange={(e) => setAwardData({ ...awardData, award_id: e.target.value })} required placeholder="e.g., CONTRACT-2023-001" />
              </div>
              <div className="input-group">
                <label>Recipient Name *</label>
                <input type="text" value={awardData.recipient_name} onChange={(e) => setAwardData({ ...awardData, recipient_name: e.target.value })} required placeholder="Entity or organization name" />
              </div>
              <div className="input-group">
                <label>Awarding Agency *</label>
                <input type="text" value={awardData.awarding_agency} onChange={(e) => setAwardData({ ...awardData, awarding_agency: e.target.value })} required placeholder="e.g., Department of Defense" />
              </div>
              <div className="input-group">
                <label>Award Amount (USD)</label>
                <input type="number" value={awardData.award_amount} onChange={(e) => setAwardData({ ...awardData, award_amount: e.target.value })} placeholder="0.00" />
              </div>
              <div className="input-group">
                <label>Award Date</label>
                <input type="date" value={awardData.award_date} onChange={(e) => setAwardData({ ...awardData, award_date: e.target.value })} />
              </div>
              <div className="input-group">
                <label>Description</label>
                <textarea value={awardData.description} onChange={(e) => setAwardData({ ...awardData, description: e.target.value })} rows={3} placeholder="Brief description of the award or contract" />
              </div>
            </>
          ) : (
            <>
              <div className="input-group">
                <label>Target Entity *</label>
                <input type="text" value={foiaData.target_entity} onChange={(e) => setFoiaData({ ...foiaData, target_entity: e.target.value })} required placeholder="Organization to request from" />
              </div>
              <div className="input-group">
                <label>Agency *</label>
                <input type="text" value={foiaData.agency} onChange={(e) => setFoiaData({ ...foiaData, agency: e.target.value })} required placeholder="e.g., DOD, NASA, DHS" />
              </div>
              <div className="input-group">
                <label>Topic *</label>
                <input type="text" value={foiaData.topic} onChange={(e) => setFoiaData({ ...foiaData, topic: e.target.value })} required placeholder="Subject matter for FOIA request" />
              </div>
              <div className="input-group">
                <label>Priority</label>
                <select value={foiaData.priority} onChange={(e) => setFoiaData({ ...foiaData, priority: e.target.value })}>
                  <option value="">Select priority...</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
              <div className="input-group">
                <label>Additional Notes</label>
                <textarea value={foiaData.notes} onChange={(e) => setFoiaData({ ...foiaData, notes: e.target.value })} rows={4} placeholder="Rationale, background information, or specific items to request" />
              </div>
            </>
          )}
        </div>

        <div className="card">
          <h3>Contributor Information (Optional)</h3>
          <div className="input-group">
            <label>Your Name</label>
            <input type="text" value={contributorName} onChange={(e) => setContributorName(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Your Email</label>
            <input type="email" value={contributorEmail} onChange={(e) => setContributorEmail(e.target.value)} />
          </div>
          <div className="input-group">
            <label>Additional Notes</label>
            <textarea value={notes} onChange={(e) => setNotes(e.target.value)} rows={4} placeholder="Provide any additional context or notes about this contribution" />
          </div>
        </div>

        {result && (
          <div className={`alert ${result.success ? 'alert-success' : 'alert-error'}`}>
            <p>{result.message}</p>
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={loading}>
          {loading ? 'Submitting...' : 'Submit Contribution'}
        </button>
      </form>

      <div className="card">
        <h3>How It Works</h3>
        <ol>
          <li>Fill out the form with accurate, sourced data</li>
          <li>Your contribution is saved for admin review</li>
          <li>Once approved, the data is merged into the live database</li>
          <li>Rejected submissions receive feedback notes</li>
        </ol>
        <p><strong>No account required.</strong> All contributions are subject to review and validation before being published.</p>
      </div>
    </div>
  );
}

export default Contribute;
