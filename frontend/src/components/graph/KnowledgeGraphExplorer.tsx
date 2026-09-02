import React, { useState, useEffect, useRef, useMemo } from 'react';
import { 
  Network, Search, ZoomIn, ZoomOut, RotateCcw, 
  ExternalLink, Shield, Leaf, BookOpen, Scale, FileText, 
  Globe, X, ChevronRight, Sparkles, Filter
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
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
    color: '#4338ca',
    bg: 'bg-indigo-50',
    border: 'border-indigo-200',
    icon: Scale
  },
  section: {
    label: 'Statutory Section',
    color: '#6366f1',
    bg: 'bg-indigo-50',
    border: 'border-indigo-200',
    icon: Shield
  },
  form: {
    label: 'Filing Form',
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

export function KnowledgeGraphExplorer({ onAskCopilot }: KnowledgeGraphExplorerProps) {
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
          // Initialize balanced radial layout positions
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
          // Count categories
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
          if (positionedNodes.length > 0) {
            setSelectedNode(positionedNodes[0]);
          }
        }
      })
      .catch((err) => {
        console.error('Failed to load knowledge graph', err);
      })
      .finally(() => setLoading(false));
  }, []);

  // Compute connected neighbors for active node
  const activeFocusId = hoveredNodeId || selectedNode?.id;

  const connectedNodeIds = useMemo(() => {
    if (!activeFocusId) return new Set<string>();
    const ids = new Set<string>([activeFocusId]);
    edges.forEach((e) => {
      if (e.source === activeFocusId) ids.add(e.target);
      if (e.target === activeFocusId) ids.add(e.source);
    });
    return ids;
  }, [activeFocusId, edges]);

  // Filtered node IDs
  const filteredNodeIds = useMemo(() => {
    return new Set(
      nodes
        .filter((n) => {
          const matchCat = selectedCategory === 'all' || n.category === selectedCategory;
          const matchSearch = !searchQuery || 
            n.label.toLowerCase().includes(searchQuery.toLowerCase()) ||
            n.description.toLowerCase().includes(searchQuery.toLowerCase()) ||
            n.section_reference.toLowerCase().includes(searchQuery.toLowerCase());
          return matchCat && matchSearch;
        })
        .map(n => n.id)
    );
  }, [nodes, selectedCategory, searchQuery]);

  // Drag handlers for canvas panning
  const handleMouseDown = (e: React.MouseEvent) => {
    if (draggingNodeId) return;
    setIsPanning(true);
    setDragStart({ x: e.clientX - transform.x, y: e.clientY - transform.y });
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isPanning && !draggingNodeId) {
      setTransform(prev => ({
        ...prev,
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      }));
    } else if (draggingNodeId) {
      // Update dragged node position directly in local coordinates
      const rect = containerRef.current?.getBoundingClientRect();
      if (!rect) return;
      const mouseX = (e.clientX - rect.left - transform.x) / transform.scale;
      const mouseY = (e.clientY - rect.top - transform.y) / transform.scale;

      setNodes(prev => prev.map(n => n.id === draggingNodeId ? { ...n, x: mouseX, y: mouseY } : n));
    }
  };

  const handleMouseUp = () => {
    setIsPanning(false);
    setDraggingNodeId(null);
  };

  // Zoom controls
  const handleZoom = (delta: number) => {
    setTransform(prev => ({
      ...prev,
      scale: Math.min(Math.max(0.4, prev.scale + delta), 2.2)
    }));
  };

  const handleReset = () => {
    setTransform({ x: 0, y: 0, scale: 0.95 });
  };

  // Node coordinate lookup
  const nodeMap = useMemo(() => {
    const map = new Map<string, GraphNode>();
    nodes.forEach(n => map.set(n.id, n));
    return map;
  }, [nodes]);

  // Edges linked to selected node
  const selectedEdges = useMemo(() => {
    if (!selectedNode) return [];
    return edges.filter(e => e.source === selectedNode.id || e.target === selectedNode.id);
  }, [selectedNode, edges]);

  return (
    <div className="flex flex-col h-full bg-[#FAFAFA] rounded-2xl border border-slate-200 overflow-hidden shadow-card">
      {/* Top Controls Bar */}
      <div className="p-4 bg-white border-b border-slate-200/80 flex flex-wrap items-center justify-between gap-4 z-10 shadow-subtle">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-50 border border-indigo-200 text-indigo-700 flex items-center justify-center font-bold shadow-xs">
            <Network className="w-5 h-5" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h2 className="font-extrabold text-base text-slate-900 font-display tracking-tight">
                Statutory & TK Knowledge Graph
              </h2>
              <span className="px-2 py-0.5 text-[10px] font-mono font-bold bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-md">
                SIH 26045 Multi-Hop
              </span>
            </div>
            <p className="text-xs text-slate-500">
              Interactive relational topology between botanicals, First Schedule books, patent exclusions, and filing forms.
            </p>
          </div>
        </div>

        {/* Search & Filter */}
        <div className="flex items-center space-x-2.5">
          {/* Real-time search */}
          <div className="relative">
            <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search nodes, herbs, sections..."
              className="pl-8 pr-3 py-1.5 bg-slate-50 border border-slate-200 rounded-xl text-xs text-slate-800 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all w-52 sm:w-64"
            />
            {searchQuery && (
              <button 
                onClick={() => setSearchQuery('')}
                className="absolute right-2.5 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              >
                <X className="w-3 h-3" />
              </button>
            )}
          </div>

          {/* Zoom Actions */}
          <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 space-x-1">
            <button
              onClick={() => handleZoom(0.15)}
              className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-white rounded-lg transition-all"
              title="Zoom in"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => handleZoom(-0.15)}
              className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-white rounded-lg transition-all"
              title="Zoom out"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={handleReset}
              className="p-1.5 text-slate-600 hover:text-slate-900 hover:bg-white rounded-lg transition-all"
              title="Reset layout"
            >
              <RotateCcw className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>

      {/* Cluster Category Filter Pills */}
      <div className="px-4 py-2 bg-slate-50 border-b border-slate-200/60 flex items-center gap-2 overflow-x-auto text-xs">
        <span className="text-[11px] font-bold text-slate-400 uppercase tracking-wider flex items-center gap-1 shrink-0 mr-1">
          <Filter className="w-3 h-3" /> Filter:
        </span>
        <button
          onClick={() => setSelectedCategory('all')}
          className={`px-3 py-1 rounded-lg font-bold transition-all shrink-0 ${
            selectedCategory === 'all'
              ? 'bg-slate-900 text-white shadow-xs'
              : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-100'
          }`}
        >
          All Entities ({nodes.length})
        </button>
        {Object.entries(CATEGORY_CONFIG).map(([catKey, config]) => {
          const count = nodes.filter(n => n.category === catKey).length;
          const Icon = config.icon;
          return (
            <button
              key={catKey}
              onClick={() => setSelectedCategory(catKey)}
              className={`px-3 py-1 rounded-lg font-bold flex items-center space-x-1.5 transition-all shrink-0 ${
                selectedCategory === catKey
                  ? 'bg-white text-slate-900 shadow-xs border-2'
                  : 'bg-white/80 text-slate-600 border border-slate-200/80 hover:bg-white'
              }`}
              style={{ borderColor: selectedCategory === catKey ? config.color : undefined }}
            >
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: config.color }} />
              <Icon className="w-3 h-3" style={{ color: config.color }} />
              <span>{config.label} ({count})</span>
            </button>
          );
        })}
      </div>

      {/* Main Canvas + Inspector Split View */}
      <div className="flex-1 flex overflow-hidden relative">
        {/* Canvas Area */}
        <div 
          ref={containerRef}
          onMouseDown={handleMouseDown}
          onMouseMove={handleMouseMove}
          onMouseUp={handleMouseUp}
          onMouseLeave={handleMouseUp}
          className={`flex-1 relative overflow-hidden bg-[#FBFBFC] ${isPanning ? 'cursor-grabbing' : 'cursor-grab'} select-none`}
        >
          {/* Grid Background Pattern */}
          <div 
            className="absolute inset-0 pointer-events-none opacity-[0.35]" 
            style={{
              backgroundImage: 'radial-gradient(circle, #94a3b8 0.75px, transparent 0.75px)',
              backgroundSize: '24px 24px',
              transform: `translate(${transform.x % 24}px, ${transform.y % 24}px)`
            }} 
          />

          {/* SVG Graph Layer */}
          <svg 
            className="w-full h-full absolute inset-0"
            style={{
              transform: `translate(${transform.x}px, ${transform.y}px) scale(${transform.scale})`,
              transformOrigin: '0 0',
              transition: isPanning || draggingNodeId ? 'none' : 'transform 0.15s ease-out'
            }}
          >
            <defs>
              {/* Arrowhead markers for relations */}
              <marker
                id="arrowhead-default"
                viewBox="0 0 10 10"
                refX="22"
                refY="5"
                markerWidth="6"
                markerHeight="6"
                orient="auto"
              >
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#cbd5e1" />
              </marker>
              <marker
                id="arrowhead-highlight"
                viewBox="0 0 10 10"
                refX="22"
                refY="5"
                markerWidth="7"
                markerHeight="7"
                orient="auto"
              >
                <path d="M 0 1 L 10 5 L 0 9 z" fill="#4f46e5" />
              </marker>
            </defs>

            {/* 1. EDGES */}
            <g className="edges">
              {edges.map((edge, idx) => {
                const sNode = nodeMap.get(edge.source);
                const tNode = nodeMap.get(edge.target);
                if (!sNode || !tNode) return null;

                const isConnectedToFocus = activeFocusId && (edge.source === activeFocusId || edge.target === activeFocusId);
                const isDimmed = activeFocusId && !isConnectedToFocus;

                const sx = sNode.x || 0;
                const sy = sNode.y || 0;
                const tx = tNode.x || 0;
                const ty = tNode.y || 0;

                // Midpoint for relation label
                const mx = (sx + tx) / 2;
                const my = (sy + ty) / 2;

                return (
                  <g key={`edge-${idx}`} className="transition-opacity duration-300" style={{ opacity: isDimmed ? 0.12 : 1 }}>
                    <line
                      x1={sx}
                      y1={sy}
                      x2={tx}
                      y2={ty}
                      stroke={isConnectedToFocus ? '#4f46e5' : '#cbd5e1'}
                      strokeWidth={isConnectedToFocus ? 2.5 : 1.5}
                      strokeDasharray={isConnectedToFocus ? 'none' : '4 3'}
                      markerEnd={isConnectedToFocus ? 'url(#arrowhead-highlight)' : 'url(#arrowhead-default)'}
                    />
                    {/* Edge Label on hover/select */}
                    {isConnectedToFocus && (
                      <g transform={`translate(${mx}, ${my})`}>
                        <rect
                          x={-40}
                          y={-10}
                          width={80}
                          height={18}
                          rx={9}
                          fill="#ffffff"
                          stroke="#4f46e5"
                          strokeWidth={1}
                          className="shadow-xs"
                        />
                        <text
                          x={0}
                          y={2}
                          textAnchor="middle"
                          fontSize="9"
                          fontWeight="700"
                          fill="#4338ca"
                          className="font-mono tracking-tight select-none"
                        >
                          {edge.relation}
                        </text>
                      </g>
                    )}
                  </g>
                );
              })}
            </g>

            {/* 2. NODES */}
            <g className="nodes">
              {nodes.map((node) => {
                const isSelected = selectedNode?.id === node.id;
                const isHovered = hoveredNodeId === node.id;
                const isConnected = connectedNodeIds.has(node.id);
                const isFilteredOut = !filteredNodeIds.has(node.id);
                const isDimmed = isFilteredOut || (activeFocusId && !isConnected);

                const config = CATEGORY_CONFIG[node.category] || CATEGORY_CONFIG.statute;
                const nx = node.x || 0;
                const ny = node.y || 0;
                const radius = node.category === 'statute' ? 24 : node.category === 'section' ? 20 : 18;

                return (
                  <g
                    key={node.id}
                    transform={`translate(${nx}, ${ny})`}
                    className="cursor-pointer transition-opacity duration-300"
                    style={{ opacity: isDimmed ? 0.18 : 1 }}
                    onMouseEnter={() => setHoveredNodeId(node.id)}
                    onMouseLeave={() => setHoveredNodeId(null)}
                    onClick={(e) => {
                      e.stopPropagation();
                      setSelectedNode(node);
                    }}
                    onMouseDown={(e) => {
                      e.stopPropagation();
                      setDraggingNodeId(node.id);
                    }}
                  >
                    {/* Outer Glowing Pulse on selection/hover */}
                    {(isSelected || isHovered) && (
                      <circle
                        r={radius + 8}
                        fill="none"
                        stroke={config.color}
                        strokeWidth={3}
                        strokeOpacity={0.35}
                        className="animate-pulse"
                      />
                    )}

                    {/* Main Node Circle */}
                    <circle
                      r={radius}
                      fill="#ffffff"
                      stroke={isSelected ? config.color : isHovered ? config.color : '#e2e8f0'}
                      strokeWidth={isSelected ? 3.5 : 2}
                      className="shadow-md transition-all"
                    />

                    {/* Category Center Color Pip */}
                    <circle
                      r={radius - 6}
                      fill={config.color}
                      opacity={0.15}
                    />
                    <circle
                      r={6}
                      fill={config.color}
                    />

                    {/* Node Text Label */}
                    <text
                      y={radius + 14}
                      textAnchor="middle"
                      className="font-bold text-[11px] select-none font-display pointer-events-none fill-slate-800"
                    >
                      {node.label.length > 22 ? `${node.label.substring(0, 20)}…` : node.label}
                    </text>

                    {/* Sub-badge */}
                    <text
                      y={radius + 25}
                      textAnchor="middle"
                      className="font-mono text-[9px] select-none pointer-events-none fill-slate-400 font-semibold"
                    >
                      {node.badge}
                    </text>
                  </g>
                );
              })}
            </g>
          </svg>

          {/* Quick Help Overlay */}
          <div className="absolute bottom-3 left-3 bg-white/90 backdrop-blur-sm px-3 py-1.5 rounded-xl border border-slate-200 text-[10px] text-slate-500 font-mono flex items-center space-x-2 shadow-xs">
            <span>💡 Click node to inspect</span>
            <span>•</span>
            <span>Drag nodes to re-arrange</span>
            <span>•</span>
            <span>Scroll/drag canvas to pan</span>
          </div>
        </div>

        {/* Right Node Inspector Drawer */}
        <AnimatePresence>
          {selectedNode && (
            <motion.div
              initial={{ width: 0, opacity: 0 }}
              animate={{ width: 380, opacity: 1 }}
              exit={{ width: 0, opacity: 0 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="bg-white border-l border-slate-200 flex flex-col justify-between overflow-y-auto z-10 shadow-lg"
            >
              <div className="p-6 space-y-6">
                {/* Header with Close */}
                <div className="flex items-start justify-between">
                  <div className="space-y-1">
                    <span 
                      className="px-2.5 py-1 rounded-md text-[10px] font-bold tracking-wider uppercase border inline-flex items-center space-x-1"
                      style={{
                        backgroundColor: `${CATEGORY_CONFIG[selectedNode.category]?.color}15`,
                        color: CATEGORY_CONFIG[selectedNode.category]?.color,
                        borderColor: `${CATEGORY_CONFIG[selectedNode.category]?.color}30`
                      }}
                    >
                      <span>{CATEGORY_CONFIG[selectedNode.category]?.label}</span>
                    </span>
                    <h3 className="font-extrabold text-lg text-slate-900 font-display leading-tight pt-1">
                      {selectedNode.label}
                    </h3>
                  </div>
                  <button
                    onClick={() => setSelectedNode(null)}
                    className="p-1.5 text-slate-400 hover:text-slate-700 hover:bg-slate-100 rounded-xl transition-all"
                  >
                    <X className="w-4 h-4" />
                  </button>
                </div>

                {/* Authority & Legal Reference */}
                <div className="bg-slate-50 p-4 rounded-xl border border-slate-100 space-y-2">
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-500 font-medium">Statutory Provision:</span>
                    <span className="font-mono font-bold text-slate-800 bg-white px-2 py-0.5 rounded border border-slate-200">
                      {selectedNode.section_reference}
                    </span>
                  </div>
                  <div className="flex items-center justify-between text-[11px]">
                    <span className="text-slate-500 font-medium">Authoritative Source:</span>
                    <span className="font-bold text-slate-700 truncate max-w-[180px]" title={selectedNode.authority}>
                      {selectedNode.authority}
                    </span>
                  </div>
                </div>

                {/* Substantive Description */}
                <div className="space-y-2">
                  <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                    Legal & Taxonomic Substance
                  </p>
                  <p className="text-xs text-slate-700 leading-relaxed bg-slate-50/50 p-3.5 rounded-xl border border-slate-100">
                    {selectedNode.description}
                  </p>
                </div>

                {/* Connected Relational Nodes */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <p className="text-xs font-bold text-slate-400 uppercase tracking-widest">
                      Interlocking Relations ({selectedEdges.length})
                    </p>
                    <span className="text-[10px] font-mono text-indigo-600">Multi-Hop Path</span>
                  </div>

                  <div className="space-y-2 max-h-56 overflow-y-auto pr-1">
                    {selectedEdges.map((edge, idx) => {
                      const isSource = edge.source === selectedNode.id;
                      const otherNodeId = isSource ? edge.target : edge.source;
                      const otherNode = nodeMap.get(otherNodeId);
                      if (!otherNode) return null;

                      return (
                        <div
                          key={idx}
                          onClick={() => setSelectedNode(otherNode)}
                          className="p-3 bg-white hover:bg-slate-50 rounded-xl border border-slate-200 hover:border-indigo-300 transition-all cursor-pointer group space-y-1.5 shadow-2xs"
                        >
                          <div className="flex items-center justify-between">
                            <span className="text-[10px] font-mono font-bold text-indigo-600 bg-indigo-50 px-2 py-0.5 rounded border border-indigo-100">
                              {isSource ? `→ ${edge.relation}` : `← ${edge.relation}`}
                            </span>
                            <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-indigo-600 transition-colors" />
                          </div>
                          <h4 className="font-bold text-xs text-slate-900 group-hover:text-indigo-900 transition-colors">
                            {otherNode.label}
                          </h4>
                          <p className="text-[11px] text-slate-500 leading-snug">
                            {edge.rationale}
                          </p>
                        </div>
                      );
                    })}
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="pt-2 space-y-2">
                  <a
                    href={selectedNode.official_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="w-full flex items-center justify-center space-x-2 py-2.5 px-4 bg-slate-900 hover:bg-black text-white text-xs font-bold rounded-xl transition-all shadow-xs"
                  >
                    <span>View Gazette / Authority Portal</span>
                    <ExternalLink className="w-3.5 h-3.5" />
                  </a>

                  {onAskCopilot && (
                    <button
                      onClick={() => onAskCopilot(`Explain the statutory relationship between ${selectedNode.label} and patentability / ABS compliance under Indian law.`)}
                      className="w-full flex items-center justify-center space-x-2 py-2 px-4 bg-emerald-50 hover:bg-emerald-100 text-emerald-800 text-xs font-bold rounded-xl border border-emerald-200 transition-all"
                    >
                      <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                      <span>Ask Copilot about this Node</span>
                    </button>
                  )}
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {loading && (
          <div className="absolute inset-0 z-20 bg-white/75 backdrop-blur-xs flex items-center justify-center space-x-2 text-xs font-bold text-slate-700">
            <div className="w-5 h-5 border-2 border-indigo-600 border-t-transparent rounded-full animate-spin" />
            <span>Synthesizing Statutory Graph Topology...</span>
          </div>
        )}
      </div>
    </div>
  );
}
