import { useState, useCallback } from 'react';
import NetworkGraph, { ENTITY_COLOR_MAP } from '../components/NetworkGraph';
import GraphSidebar from '../components/GraphSidebar';
import RelationshipTimeline from '../components/RelationshipTimeline';

interface GraphDataInfo {
  nodeCount: number;
  linkCount: number;
  inferredCount: number;
  nodeIndex: { name: string; connections: number; type: string }[];
  rawLinks: { source: string; target: string; label?: string; value?: number; count?: number }[];
  totalRawLinks: number;
}

function NetworkGraphPage() {
  const [filterLevels, setFilterLevels] = useState<number[]>([]);
  const [selectedActor, setSelectedActor] = useState<string | null>(null);
  const [colorMode, setColorMode] = useState<'type' | 'proximity'>('type');
  const [showInferred, setShowInferred] = useState(true);
  const [minConnections, setMinConnections] = useState(0);
  const [dataInfo, setDataInfo] = useState<GraphDataInfo>({
    nodeCount: 0,
    linkCount: 0,
    inferredCount: 0,
    nodeIndex: [],
    rawLinks: [],
    totalRawLinks: 0,
  });

  const handleDataReady = useCallback((info: GraphDataInfo) => {
    setDataInfo(info);
  }, []);

  const uniqueTypes = dataInfo.nodeIndex
    .reduce((acc, n) => { if (!acc.includes(n.type)) acc.push(n.type); return acc; }, [] as string[])
    .sort();

  return (
    <div className="network-page-layout" role="main" aria-label="Entity Network Graph">
      {/* Left Sidebar */}
      <GraphSidebar
        nodeCount={dataInfo.nodeCount}
        linkCount={dataInfo.linkCount}
        inferredCount={dataInfo.inferredCount}
        selectedActor={selectedActor}
        onClearActor={() => setSelectedActor(null)}
        onSelectActor={(name) => setSelectedActor(name)}
        nodeIndex={dataInfo.nodeIndex}
        showInferred={showInferred}
        onShowInferredChange={setShowInferred}
        minConnections={minConnections}
        onMinConnectionsChange={setMinConnections}
        colorMode={colorMode}
        onColorModeChange={setColorMode}
        filterLevels={filterLevels}
        onFilterLevelsChange={setFilterLevels}
        colorMap={ENTITY_COLOR_MAP}
        uniqueTypes={uniqueTypes}
      />

      {/* Center: Graph */}
      <div className="network-page-center">
        <NetworkGraph
          filterLevels={filterLevels}
          selectedActor={selectedActor}
          onSelectActor={setSelectedActor}
          colorMode={colorMode}
          showInferred={showInferred}
          minConnections={minConnections}
          onDataReady={handleDataReady}
        />
      </div>

      {/* Right: Timeline (only when actor selected) */}
      {selectedActor && (
        <RelationshipTimeline
          actorName={selectedActor}
          links={dataInfo.rawLinks}
          totalLinks={dataInfo.totalRawLinks}
          onClose={() => setSelectedActor(null)}
          onSelectActor={(name) => setSelectedActor(name)}
        />
      )}

      <style>{`
        .network-page-layout {
          display: flex;
          height: calc(100vh - 60px);
          width: 100%;
          overflow: hidden;
          background: #030712;
        }

        .network-page-center {
          flex: 1;
          min-width: 280px;
          height: 100%;
          position: relative;
        }

        @media (max-width: 700px) {
          .network-page-layout {
            flex-direction: column;
            height: calc(100vh - 50px);
          }
          .network-page-center {
            flex: 1;
          }
        }
      `}</style>
    </div>
  );
}

export default NetworkGraphPage;
