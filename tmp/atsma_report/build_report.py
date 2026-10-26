from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(r"D:\Projects\ATSMA")
TMP = ROOT / "tmp" / "atsma_report"
OUTPUT = ROOT / "output" / "pdf" / "ATSMA_Social_Network_Analysis_Report.pdf"
RESULTS = ROOT / "results" / "figures"


styles = getSampleStyleSheet()
styles.add(ParagraphStyle(
    name="CoverField",
    parent=styles["Normal"],
    fontName="Helvetica",
    fontSize=17,
    leading=24,
    alignment=TA_CENTER,
    spaceAfter=2,
))
styles.add(ParagraphStyle(
    name="CoverProject",
    parent=styles["Normal"],
    fontName="Helvetica-Bold",
    fontSize=18,
    leading=24,
    alignment=TA_CENTER,
    spaceBefore=9,
    spaceAfter=3,
))
styles.add(ParagraphStyle(
    name="ReportHeading",
    parent=styles["Heading2"],
    fontName="Helvetica-Bold",
    fontSize=14,
    leading=18,
    spaceBefore=10,
    spaceAfter=6,
    keepWithNext=True,
    textColor=colors.black,
))
styles.add(ParagraphStyle(
    name="SubHeading",
    parent=styles["Heading3"],
    fontName="Helvetica-Bold",
    fontSize=11.5,
    leading=15,
    spaceBefore=8,
    spaceAfter=4,
    keepWithNext=True,
    textColor=colors.black,
))
styles.add(ParagraphStyle(
    name="BodyReport",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10.5,
    leading=15,
    alignment=TA_JUSTIFY,
    spaceAfter=7,
))
styles.add(ParagraphStyle(
    name="BulletReport",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=10.5,
    leading=14,
    leftIndent=18,
    firstLineIndent=-10,
    spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="CodeLabel",
    parent=styles["BodyText"],
    fontName="Helvetica-Bold",
    fontSize=10.5,
    leading=14,
    spaceBefore=5,
    spaceAfter=4,
))
styles.add(ParagraphStyle(
    name="Caption",
    parent=styles["BodyText"],
    fontName="Helvetica",
    fontSize=9,
    leading=12,
    alignment=TA_CENTER,
    spaceBefore=3,
    spaceAfter=9,
))
code_style = ParagraphStyle(
    "Code",
    fontName="Courier",
    fontSize=8.2,
    leading=10.5,
    leftIndent=10,
    rightIndent=8,
    borderColor=colors.HexColor("#D9D9D9"),
    borderWidth=0.5,
    borderPadding=7,
    backColor=colors.HexColor("#F7F7F7"),
)


def p(text, style="BodyReport"):
    return Paragraph(text, styles[style])


def bullet(text):
    return Paragraph(f"&bull; {text}", styles["BulletReport"])


def code(text):
    return Preformatted(text.strip("\n"), code_style)


def figure(filename, caption, width=5.9 * inch, height=None):
    path = RESULTS / filename
    image = Image(str(path))
    aspect = image.imageHeight / image.imageWidth
    image.drawWidth = width
    image.drawHeight = height if height else width * aspect
    return KeepTogether([image, p(caption, "Caption")])


