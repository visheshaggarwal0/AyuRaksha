import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Network, Search, ZoomIn, ZoomOut, RotateCcw, 
  ExternalLink, Shield, Leaf, BookOpen, Scale, FileText, 
  Globe, X, Sparkles
} from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { api } from '../../services/api';

export interface GraphNode {
  id: string;
  label: string;
  category: 'botanical' | 'classical_text' | 'statute' | 'section' | 'form' | 'treaty';
  authority: string;
  section_reference: string;
  badge: string;
  official_url: string;
  description: string;
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
}

export interface GraphEdge {
  source: string;
  target: string;
  relation: string;
  rationale: string;
}

interface KnowledgeGraphExplorerProps {
  onSelectCitation?: (citation: any) => void;
  onAskCopilot?: (query: string) => void;
}

const CATEGORY_CONFIG: Record<string, { label: string; color: string; bg: string; border: string; icon: any }> = {
  botanical: {
    label: 'Medicinal Resource',
    color: '#059669',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    icon: Leaf
  },
  classical_text: {
    label: 'First Schedule Book',
    color: '#d97706',
    bg: 'bg-amber-50',
    border: 'border-amber-200',
    icon: BookOpen
  },
  statute: {
    label: 'Primary Statute',
    color: '#14532D',
    bg: 'bg-emerald-50',
    border: 'border-emerald-200',
    icon: Scale
  },
  section: {
    label: 'Statutory Section',
    color: '#4f46e5',
    bg: 'bg-indigo-50',
    border: 'border-indigo-200',
    icon: Shield
  },
  form: {
    label: 'Official Form',
    color: '#0284c7',
    bg: 'bg-sky-50',
    border: 'border-sky-200',
    icon: FileText
  },
  treaty: {
    label: 'International Treaty',
    color: '#9333ea',
    bg: 'bg-purple-50',
    border: 'border-purple-200',
    icon: Globe
  }
};

