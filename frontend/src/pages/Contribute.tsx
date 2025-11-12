import { useState } from 'react';
import { 
  contributeEntity, 
  contributeMoneyFlow, 
  contributeAward,
  contributeFOIATarget,
  validateGitHubToken 
} from '../services/api';

type ContributionType = 'entity' | 'money-flow' | 'award' | 'foia-target';

function Contribute() {
  const [contributionType, setContributionType] = useState<ContributionType>('entity');
  const [githubToken, setGithubToken] = useState('');
  const [tokenValid, setTokenValid] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);

  // Entity form state
  const [entityData, setEntityData] = useState({
    entity_id: '',
    display_name: '',
    normalized_name: '',
    entity_type: '',
  });

  // Money flow form state
  const [moneyFlowData, setMoneyFlowData] = useState({
    source: '',
    target: '',
    relationship: '',
    amount_usd: '',
    start_date: '',
    source_citation: '',
  });

  // Award form state
  const [awardData, setAwardData] = useState({
    award_id: '',
    recipient_name: '',
    awarding_agency: '',
    award_amount: '',
    award_date: '',
    description: '',
  });

  // FOIA Target form state
  const [foiaData, setFoiaData] = useState({
    target_entity: '',
    agency: '',
    topic: '',
    priority: '',
    notes: '',
  });

  // Contributor info
  const [contributorName, setContributorName] = useState('');
  const [contributorEmail, setContributorEmail] = useState('');
  const [notes, setNotes] = useState('');

  const handleValidateToken = async () => {
    if (!githubToken.trim()) {
      setTokenValid(false);
      return;
    }

    setLoading(true);
    try {
      const response = await validateGitHubToken(githubToken);
      setTokenValid(response.valid);
    } catch (error) {
      setTokenValid(false);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!tokenValid) {
      setResult({ success: false, message: 'Please provide a valid GitHub token' });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      let response;
      if (contributionType === 'entity') {
        response = await contributeEntity(entityData, githubToken);
      } else if (contributionType === 'money-flow') {
        const flowData = {
          ...moneyFlowData,
          amount_usd: moneyFlowData.amount_usd ? parseFloat(moneyFlowData.amount_usd) : undefined,
        };
        response = await contributeMoneyFlow(flowData, githubToken);
      } else if (contributionType === 'award') {
        const award = {
          ...awardData,
          award_amount: awardData.award_amount ? parseFloat(awardData.award_amount) : undefined,
        };
        response = await contributeAward(award, githubToken);
      } else if (contributionType === 'foia-target') {
        response = await contributeFOIATarget(foiaData, githubToken);
      }
      
      setResult(response);
      
      if (response.success) {
        // Reset form
        if (contributionType === 'entity') {
          setEntityData({
            entity_id: '',
            display_name: '',
            normalized_name: '',
            entity_type: '',
          });
        } else if (contributionType === 'money-flow') {
          setMoneyFlowData({
            source: '',
            target: '',
            relationship: '',
            amount_usd: '',
            start_date: '',
            source_citation: '',
          });
        } else if (contributionType === 'award') {
          setAwardData({
            award_id: '',
            recipient_name: '',
            awarding_agency: '',
            award_amount: '',
            award_date: '',
            description: '',
          });
        } else if (contributionType === 'foia-target') {
          setFoiaData({
            target_entity: '',
            agency: '',
            topic: '',
            priority: '',
            notes: '',
          });
        }
        setNotes('');
      }
    } catch (error: any) {
      setResult({ success: false, message: error.message || 'Error submitting contribution' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="contribute">
      <div className="page-header">
        <h2>Contribute Data</h2>
        <p>Submit new data via automated GitHub pull request</p>
      </div>

      <div className="card">
        <h3>GitHub Token Setup</h3>
        <p>
          To contribute data, you need a GitHub personal access token with <code>repo</code> scope.
          <br />
          Generate one at: <a href="https://github.com/settings/tokens" target="_blank" rel="noopener noreferrer">
            https://github.com/settings/tokens
          </a>
        </p>
        <div className="input-group">
          <label>GitHub Personal Access Token</label>
          <input
            type="password"
            value={githubToken}
            onChange={(e) => setGithubToken(e.target.value)}
            placeholder="ghp_..."
          />
          <button 
            onClick={handleValidateToken} 
            className="btn btn-secondary" 
            style={{ marginTop: '10px' }}
            disabled={loading}
          >
            Validate Token
          </button>
          {tokenValid === true && (
            <p style={{ color: '#5afa5a', marginTop: '10px' }}>✓ Token is valid</p>
          )}
          {tokenValid === false && (
            <p style={{ color: '#fa5a5a', marginTop: '10px' }}>✗ Token is invalid</p>
          )}
        </div>
      </div>

      <div className="card">
        <h3>Select Contribution Type</h3>
        <div className="tabs">
          <button
            className={contributionType === 'entity' ? 'active' : ''}
            onClick={() => setContributionType('entity')}
          >
            Entity
          </button>
          <button
            className={contributionType === 'money-flow' ? 'active' : ''}
            onClick={() => setContributionType('money-flow')}
          >
            Money Flow
          </button>
          <button
            className={contributionType === 'award' ? 'active' : ''}
            onClick={() => setContributionType('award')}
          >
            Award
          </button>
          <button
            className={contributionType === 'foia-target' ? 'active' : ''}
            onClick={() => setContributionType('foia-target')}
          >
            FOIA Target
          </button>
        </div>
      </div>

      <form onSubmit={handleSubmit}>
        <div className="card">
          <h3>
            {contributionType === 'entity' && 'New Entity'}
            {contributionType === 'money-flow' && 'New Money Flow'}
            {contributionType === 'award' && 'New Federal Award'}
            {contributionType === 'foia-target' && 'New FOIA Target'}
          </h3>
          
          {contributionType === 'entity' ? (
            <>
              <div className="input-group">
                <label>Entity ID *</label>
                <input
                  type="text"
                  value={entityData.entity_id}
                  onChange={(e) => setEntityData({ ...entityData, entity_id: e.target.value })}
                  required
                />
              </div>
              <div className="input-group">
                <label>Display Name *</label>
                <input
                  type="text"
                  value={entityData.display_name}
                  onChange={(e) => setEntityData({ ...entityData, display_name: e.target.value })}
                  required
                />
              </div>
              <div className="input-group">
                <label>Normalized Name *</label>
                <input
                  type="text"
                  value={entityData.normalized_name}
                  onChange={(e) => setEntityData({ ...entityData, normalized_name: e.target.value })}
                  required
                />
              </div>
              <div className="input-group">
                <label>Entity Type</label>
                <input
                  type="text"
                  value={entityData.entity_type}
                  onChange={(e) => setEntityData({ ...entityData, entity_type: e.target.value })}
                />
              </div>
            </>
          ) : contributionType === 'money-flow' ? (
            <>
              <div className="input-group">
                <label>Source Entity *</label>
                <input
                  type="text"
                  value={moneyFlowData.source}
                  onChange={(e) => setMoneyFlowData({ ...moneyFlowData, source: e.target.value })}
                  required
                />
              </div>
              <div className="input-group">
                <label>Target Entity *</label>
                <input
                  type="text"
                  value={moneyFlowData.target}
                  onChange={(e) => setMoneyFlowData({ ...moneyFlowData, target: e.target.value })}
                  required
                />
              </div>
              <div className="input-group">
                <label>Relationship Type</label>
                <input
                  type="text"
                  value={moneyFlowData.relationship}
                  onChange={(e) => setMoneyFlowData({ ...moneyFlowData, relationship: e.target.value })}
                  placeholder="e.g., M&A, Contract, Investment"
                />
              </div>
              <div className="input-group">
                <label>Amount (USD)</label>
                <input
                  type="number"
                  value={moneyFlowData.amount_usd}
                  onChange={(e) => setMoneyFlowData({ ...moneyFlowData, amount_usd: e.target.value })}
                />
              </div>
              <div className="input-group">
                <label>Date</label>
                <input
                  type="date"
                  value={moneyFlowData.start_date}
                  onChange={(e) => setMoneyFlowData({ ...moneyFlowData, start_date: e.target.value })}
                />
              </div>
              <div className="input-group">
                <label>Source Citation</label>
                <input
                  type="text"
                  value={moneyFlowData.source_citation}
                  onChange={(e) => setMoneyFlowData({ ...moneyFlowData, source_citation: e.target.value })}
                  placeholder="URL or document reference"
                />
              </div>
            </>
          ) : contributionType === 'award' ? (
            <>
              <div className="input-group">
                <label>Award ID *</label>
                <input
                  type="text"
                  value={awardData.award_id}
                  onChange={(e) => setAwardData({ ...awardData, award_id: e.target.value })}
                  required
                  placeholder="e.g., CONTRACT-2023-001"
                />
              </div>
              <div className="input-group">
                <label>Recipient Name *</label>
                <input
                  type="text"
                  value={awardData.recipient_name}
                  onChange={(e) => setAwardData({ ...awardData, recipient_name: e.target.value })}
                  required
                  placeholder="Entity or organization name"
                />
              </div>
              <div className="input-group">
                <label>Awarding Agency *</label>
                <input
                  type="text"
                  value={awardData.awarding_agency}
                  onChange={(e) => setAwardData({ ...awardData, awarding_agency: e.target.value })}
                  required
                  placeholder="e.g., Department of Defense"
                />
              </div>
              <div className="input-group">
                <label>Award Amount (USD)</label>
                <input
                  type="number"
                  value={awardData.award_amount}
                  onChange={(e) => setAwardData({ ...awardData, award_amount: e.target.value })}
                  placeholder="0.00"
                />
              </div>
              <div className="input-group">
                <label>Award Date</label>
                <input
                  type="date"
                  value={awardData.award_date}
                  onChange={(e) => setAwardData({ ...awardData, award_date: e.target.value })}
                />
              </div>
              <div className="input-group">
                <label>Description</label>
                <textarea
                  value={awardData.description}
                  onChange={(e) => setAwardData({ ...awardData, description: e.target.value })}
                  rows={3}
                  placeholder="Brief description of the award or contract"
                />
              </div>
            </>
          ) : contributionType === 'foia-target' ? (
            <>
              <div className="input-group">
                <label>Target Entity *</label>
                <input
                  type="text"
                  value={foiaData.target_entity}
                  onChange={(e) => setFoiaData({ ...foiaData, target_entity: e.target.value })}
                  required
                  placeholder="Organization to request from"
                />
              </div>
              <div className="input-group">
                <label>Agency *</label>
                <input
                  type="text"
                  value={foiaData.agency}
                  onChange={(e) => setFoiaData({ ...foiaData, agency: e.target.value })}
                  required
                  placeholder="e.g., DOD, NASA, DHS"
                />
              </div>
              <div className="input-group">
                <label>Topic *</label>
                <input
                  type="text"
                  value={foiaData.topic}
                  onChange={(e) => setFoiaData({ ...foiaData, topic: e.target.value })}
                  required
                  placeholder="Subject matter for FOIA request"
                />
              </div>
              <div className="input-group">
                <label>Priority</label>
                <select
                  value={foiaData.priority}
                  onChange={(e) => setFoiaData({ ...foiaData, priority: e.target.value })}
                >
                  <option value="">Select priority...</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </select>
              </div>
              <div className="input-group">
                <label>Additional Notes</label>
                <textarea
                  value={foiaData.notes}
                  onChange={(e) => setFoiaData({ ...foiaData, notes: e.target.value })}
                  rows={4}
                  placeholder="Rationale, background information, or specific items to request"
                />
              </div>
            </>
          ) : null}
        </div>

        <div className="card">
          <h3>Contributor Information (Optional)</h3>
          <div className="input-group">
            <label>Your Name</label>
            <input
              type="text"
              value={contributorName}
              onChange={(e) => setContributorName(e.target.value)}
            />
          </div>
          <div className="input-group">
            <label>Your Email</label>
            <input
              type="email"
              value={contributorEmail}
              onChange={(e) => setContributorEmail(e.target.value)}
            />
          </div>
          <div className="input-group">
            <label>Additional Notes</label>
            <textarea
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={4}
              placeholder="Provide any additional context or notes about this contribution"
            />
          </div>
        </div>

        {result && (
          <div className={`alert ${result.success ? 'alert-success' : 'alert-error'}`}>
            <p>{result.message}</p>
            {result.pr_url && (
              <p>
                View your pull request: <a href={result.pr_url} target="_blank" rel="noopener noreferrer">
                  {result.pr_url}
                </a>
              </p>
            )}
          </div>
        )}

        <button type="submit" className="btn btn-primary" disabled={loading || !tokenValid}>
          {loading ? 'Submitting...' : 'Submit Contribution'}
        </button>
      </form>

      <div className="card">
        <h3>How It Works</h3>
        <ol>
          <li>Fill out the form with accurate data</li>
          <li>Your contribution will automatically create a fork of the repository (if needed)</li>
          <li>A new branch will be created with your contribution</li>
          <li>A pull request will be opened for review</li>
          <li>Once reviewed and approved, your contribution will be merged into the main database</li>
        </ol>
        <p><strong>Note:</strong> All contributions are subject to review and validation.</p>
      </div>
    </div>
  );
}

export default Contribute;
