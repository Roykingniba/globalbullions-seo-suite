"""Ported from seo_tool/mapper/graph_builder.py — unchanged logic (including
the dark-themed pyvis visual styling)."""

import json
import logging
import os
from typing import Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
import pandas as pd

from core.pipeline_config import PipelineConfig

logger = logging.getLogger(__name__)


class GraphBuilder:
    def __init__(self, config: PipelineConfig):
        self.config = config

    # ------------------------------------------------------------------
    def build(self, pages_df: pd.DataFrame, opps_df: pd.DataFrame) -> nx.DiGraph:
        G = nx.DiGraph()
        page_urls = set(pages_df["url"])

        for _, row in pages_df.iterrows():
            G.add_node(
                row["url"],
                title=str(row.get("title") or row["url"])[:60],
                content_score=float(row.get("content_score") or 0),
                depth=int(row.get("depth") or 0),
                word_count=int(row.get("word_count") or 0),
            )

        for _, row in pages_df.iterrows():
            try:
                links = json.loads(row.get("internal_links") or "[]")
            except (json.JSONDecodeError, TypeError):
                links = []
            for tgt in links:
                if tgt in page_urls and tgt != row["url"]:
                    G.add_edge(row["url"], tgt, edge_type="existing", weight=1.0)

        if not opps_df.empty:
            for _, row in opps_df.iterrows():
                src, tgt = row["source_url"], row["target_url"]
                if src in page_urls and tgt in page_urls and not G.has_edge(src, tgt):
                    G.add_edge(src, tgt,
                        edge_type="proposed",
                        weight=float(row["semantic_relevance_score"]),
                        anchor=str(row.get("recommended_anchor_text") or ""),
                    )

        logger.info("Graph: %d nodes, %d edges", G.number_of_nodes(), G.number_of_edges())
        return G

    # ------------------------------------------------------------------
    def visualize(self, G: nx.DiGraph, output_path: Optional[str] = None) -> str:
        try:
            from pyvis.network import Network
        except ImportError:
            logger.error("pyvis not installed: pip install pyvis")
            return ""

        if output_path is None:
            output_path = os.path.join(self.config.output_dir, self.config.graph_output)

        net = Network(
            height="100%",
            width="100%",
            directed=True,
            bgcolor="#05050f",
            font_color="#94a3b8",
            notebook=False,
        )

        for node, attrs in G.nodes(data=True):
            score = attrs.get("content_score", 50)
            # Gradient: low=red -> mid=purple -> high=cyan
            if score >= 70:
                node_color = f"rgba(0,212,255,{0.4 + score/200:.2f})"
                border_col = "#00d4ff"
            elif score >= 40:
                node_color = f"rgba(124,58,237,{0.4 + score/200:.2f})"
                border_col = "#7c3aed"
            else:
                node_color = f"rgba(255,71,87,{0.5 + score/200:.2f})"
                border_col = "#ff4757"

            label = (attrs.get("title") or node)[:25]
            tooltip = (
                f"<b style='color:#00d4ff'>{attrs.get('title','')[:50]}</b><br>"
                f"<span style='color:#64748b'>URL:</span> {node[:60]}<br>"
                f"<span style='color:#64748b'>Score:</span> <b style='color:#00d4ff'>{score:.1f}/100</b><br>"
                f"<span style='color:#64748b'>Words:</span> {attrs.get('word_count', 0):,}<br>"
                f"<span style='color:#64748b'>Depth:</span> {attrs.get('depth', 0)}"
            )

            net.add_node(
                node,
                label=label,
                title=tooltip,
                color={"background": node_color, "border": border_col,
                       "highlight": {"background": "#00d4ff22", "border": "#00d4ff"}},
                size=max(10, min(40, 10 + score / 4)),
                font={"color": "#e2e8f0", "size": 11, "face": "Space Grotesk, sans-serif"},
                borderWidth=1,
                borderWidthSelected=3,
            )

        for src, tgt, attrs in G.edges(data=True):
            if attrs.get("edge_type") == "existing":
                net.add_edge(src, tgt,
                    color={"color": "#1e40af", "highlight": "#3b82f6", "opacity": 0.6},
                    width=1, dashes=False, arrows="to",
                    title="<span style='color:#3b82f6'>Existing internal link</span>",
                    smooth={"type": "curvedCW", "roundness": 0.1},
                )
            else:
                w = attrs.get("weight", 0.5)
                net.add_edge(src, tgt,
                    color={"color": f"rgba(0,255,136,{0.3 + w * 0.5:.2f})",
                           "highlight": "#00ff88"},
                    width=max(1, int(w * 5)),
                    dashes=True, arrows="to",
                    title=(f"<span style='color:#00ff88'>Proposed link</span><br>"
                           f"Score: <b>{w:.3f}</b><br>"
                           f"Anchor: <i>{attrs.get('anchor','')[:40]}</i>"),
                    smooth={"type": "curvedCCW", "roundness": 0.15},
                )

        net.set_options("""
        {
          "nodes": {
            "shape": "dot",
            "shadow": {"enabled": true, "color": "rgba(0,212,255,0.3)", "size": 8, "x": 0, "y": 0}
          },
          "edges": {
            "smooth": {"enabled": true},
            "shadow": false,
            "selectionWidth": 2
          },
          "physics": {
            "enabled": true,
            "solver": "barnesHut",
            "barnesHut": {
              "gravitationalConstant": -6000,
              "centralGravity": 0.3,
              "springLength": 180,
              "springConstant": 0.04,
              "damping": 0.09
            },
            "stabilization": {"iterations": 150}
          },
          "interaction": {
            "navigationButtons": true,
            "keyboard": {"enabled": true},
            "tooltipDelay": 60,
            "hover": true,
            "multiselect": true
          },
          "layout": {"improvedLayout": true}
        }
        """)

        net.save_graph(output_path)
        _inject_graph_styles(output_path)

        logger.info("Graph saved -> %s", output_path)
        return output_path

    # ------------------------------------------------------------------
    def metrics(self, G: nx.DiGraph) -> Dict:
        if G.number_of_nodes() == 0:
            return {}
        in_deg = dict(G.in_degree())
        out_deg = dict(G.out_degree())
        top_linked: List[Tuple[str, int]] = sorted(
            in_deg.items(), key=lambda x: x[1], reverse=True
        )[:10]
        orphans = [n for n, d in in_deg.items() if d == 0]
        return {
            "total_nodes": G.number_of_nodes(),
            "total_edges": G.number_of_edges(),
            "avg_in_degree": round(float(np.mean(list(in_deg.values()))), 2),
            "avg_out_degree": round(float(np.mean(list(out_deg.values()))), 2),
            "top_linked_pages": top_linked,
            "orphan_pages": orphans,
            "orphan_count": len(orphans),
        }


