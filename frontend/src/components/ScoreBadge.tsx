import './ScoreBadge.css';

export type ScoreType = 'priority' | 'specificity' | 'likelihood';

interface ScoreBadgeProps {
  score: number | null | undefined;
  type?: ScoreType;
}

function getScoreLevel(score: number, type: ScoreType): 'high' | 'medium' | 'low' {
  if (type === 'likelihood') {
    return score >= 0.6 ? 'high' : score >= 0.3 ? 'medium' : 'low';
  }
  return score >= 0.7 ? 'high' : score >= 0.4 ? 'medium' : 'low';
}

export function ScoreBadge({ score, type = 'priority' }: ScoreBadgeProps) {
  if (score === null || score === undefined) {
    return <span className="score-badge-na">N/A</span>;
  }
  const level = getScoreLevel(score, type);
  const display = (score * 100).toFixed(0);
  return (
    <span className={`score-badge score-badge-${level}`} title={`${display}%`}>
      {display}%
    </span>
  );
}

export default ScoreBadge;