def grid_table(data, widths, header=True):
    table = Table(data, colWidths=widths, repeatRows=1 if header else 0, hAlign="LEFT")
    commands = [
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D9D9D9")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("FONT", (0, 0), (-1, -1), "Helvetica", 9),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#404040")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("ALIGN", (1, 1), (-1, -1), "CENTER"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F4F7FA")]),
        ]
    table.setStyle(TableStyle(commands))
    return table


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=letter,
        leftMargin=1 * inch,
        rightMargin=1 * inch,
        topMargin=1 * inch,
        bottomMargin=1 * inch,
        title="Social Network Analysis Metrics Project Report",
        author="Vikhyat Shajee Nambiar",
    )
    story = []

    banner = Image(str(TMP / "template_banner.png"), width=6.5 * inch, height=2.313194 * inch)
    story.extend([
        banner,
        Spacer(1, 0.28 * inch),
        p("<b>NAME:</b> Vikhyat Shajee Nambiar", "CoverField"),
        p("<b>REG NO:</b> 23BCB7137", "CoverField"),
        p("<b>COURSE CODE:</b> CSE4039", "CoverField"),
        p("<b>COURSE:</b> Advanced Text and Social Media Analytics", "CoverField"),
        p("<b>SLOT:</b> L39-L40", "CoverField"),
        p("<b>FACULTY NAME:</b> Gundimeda Venugopal", "CoverField"),
        p("LAB TOPIC 5", "CoverProject"),
        p("SOCIAL NETWORK ANALYSIS METRICS", "CoverProject"),
        Spacer(1, 0.1 * inch),
        p("Group project report", "Caption"),
        PageBreak(),
    ])

    story += [
        p("Question:", "ReportHeading"),
        p(
            "Analyse the Zachary Karate Club social network using degree, closeness, "
            "betweenness, eigenvector centrality, and PageRank. Compare the meaning of "
            "these rankings, validate selected algorithms from first principles, identify "
            "communities, and evaluate how targeted removal of influential nodes affects "
            "network connectivity.",
        ),
        p("Dataset and project organisation:", "ReportHeading"),
        p(
            "The primary dataset is NetworkX's built-in Zachary Karate Club graph. It has "
            "34 members and 78 observed social ties. The repository divides the work into "
            "three notebooks: network exploration, centrality analysis and validation, and "
            "communities with robustness analysis. Reusable loading, visualisation, and "
            "centrality routines are stored in the src package, while automated tests verify "
            "the manual implementations against NetworkX.",
        ),
        p("Part 1 - Network exploration:", "SubHeading"),
        bullet("Load the Karate Club graph and preserve a fixed spring layout for comparable network plots."),
        bullet("Calculate graph size, density, average degree, connected components, diameter, average path length, clustering, and transitivity."),
        bullet("Use a degree distribution to show that a small number of members have many more social ties than the rest."),
        p("Part 2 - Centrality analysis and validation:", "SubHeading"),
        bullet("Compute degree, closeness, betweenness, eigenvector centrality, and PageRank."),
        bullet("Implement BFS-based closeness, Brandes betweenness, eigenvector power iteration, and PageRank for transparent algorithm validation."),
        bullet("Compare rankings using a Spearman rank-correlation matrix rather than assuming all measures identify the same actors."),
        p("Part 3 - Communities and robustness:", "SubHeading"),
        bullet("Detect communities with greedy modularity maximisation and compare them with the historical club split."),
        bullet("Remove high-degree and high-betweenness nodes one at a time and compare the largest connected component with a 100-run random baseline."),
        bullet("Use a directed follower-network example to distinguish popularity through in-degree from activity through out-degree and PageRank."),
        PageBreak(),
        p("Code:", "ReportHeading"),
        p("The following excerpts show the reusable structure used throughout the project.", "BodyReport"),
        p("1. Dataset loader and network summary", "CodeLabel"),
        code('''def load_graph(source="karate", directed=False):
    if source in BUILTIN_GRAPHS:
        return BUILTIN_GRAPHS[source]()
    graph_type = nx.DiGraph if directed else nx.Graph
    return nx.parse_edgelist(source, create_using=graph_type)

def network_summary(graph):
    undirected = graph.to_undirected()
    giant = undirected.subgraph(max(nx.connected_components(undirected), key=len))
    return {"Nodes": graph.number_of_nodes(),
            "Edges": graph.number_of_edges(),
            "Density": nx.density(graph),
            "Diameter": nx.diameter(giant),
            "Average clustering": nx.average_clustering(undirected)}'''),
        p("2. Centrality calculation", "CodeLabel"),
        code('''def compute_centralities(graph, alpha=0.85):
    return {
        "degree": nx.degree_centrality(graph),
        "closeness": nx.closeness_centrality(graph),
        "betweenness": nx.betweenness_centrality(graph, normalized=True, weight=None),
        "eigenvector": nx.eigenvector_centrality(graph, max_iter=1000, weight=None),
        "pagerank": nx.pagerank(graph, alpha=alpha, weight=None),
    }'''),
        p("3. Robustness experiment", "CodeLabel"),
        code('''def lcc_fraction_after_removals(graph, removal_order):
    working_graph = graph.copy()
    fractions = [1.0]
    for node in removal_order:
        working_graph.remove_node(node)
        lcc_size = max((len(c) for c in nx.connected_components(working_graph)), default=0)
        fractions.append(lcc_size / graph.number_of_nodes())
    return fractions'''),
        p("Working of the code:", "ReportHeading"),
        bullet("The graph is loaded as an undirected social network. A reproducible layout seed ensures that changes in colour or node size represent scores rather than a different drawing."),
        bullet("Each centrality measure produces one score per node. Higher values correspond to a different structural role: direct popularity, short-path reach, brokerage, prestige, or random-walk visibility."),
        bullet("The from-scratch algorithms are compared with NetworkX results. Degree, closeness, and betweenness match exactly to displayed precision; eigenvector centrality differs only by numerical convergence tolerance."),
        bullet("For the robustness study, the largest connected component is recorded after every removal. A rapid decline means the selected nodes were important for holding the network together."),
        PageBreak(),
        p("Output:", "ReportHeading"),
        p("Centrality ranking summary", "SubHeading"),
        p("The measures agree that nodes 0 and 33 are unusually influential, but they do not assign them the same role. Node 33 leads direct-connection, prestige, and PageRank rankings, while node 0 is the strongest bridge and fastest broadcaster.", "BodyReport"),
        grid_table([
            ["Metric", "Highest node", "Score", "Interpretation"],
            ["Degree", "33", "0.515", "Most direct ties"],
            ["Closeness", "0", "0.569", "Fastest reach to others"],
            ["Betweenness", "0", "0.438", "Key broker / bridge"],
            ["Eigenvector", "33", "0.373", "Connected to influential members"],
            ["PageRank", "33", "0.101", "Highest random-walk visibility"],
        ], [1.05 * inch, 0.85 * inch, 0.65 * inch, 3.95 * inch]),
        Spacer(1, 0.12 * inch),
        p("Community detection", "SubHeading"),
        p("Greedy modularity maximisation detects three communities with modularity 0.411. Comparing the detected labels with the observed Karate Club factions gives 94.1% community-to-history purity. The third group is a useful refinement of the historical two-faction split rather than evidence of a contradiction.", "BodyReport"),
        figure("community_vs_history.png", "Figure 1. Observed historical factions and communities detected from graph structure.", width=6.1 * inch),
        PageBreak(),
        p("Output continued:", "ReportHeading"),
        p("Network robustness", "SubHeading"),
        p("Targeted removal exposes a clear vulnerability. The largest connected component falls below half of its original size after four removals when nodes are chosen by degree or betweenness. The mean random-removal baseline does not fall below half until fourteen removals.", "BodyReport"),
        figure("robustness_targeted_vs_random.png", "Figure 2. Targeted central-node removal fragments the network much faster than random removal.", width=6.0 * inch),
        KeepTogether([
            p("Directed-network extension", "SubHeading"),
            p("The Karate Club graph is undirected, so a small follower-network example demonstrates direction-specific analysis. In-degree represents attention received, out-degree represents following activity, and PageRank weights incoming attention by the importance of the sender.", "BodyReport"),
            figure("directed_network_pagerank.png", "Figure 3. Directed follower-network example; node size represents PageRank.", width=5.0 * inch),
        ]),
        PageBreak(),
        p("Conclusion:", "ReportHeading"),
        p(
            "This project shows that centrality is not one universal ranking. Node 33 is the "
            "most connected and highly prestigious member, whereas node 0 is the strongest "
            "bridge between parts of the network and the most efficient broadcaster. The "
            "manual implementations support the correctness of the centrality computations, "
            "and the rank comparison demonstrates that the metrics are related but not "
            "interchangeable.",
        ),
        p(
            "Community detection closely reflects the historical Karate Club division, and "
            "the robustness experiment shows why structural importance matters: removing a "
            "small number of central members fragments the network far more quickly than "
            "random failure. The directed extension further shows that popularity and "
            "activity must be interpreted separately when relationships have direction.",
        ),
        p("Limitations and future work:", "ReportHeading"),
        bullet("The Karate Club graph is small and undirected; results should be compared with a larger real social-media interaction network."),
        bullet("Exact betweenness becomes expensive on large graphs, so sampling should be considered for networks with many thousands of nodes."),
        bullet("Future analysis can combine centrality with temporal data, sentiment, or topic information to relate structural roles to communication content."),
        p("References:", "ReportHeading"),
        p("Zachary, W. W. (1977). An information flow model for conflict and fission in small groups. Journal of Anthropological Research, 33(4), 452-473.", "BodyReport"),
        p("Brandes, U. (2001). A faster algorithm for betweenness centrality. Journal of Mathematical Sociology, 25(2), 163-177.", "BodyReport"),
        p("NetworkX Developers. NetworkX documentation. https://networkx.org/documentation/stable/", "BodyReport"),
    ]
    document.build(story)


if __name__ == "__main__":
    build()