# ------------------------------------------------------------------------------
def _inject_graph_styles(html_path: str):
    """Post-process Pyvis HTML: inject dark theme CSS + legend overlay."""
    try:
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()

        style_inject = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;600&display=swap');
body, html { margin:0; padding:0; background:#05050f !important; font-family:'Space Grotesk',sans-serif; }
#mynetwork {
  background: radial-gradient(ellipse 80% 60% at 50% 0%, rgba(0,212,255,0.04) 0%, transparent 60%),
              radial-gradient(ellipse 60% 60% at 80% 100%, rgba(124,58,237,0.04) 0%, transparent 60%),
              #05050f;
  border: 1px solid rgba(0,212,255,0.1);
  border-radius: 12px;
}
#graph-legend {
  position: fixed; bottom: 24px; left: 24px;
  background: rgba(5,5,30,0.85);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 10px;
  padding: 14px 18px;
  font-size: 12px;
  color: #94a3b8;
  z-index: 9999;
}
.legend-dot { display:inline-block; width:10px; height:10px; border-radius:50%; margin-right:6px; }
.vis-tooltip {
  background: rgba(5,5,30,0.95) !important;
  border: 1px solid rgba(0,212,255,0.3) !important;
  color: #e2e8f0 !important;
  border-radius: 8px !important;
  font-family: 'Space Grotesk', sans-serif !important;
  font-size: 12px !important;
  padding: 10px 14px !important;
  box-shadow: 0 8px 32px rgba(0,0,0,0.6) !important;
}
.vis-button { filter: invert(0.8); }
</style>
<div id="graph-legend">
  <div style="font-size:10px;letter-spacing:2px;color:#4a5568;margin-bottom:10px;font-weight:600;">LEGEND</div>
  <div style="margin-bottom:6px;"><span class="legend-dot" style="background:#00d4ff;box-shadow:0 0 6px #00d4ff88;"></span>High score page (70+)</div>
  <div style="margin-bottom:6px;"><span class="legend-dot" style="background:#7c3aed;box-shadow:0 0 6px #7c3aed88;"></span>Medium score page (40-70)</div>
  <div style="margin-bottom:6px;"><span class="legend-dot" style="background:#ff4757;box-shadow:0 0 6px #ff475788;"></span>Low score page (&lt;40)</div>
  <div style="margin-bottom:6px;"><span style="display:inline-block;width:20px;height:2px;background:#1e40af;margin-right:6px;vertical-align:middle;"></span>Existing link</div>
  <div><span style="display:inline-block;width:20px;height:2px;background:#00ff88;border-top:2px dashed #00ff88;margin-right:6px;vertical-align:middle;"></span>Proposed link</div>
</div>
"""
        html = html.replace("</head>", style_inject + "</head>", 1)

        with open(html_path, "w", encoding="utf-8") as f:
            f.write(html)
    except Exception as e:
        logger.warning("Could not inject graph styles: %s", e)
