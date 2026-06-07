# gui/graph.py
import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl
from core.ideas import list_ideas

class GraphWindow(QWidget):
    def __init__(self, dark_mode=False, on_back=None, on_theme_change=None, on_idea_open=None):
        super().__init__()
        self.dark_mode = dark_mode
        self.on_back = on_back
        self.on_theme_change = on_theme_change
        self.on_idea_open = on_idea_open

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # Header
        header = QHBoxLayout()
        back_btn = QPushButton("← Zurück")
        back_btn.setObjectName("back_btn")
        back_btn.clicked.connect(on_back if on_back else self.close)
        self.theme_btn = QPushButton("☀" if dark_mode else "☾")
        self.theme_btn.setObjectName("theme_btn")
        self.theme_btn.clicked.connect(self.toggle_theme)
        header.addWidget(back_btn)
        header.addStretch()
        header.addWidget(self.theme_btn)
        layout.addLayout(header)

        # Graph
        self.web = QWebEngineView()
        self.web.loadFinished.connect(lambda: None)
        self.web.page().titleChanged.connect(self.on_title_changed)
        layout.addWidget(self.web)

        self.load_graph()
        self.apply_theme()

    def load_graph(self):
        ideas = list_ideas()
        nodes = [{"id": i["id"], "title": i["title"], "status": i.get("context", {}).get("status", "raw")} for i in ideas]
        edges = []
        for idea in ideas:
            for link_type, ids in idea.get("links", {}).items():
                for to_id in ids:
                    edges.append({"source": idea["id"], "target": to_id, "type": link_type})

        bg = "#18181b" if self.dark_mode else "#f5f4f0"
        text_color = "#f0f0f0" if self.dark_mode else "#1a1a1a"
        link_color = "#666" if self.dark_mode else "#aaa"

        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
            <style>
                * {{ margin: 0; padding: 0; }}
                body {{ background: {bg}; overflow: hidden; }}
                .node circle {{ cursor: pointer; stroke: {bg}; stroke-width: 2px; }}
                .node text {{ font-size: 12px; fill: {text_color}; font-family: -apple-system, sans-serif; }}
                .link {{ stroke: {link_color}; stroke-opacity: 0.5; stroke-width: 1.5px; }}
            </style>
        </head>
        <body>
            <svg id="graph" width="100vw" height="100vh"></svg>
            <script>
                const nodes = {json.dumps(nodes)};
                const edges = {json.dumps(edges)};

                const statusColors = {{
                    raw: "#888780",
                    refined: "#378ADD",
                    applied: "#1D9E75",
                    archived: "#D85A30"
                }};

                const svg = d3.select("#graph");
                const width = window.innerWidth;
                const height = window.innerHeight;
                svg.attr("width", width).attr("height", height);

                const g = svg.append("g");

                const zoom = d3.zoom()
                    .scaleExtent([0.1, 4])
                    .on("zoom", (event) => {{
                        g.attr("transform", event.transform);
                    }});
                svg.call(zoom);

                // Zuerst linkCount und radiusScale berechnen
                const linkCount = {{}};
                nodes.forEach(d => linkCount[d.id] = 0);
                edges.forEach(e => {{
                    const s = e.source.id || e.source;
                    const t = e.target.id || e.target;
                    linkCount[s] = (linkCount[s] || 0) + 1;
                    linkCount[t] = (linkCount[t] || 0) + 1;
                }});

                const radiusScale = d3.scaleLinear()
                    .domain([0, d3.max(Object.values(linkCount)) || 1])
                    .range([8, 18]);

                const simulation = d3.forceSimulation(nodes)
                    .force("link", d3.forceLink(edges).id(d => d.id).distance(120))
                    .force("charge", d3.forceManyBody().strength(-200))
                    .force("center", d3.forceCenter(width / 2, height / 2))
                    .force("x", d3.forceX(width / 2).strength(0.05))
                    .force("y", d3.forceY(height / 2).strength(0.05))
                    .force("collision", d3.forceCollide().radius(d => radiusScale(linkCount[d.id] || 0) + 15));

                const link = g.append("g")
                    .selectAll("line")
                    .data(edges)
                    .join("line")
                    .attr("class", "link");

                const node = g.append("g")
                    .selectAll("g")
                    .data(nodes)
                    .join("g")
                    .attr("class", "node")
                    .call(d3.drag()
                        .on("start", (e, d) => {{ if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; }})
                        .on("drag", (e, d) => {{ d.fx = e.x; d.fy = e.y; }})
                        .on("end", (e, d) => {{ if (!e.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; }}));

                node.append("circle")
                    .attr("r", d => radiusScale(linkCount[d.id] || 0))
                    .attr("fill", d => statusColors[d.status] || "#888")
                    .attr("stroke", "{bg}")
                    .attr("stroke-width", 2)
                    .on("click", (event, d) => {{
                        document.title = `idea-${{d.id}}`;
                    }});

                node.append("text")
                    .attr("x", 20)
                    .attr("y", 0)
                    .attr("dominant-baseline", "middle")
                    .text(d => d.title.length > 20 ? d.title.slice(0, 20) + "…" : d.title);

                simulation.on("tick", () => {{
                    link
                        .attr("x1", d => d.source.x).attr("y1", d => d.source.y)
                        .attr("x2", d => d.target.x).attr("y2", d => d.target.y);
                    node.attr("transform", d => `translate(${{d.x}},${{d.y}})`);
                }});
            </script>
        </body>
        </html>
        """
        self.web.setHtml(html)

    def apply_theme(self):
        from gui.styles import DARK, LIGHT
        self.setStyleSheet(DARK if self.dark_mode else LIGHT)
        self.theme_btn.setText("☀" if self.dark_mode else "☾")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        self.theme_btn.setText("☀" if self.dark_mode else "☾")
        if self.on_theme_change:
            self.on_theme_change(self.dark_mode)
        self.apply_theme()
        self.load_graph()

    def on_url_changed(self, url):
        if url.scheme() == "idea":
            idea_id = int(url.host())
            if self.on_idea_open:
                self.on_idea_open(idea_id)

    def on_title_changed(self, title):
        if title.startswith("idea-"):
            idea_id = int(title.replace("idea-", ""))
            if self.on_idea_open:
                self.on_idea_open(idea_id)