export function KnowledgeGraphExplorer({ onSelectCitation, onAskCopilot }: KnowledgeGraphExplorerProps) {
  const [nodes, setNodes] = useState<GraphNode[]>([]);
  const [edges, setEdges] = useState<GraphEdge[]>([]);
  const [loading, setLoading] = useState(true);

  // Filter & Search
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedNode, setSelectedNode] = useState<GraphNode | null>(null);
  const [hoveredNodeId, setHoveredNodeId] = useState<string | null>(null);

  // Pan and Zoom transform
  const [transform, setTransform] = useState({ x: 0, y: 0, scale: 0.95 });
  const [isPanning, setIsPanning] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [draggingNodeId, setDraggingNodeId] = useState<string | null>(null);

  const containerRef = useRef<HTMLDivElement>(null);

  // Fetch initial graph
  useEffect(() => {
    setLoading(true);
    api.getKnowledgeGraph()
      .then((data) => {
        if (data && data.nodes && data.edges) {
          const rawNodes: GraphNode[] = data.nodes;
          const total = rawNodes.length;
          const centerX = 500;
          const centerY = 350;
          const radiusByCategory: Record<string, number> = {
            botanical: 260,
            classical_text: 180,
            statute: 90,
            section: 170,
            form: 280,
            treaty: 340
          };

          const angleByCategory: Record<string, { current: number; step: number }> = {};
          const catCounts: Record<string, number> = {};
          rawNodes.forEach(n => { catCounts[n.category] = (catCounts[n.category] || 0) + 1; });
          Object.keys(catCounts).forEach(cat => {
            angleByCategory[cat] = { current: 0, step: (2 * Math.PI) / catCounts[cat] };
          });

          const positionedNodes = rawNodes.map((node, i) => {
            const r = radiusByCategory[node.category] || 200;
            const angleInfo = angleByCategory[node.category];
            const angle = angleInfo ? angleInfo.current : (i / total) * 2 * Math.PI;
            if (angleInfo) angleInfo.current += angleInfo.step;

            return {
              ...node,
              x: centerX + Math.cos(angle) * r + (Math.random() * 20 - 10),
              y: centerY + Math.sin(angle) * r + (Math.random() * 20 - 10),
              vx: 0,
              vy: 0
            };
          });

          setNodes(positionedNodes);
          setEdges(data.edges);
        }
      })
      .catch((err) => {
        console.error('Failed to load knowledge graph:', err);
      })
      .finally(() => setLoading(false));
  }, []);

  // Filtered nodes based on category and search
  const filteredNodes = useMemo(() => {
    return nodes.filter((node) => {
      const matchesCat = selectedCategory === 'all' || node.category === selectedCategory;
      const matchesSearch = !searchQuery.trim() || 
        node.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.authority.toLowerCase().includes(searchQuery.toLowerCase()) ||
        node.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchesCat && matchesSearch;
    });
  }, [nodes, selectedCategory, searchQuery]);

  const filteredNodeIds = useMemo(() => new Set(filteredNodes.map(n => n.id)), [filteredNodes]);

  // Filtered edges where both source and target are in filteredNodeIds
  const filteredEdges = useMemo(() => {
    return edges.filter(e => filteredNodeIds.has(e.source) && filteredNodeIds.has(e.target));
  }, [edges, filteredNodeIds]);

  const nodeMap = useMemo(() => new Map(nodes.map(n => [n.id, n])), [nodes]);

  // Pan and Zoom handlers
  const handleWheel = (e: React.WheelEvent) => {
    e.preventDefault();
    const zoomFactor = e.deltaY < 0 ? 1.08 : 0.92;
    setTransform(prev => ({
      ...prev,
      scale: Math.max(0.4, Math.min(2.5, prev.scale * zoomFactor))
    }));
  };

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.target === containerRef.current || (e.target as HTMLElement).tagName === 'svg') {
      setIsPanning(true);
      setDragStart({ x: e.clientX - transform.x, y: e.clientY - transform.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning) {
      setTransform(prev => ({
        ...prev,
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      }));
    } else if (draggingNodeId) {
      setNodes(prev => prev.map(n => {
        if (n.id === draggingNodeId) {
          return { ...n, x: (e.clientX - transform.x) / transform.scale, y: (e.clientY - transform.y) / transform.scale };
        }
        return n;
      }));
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
    setDraggingNodeId(null);
  };

  const handleResetView = () => {
    setTransform({ x: 0, y: 0, scale: 0.95 });
    setSelectedCategory('all');
    setSearchQuery('');
  };

  // Connected edges for the selected node
  const selectedEdges = useMemo(() => {
    if (!selectedNode) return [];
    return edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id);
  }, [selectedNode, edges]);

  return (
    <div className="h-full flex flex-col space-y-3 select-none">
      {/* Top Controls Toolbar */}
      <div className="bg-white border border-slate-200 rounded-2xl p-3.5 sm:p-4 shadow-card flex flex-wrap items-center justify-between gap-3 shrink-0">
        <div className="flex items-center space-x-3">
          <div className="p-2 bg-emerald-50 text-ayush-forest rounded-xl">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <h2 className="font-extrabold text-sm text-slate-900 font-display">
              Legal Knowledge Graph Explorer
            </h2>
            <p className="text-[11px] text-slate-500 font-medium">
              Interactive network of {nodes.length} statutory nodes & {edges.length} relational legal edges
            </p>
          </div>
        </div>

        {/* Search & Category Filter Pills */}
        <div className="flex flex-wrap items-center gap-2 text-xs">
          <div className="relative">
            <Search className="w-3.5 h-3.5 text-slate-400 absolute left-2.5 top-2.5" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search nodes..."
              className="pl-8 pr-3 py-1.5 rounded-xl border border-slate-200 text-xs focus:outline-none focus:ring-2 focus:ring-ayush-forest/20 w-44 bg-slate-50"
            />
          </div>

          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 text-[11px] font-semibold">
            <button
              onClick={() => setSelectedCategory('all')}
              className={`px-2.5 py-1 rounded-lg transition-all ${
                selectedCategory === 'all' ? 'bg-white text-slate-900 shadow-subtle font-bold' : 'text-slate-600 hover:text-slate-900'
              }`}
            >
              All ({nodes.length})
            </button>
            {Object.entries(CATEGORY_CONFIG).map(([key, config]) => (
              <button
                key={key}
                onClick={() => setSelectedCategory(key)}
                className={`px-2 py-1 rounded-lg transition-all capitalize ${
                  selectedCategory === key ? 'bg-white text-slate-900 shadow-subtle font-bold' : 'text-slate-600 hover:text-slate-900'
                }`}
              >
                {config.label.split(' ')[0]}
              </button>
            ))}
          </div>

          {/* Zoom & Reset Controls */}
          <div className="flex items-center space-x-1 bg-slate-100 p-1 rounded-xl border border-slate-200">
            <button
              onClick={() => setTransform(p => ({ ...p, scale: Math.min(2.5, p.scale * 1.15) }))}
              className="p-1 text-slate-600 hover:text-slate-900 hover:bg-white rounded-lg transition-all"
              title="Zoom In"
            >
              <ZoomIn className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => setTransform(p => ({ ...p, scale: Math.max(0.4, p.scale * 0.85) }))}
              className="p-1 text-slate-600 hover:text-slate-900 hover:bg-white rounded-lg transition-all"
              title="Zoom Out"
            >
              <ZoomOut className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={handleResetView}
              className="p-1 text-slate-600 hover:text-slate-900 hover:bg-white rounded-lg transition-all"
              title="Reset View"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Main Canvas Workspace */}
      <div
        ref={containerRef}
        onWheel={handleWheel}
        onMouseDown={handleMouseDown}
        onMouseMove={handleMouseMove}
        onMouseUp={handleMouseUp}
        className="flex-1 bg-white rounded-2xl border border-slate-200 shadow-card relative overflow-hidden cursor-grab active:cursor-grabbing"
      >
        {loading && (
          <div className="absolute inset-0 bg-white/70 backdrop-blur-xs flex items-center justify-center z-10 text-xs font-bold text-slate-700">
            <span>Loading Knowledge Graph Topology...</span>
          </div>
        )}

        {/* SVG Visualization Canvas */}
        <svg className="w-full h-full absolute inset-0">
          <defs>
            <marker
              id="arrowhead"
              viewBox="0 0 10 10"
              refX="20"
              refY="5"
              markerWidth="6"
              markerHeight="6"
              orient="auto-start-reverse"
            >
              <path d="M 0 0 L 10 5 L 0 10 z" fill="#94A3B8" />
            </marker>
          </defs>

          <g transform={`translate(${transform.x}, ${transform.y}) scale(${transform.scale})`}>
            {/* Edges */}
            {filteredEdges.map((edge, idx) => {
              const src = nodeMap.get(edge.source);
              const tgt = nodeMap.get(edge.target);
              if (!src || !tgt) return null;

              const isHighlighted = selectedNode && (edge.source === selectedNode.id || edge.target === selectedNode.id);

              return (
                <g key={idx}>
                  <line
                    x1={src.x || 0}
                    y1={src.y || 0}
                    x2={tgt.x || 0}
                    y2={tgt.y || 0}
                    stroke={isHighlighted ? '#4F46E5' : '#CBD5E1'}
                    strokeWidth={isHighlighted ? 2.5 : 1.2}
                    strokeOpacity={isHighlighted ? 0.9 : 0.6}
                    strokeDasharray={isHighlighted ? 'none' : '4,2'}
                  />
                  <text
                    x={((src.x || 0) + (tgt.x || 0)) / 2}
                    y={((src.y || 0) + (tgt.y || 0)) / 2 - 3}
                    textAnchor="middle"
                    className="text-[9px] font-mono fill-slate-400 font-bold"
                  >
                    {edge.relation}
                  </text>
                </g>
              );
            })}

            {/* Nodes */}
            {filteredNodes.map((node) => {
              const isSelected = selectedNode?.id === node.id;
              const isHovered = hoveredNodeId === node.id;
              const cfg = CATEGORY_CONFIG[node.category] || CATEGORY_CONFIG.statute;

              return (
                <g
                  key={node.id}
                  transform={`translate(${node.x || 0}, ${node.y || 0})`}
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelectedNode(node);
                  }}
                  onMouseEnter={() => setHoveredNodeId(node.id)}
                  onMouseLeave={() => setHoveredNodeId(null)}
                  className="cursor-pointer"
                >
                  {/* Node Circle */}
                  <circle
                    r={isSelected ? 26 : isHovered ? 22 : 18}
                    fill={cfg.color}
                    fillOpacity={isSelected ? 1 : 0.9}
                    stroke={isSelected ? '#0F172A' : '#FFFFFF'}
                    strokeWidth={isSelected ? 3 : 2}
                    className="transition-all duration-150"
                  />

                  {/* Node Icon or Text Label */}
                  <text
                    textAnchor="middle"
                    dy="4"
                    fill="#FFFFFF"
                    className="text-[10px] font-bold select-none pointer-events-none"
                  >
                    {node.label.slice(0, 3)}
                  </text>

                  {/* Node Title Below */}
                  <text
                    textAnchor="middle"
                    dy={isSelected ? 38 : 32}
                    className={`text-[11px] font-bold select-none pointer-events-none transition-all ${
                      isSelected ? 'fill-slate-900 font-extrabold text-xs' : 'fill-slate-700'
                    }`}
                  >
                    {node.label}
                  </text>
                </g>
              );
            })}
          </g>
        </svg>

        {/* Node Detail Side Inspector Drawer */}
        <AnimatePresence>
          {selectedNode && (
            <motion.div
              initial={{ opacity: 0, x: 50 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 50 }}
              className="absolute right-3 top-3 bottom-3 w-80 bg-white/95 backdrop-blur-md border border-slate-200 rounded-2xl shadow-modal p-5 flex flex-col justify-between overflow-y-auto z-30 space-y-4"
            >
              <div className="space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 pb-3">
                  <span className={`text-[10px] font-extrabold uppercase px-2 py-0.5 rounded-md border ${CATEGORY_CONFIG[selectedNode.category]?.bg} ${CATEGORY_CONFIG[selectedNode.category]?.border} text-slate-800`}>
                    {CATEGORY_CONFIG[selectedNode.category]?.label || selectedNode.category}
                  </span>
                  <button
                    onClick={() => setSelectedNode(null)}
                    className="p-1 text-slate-400 hover:text-slate-800 rounded-lg"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                <div>
                  <h3 className="text-base font-extrabold text-slate-900 font-display leading-snug">
                    {selectedNode.label}
                  </h3>
                  <p className="text-xs text-slate-500 font-medium mt-0.5">
                    Authority: {selectedNode.authority}
                  </p>
                </div>

                {/* Provision Reference */}
                <div className="p-3 bg-slate-50 rounded-xl border border-slate-200 text-xs space-y-1">
                  <span className="text-slate-400 font-bold block text-[10px] uppercase">
                    Statutory Reference
                  </span>
                  <span className="font-mono font-bold text-slate-900">
                    {selectedNode.section_reference}
                  </span>
                </div>

                {/* Description */}
                <div className="space-y-1 text-xs">
                  <span className="text-slate-400 font-bold uppercase text-[10px]">
                    Legal Substance & Role
                  </span>
                  <p className="text-slate-700 leading-relaxed font-medium">
                    {selectedNode.description}
                  </p>
                </div>

                {/* Connected Interlocking Nodes */}
                <div className="space-y-2">
                  <span className="text-slate-400 font-bold uppercase text-[10px] block">
                    Connected Relations ({selectedEdges.length})
                  </span>
                  <div className="space-y-1.5 max-h-36 overflow-y-auto">
                    {selectedEdges.map((edge, idx) => {
                      const isSrc = edge.source === selectedNode.id;
                      const otherId = isSrc ? edge.target : edge.source;
                      const other = nodeMap.get(otherId);
                      if (!other) return null;

                      return (
                        <div
                          key={idx}
                          onClick={() => setSelectedNode(other)}
                          className="p-2.5 rounded-lg border border-slate-200 bg-slate-50 hover:bg-emerald-50 hover:border-emerald-200 cursor-pointer transition-all text-xs"
                        >
                          <div className="flex items-center justify-between font-bold text-slate-800">
                            <span>{other.label}</span>
                            <span className="text-[10px] font-mono text-emerald-800">{edge.relation}</span>
                          </div>
                          <p className="text-[10px] text-slate-500 mt-0.5 truncate">{edge.rationale}</p>
                        </div>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* Inspector Action Buttons */}
              <div className="pt-2 space-y-2 border-t border-slate-100">
                {onSelectCitation && (
                  <button
                    onClick={() => {
                      onSelectCitation({
                        source_id: selectedNode.id,
                        source_title: selectedNode.authority || selectedNode.label,
                        section: selectedNode.section_reference || selectedNode.label,
                        jurisdiction: selectedNode.category === 'treaty' ? 'INT' : 'IN',
                        official_url: selectedNode.official_url,
                        support_score: 1.0,
                        verbatim_quote: selectedNode.description
                      });
                    }}
                    className="w-full flex items-center justify-center space-x-1.5 py-2.5 bg-slate-900 hover:bg-slate-800 text-white text-xs font-bold rounded-xl transition-all shadow-subtle"
                  >
                    <BookOpen className="w-3.5 h-3.5 text-emerald-300" />
                    <span>Inspect Statutory Evidence</span>
                  </button>
                )}

                {onAskCopilot && (
                  <button
                    onClick={() => onAskCopilot(`Explain the statutory relationship between ${selectedNode.label} (${selectedNode.section_reference}) and patentability / ABS compliance under Indian law.`)}
                    className="w-full flex items-center justify-center space-x-1.5 py-2.5 bg-ayush-forest hover:bg-ayush-forestDark text-white text-xs font-bold rounded-xl transition-all shadow-subtle"
                  >
                    <Sparkles className="w-3.5 h-3.5 text-emerald-200" />
                    <span>Ask AyuRaksha about this Node</span>
                  </button>
                )}

                {selectedNode.official_url && (
                  <a
                    href={selectedNode.official_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full flex items-center justify-center space-x-1.5 py-2 bg-slate-100 hover:bg-slate-200 text-slate-800 text-xs font-bold rounded-xl transition-all"
                  >
                    <span>Official Gazette Portal</span>
                    <ExternalLink className="w-3 h-3" />
                  </a>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
