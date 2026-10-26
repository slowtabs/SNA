from copy import deepcopy
from pathlib import Path
from shutil import copy2

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor


ROOT = Path(r"D:\Projects\ATSMA")
TMP = ROOT / "tmp" / "atsma_report"
TEMPLATE = Path(r"C:\College\ATSMA\Lab123BCB7137.docx")
OUTPUT = ROOT / "output" / "docx" / "ATSMA_Social_Network_Analysis_Report.docx"
RESULTS = ROOT / "results" / "figures"


def shade(cell, fill):
    properties = cell._tc.get_or_add_tcPr()
    shading = OxmlElement("w:shd")
    shading.set(qn("w:fill"), fill)
    properties.append(shading)


def set_cell_text(cell, text, bold=False, color=None):
    cell.text = ""
    paragraph = cell.paragraphs[0]
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.size = Pt(9)
    if color:
        run.font.color.rgb = RGBColor(*color)


def add_paragraph(doc, text="", bold=False, size=10.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, before=0, after=6):
    paragraph = doc.add_paragraph()
    paragraph.alignment = align
    paragraph.paragraph_format.space_before = Pt(before)
    paragraph.paragraph_format.space_after = Pt(after)
    paragraph.paragraph_format.line_spacing = 1.12
    run = paragraph.add_run(text)
    run.bold = bold
    run.font.size = Pt(size)
    return paragraph


def add_heading(doc, text, level=1):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    paragraph.paragraph_format.space_before = Pt(10 if level == 1 else 7)
    paragraph.paragraph_format.space_after = Pt(5)
    run = paragraph.add_run(text)
    run.bold = True
    run.font.size = Pt(14 if level == 1 else 11.5)
    return paragraph


def add_bullet(doc, text):
    paragraph = doc.add_paragraph(style="List Paragraph")
    paragraph.paragraph_format.left_indent = Inches(0.25)
    paragraph.paragraph_format.first_line_indent = Inches(-0.14)
    paragraph.paragraph_format.space_after = Pt(3)
    run = paragraph.add_run("• " + text)
    run.font.size = Pt(10.5)
    return paragraph


def add_code(doc, text):
    paragraph = doc.add_paragraph()
    paragraph.paragraph_format.left_indent = Inches(0.18)
    paragraph.paragraph_format.right_indent = Inches(0.12)
    paragraph.paragraph_format.space_after = Pt(8)
    paragraph.paragraph_format.line_spacing = 1.0
    run = paragraph.add_run(text.strip())
    run.font.name = "Consolas"
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "Consolas")
    run.font.size = Pt(8.5)
    return paragraph


def add_figure(doc, filename, caption, width):
    paragraph = doc.add_paragraph()
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER
    paragraph.add_run().add_picture(str(RESULTS / filename), width=Inches(width))
    caption_p = doc.add_paragraph()
    caption_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    caption_p.paragraph_format.space_after = Pt(8)
    caption_run = caption_p.add_run(caption)
    caption_run.font.size = Pt(9)


def clear_body(document):
    body = document._element.body
    for child in list(body):
        if child.tag != qn("w:sectPr"):
            body.remove(child)


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    copy2(TEMPLATE, OUTPUT)
    doc = Document(OUTPUT)
    clear_body(doc)

    # Preserve the reference's Letter portrait section and use its banner asset.
    banner_p = doc.add_paragraph()
    banner_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    banner_p.add_run().add_picture(str(TMP / "template_banner.png"), width=Inches(6.5))
    doc.add_paragraph().paragraph_format.space_after = Pt(4)
    cover = [
        ("NAME:", " Vikhyat Shajee Nambiar"),
        ("REG NO:", " 23BCB7137"),
        ("COURSE CODE:", " CSE4039"),
        ("COURSE:", " Advanced Text and Social Media Analytics"),
        ("SLOT:", " L39-L40"),
        ("FACULTY NAME:", " Gundimeda Venugopal"),
    ]
    for label, value in cover:
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_after = Pt(0)
        para.paragraph_format.line_spacing = 1.0
        left = para.add_run(label)
        left.bold = True
        left.font.size = Pt(17)
        right = para.add_run(value)
        right.font.size = Pt(17)
    for title in ["LAB TOPIC 5", "SOCIAL NETWORK ANALYSIS METRICS"]:
        para = doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        para.paragraph_format.space_before = Pt(8)
        para.paragraph_format.space_after = Pt(0)
        run = para.add_run(title)
        run.bold = True
        run.font.size = Pt(18)
    para = doc.add_paragraph()
    para.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = para.add_run("Group project report")
    run.font.size = Pt(10)
    doc.add_page_break()

    add_heading(doc, "Question:")
    add_paragraph(doc, "Analyse the Zachary Karate Club social network using degree, closeness, betweenness, eigenvector centrality, and PageRank. Compare the meaning of these rankings, validate selected algorithms from first principles, identify communities, and evaluate how targeted removal of influential nodes affects network connectivity.")
    add_heading(doc, "Dataset and project organisation:")
    add_paragraph(doc, "The primary dataset is NetworkX's built-in Zachary Karate Club graph. It has 34 members and 78 observed social ties. The repository divides the work into three notebooks: network exploration, centrality analysis and validation, and communities with robustness analysis. Reusable loading, visualisation, and centrality routines are stored in the src package, while automated tests verify the manual implementations against NetworkX.")
    add_heading(doc, "Part 1 - Network exploration:", 2)
    add_bullet(doc, "Load the Karate Club graph and preserve a fixed spring layout for comparable network plots.")
    add_bullet(doc, "Calculate graph size, density, average degree, connected components, diameter, average path length, clustering, and transitivity.")
    add_bullet(doc, "Use a degree distribution to show that a small number of members have many more social ties than the rest.")
    add_heading(doc, "Part 2 - Centrality analysis and validation:", 2)
    add_bullet(doc, "Compute degree, closeness, betweenness, eigenvector centrality, and PageRank.")
    add_bullet(doc, "Implement BFS-based closeness, Brandes betweenness, eigenvector power iteration, and PageRank for transparent algorithm validation.")
    add_bullet(doc, "Compare rankings with a Spearman rank-correlation matrix.")
    add_heading(doc, "Part 3 - Communities and robustness:", 2)
    add_bullet(doc, "Detect communities with greedy modularity maximisation and compare them with the historical club split.")
    add_bullet(doc, "Remove high-degree and high-betweenness nodes one at a time and compare the largest connected component with a 100-run random baseline.")
    add_bullet(doc, "Use a directed follower-network example to distinguish popularity through in-degree from activity through out-degree and PageRank.")

    doc.add_page_break()
    add_heading(doc, "Code:")
    add_paragraph(doc, "The following excerpts show the reusable structure used throughout the project.")
    add_heading(doc, "1. Dataset loader and network summary", 2)
    add_code(doc, '''def load_graph(source="karate", directed=False):
    if source in BUILTIN_GRAPHS:
        return BUILTIN_GRAPHS[source]()
    graph_type = nx.DiGraph if directed else nx.Graph
    return nx.parse_edgelist(source, create_using=graph_type)

def network_summary(graph):
    undirected = graph.to_undirected()
    giant = undirected.subgraph(max(nx.connected_components(undirected), key=len))
    return {"Nodes": graph.number_of_nodes(), "Edges": graph.number_of_edges(),
            "Density": nx.density(graph), "Diameter": nx.diameter(giant)}''')
    add_heading(doc, "2. Centrality calculation", 2)
    add_code(doc, '''def compute_centralities(graph, alpha=0.85):
    return {
        "degree": nx.degree_centrality(graph),
        "closeness": nx.closeness_centrality(graph),
        "betweenness": nx.betweenness_centrality(graph, normalized=True, weight=None),
        "eigenvector": nx.eigenvector_centrality(graph, max_iter=1000, weight=None),
        "pagerank": nx.pagerank(graph, alpha=alpha, weight=None),
    }''')
    add_heading(doc, "3. Robustness experiment", 2)
    add_code(doc, '''def lcc_fraction_after_removals(graph, removal_order):
    working_graph = graph.copy()
    fractions = [1.0]
    for node in removal_order:
        working_graph.remove_node(node)
        lcc_size = max((len(c) for c in nx.connected_components(working_graph)), default=0)
        fractions.append(lcc_size / graph.number_of_nodes())
    return fractions''')
    add_heading(doc, "Working of the code:")
    add_bullet(doc, "The graph is loaded as an undirected social network. A reproducible layout seed ensures comparable graph plots.")
    add_bullet(doc, "Each centrality measure scores a different structural role: direct popularity, reach, brokerage, prestige, or random-walk visibility.")
    add_bullet(doc, "Manual algorithms are compared with NetworkX results; degree, closeness, and betweenness match to displayed precision, while eigenvector centrality differs only by numerical tolerance.")
    add_bullet(doc, "The robustness study records the largest connected component after every removal.")

    doc.add_page_break()
    add_heading(doc, "Output:")
    add_heading(doc, "Centrality ranking summary", 2)
    add_paragraph(doc, "The measures agree that nodes 0 and 33 are unusually influential, but they do not assign them the same role. Node 33 leads direct-connection, prestige, and PageRank rankings, while node 0 is the strongest bridge and fastest broadcaster.")
    rows = [
        ["Metric", "Highest node", "Score", "Interpretation"],
        ["Degree", "33", "0.515", "Most direct ties"],
        ["Closeness", "0", "0.569", "Fastest reach to others"],
        ["Betweenness", "0", "0.438", "Key broker / bridge"],
        ["Eigenvector", "33", "0.373", "Connected to influential members"],
        ["PageRank", "33", "0.101", "Highest random-walk visibility"],
    ]
    table = doc.add_table(rows=len(rows), cols=4)
    widths = [1.15, 1.0, 0.75, 3.5]
    for row_i, row in enumerate(rows):
        for col_i, value in enumerate(row):
            cell = table.cell(row_i, col_i)
            set_cell_text(cell, value, bold=row_i == 0, color=(255, 255, 255) if row_i == 0 else None)
            if row_i == 0:
                shade(cell, "404040")
            elif row_i % 2 == 0:
                shade(cell, "F4F7FA")
            cell.width = Inches(widths[col_i])
    doc.add_paragraph().paragraph_format.space_after = Pt(3)
    add_heading(doc, "Community detection", 2)
    add_paragraph(doc, "Greedy modularity maximisation detects three communities with modularity 0.411. Comparing the detected labels with the observed Karate Club factions gives 94.1% community-to-history purity. The third group is a useful refinement of the historical two-faction split rather than evidence of a contradiction.")
    add_figure(doc, "community_vs_history.png", "Figure 1. Observed historical factions and communities detected from graph structure.", 6.0)

    doc.add_page_break()
    add_heading(doc, "Output continued:")
    add_heading(doc, "Network robustness", 2)
    add_paragraph(doc, "Targeted removal exposes a clear vulnerability. The largest connected component falls below half of its original size after four removals when nodes are chosen by degree or betweenness. The mean random-removal baseline does not fall below half until fourteen removals.")
    add_figure(doc, "robustness_targeted_vs_random.png", "Figure 2. Targeted central-node removal fragments the network much faster than random removal.", 6.0)
    add_heading(doc, "Directed-network extension", 2)
    add_paragraph(doc, "The Karate Club graph is undirected, so a small follower-network example demonstrates direction-specific analysis. In-degree represents attention received, out-degree represents following activity, and PageRank weights incoming attention by the importance of the sender.")
    add_figure(doc, "directed_network_pagerank.png", "Figure 3. Directed follower-network example; node size represents PageRank.", 5.0)

    doc.add_page_break()
    add_heading(doc, "Conclusion:")
    add_paragraph(doc, "This project shows that centrality is not one universal ranking. Node 33 is the most connected and highly prestigious member, whereas node 0 is the strongest bridge between parts of the network and the most efficient broadcaster. The manual implementations support the correctness of the centrality computations, and the rank comparison demonstrates that the metrics are related but not interchangeable.")
    add_paragraph(doc, "Community detection closely reflects the historical Karate Club division, and the robustness experiment shows why structural importance matters: removing a small number of central members fragments the network far more quickly than random failure. The directed extension further shows that popularity and activity must be interpreted separately when relationships have direction.")
    add_heading(doc, "Limitations and future work:")
    add_bullet(doc, "The Karate Club graph is small and undirected; results should be compared with a larger real social-media interaction network.")
    add_bullet(doc, "Exact betweenness becomes expensive on large graphs, so sampling should be considered for networks with many thousands of nodes.")
    add_bullet(doc, "Future analysis can combine centrality with temporal data, sentiment, or topic information to relate structural roles to communication content.")
    add_heading(doc, "References:")
    add_paragraph(doc, "Zachary, W. W. (1977). An information flow model for conflict and fission in small groups. Journal of Anthropological Research, 33(4), 452-473.")
    add_paragraph(doc, "Brandes, U. (2001). A faster algorithm for betweenness centrality. Journal of Mathematical Sociology, 25(2), 163-177.")
    add_paragraph(doc, "NetworkX Developers. NetworkX documentation. https://networkx.org/documentation/stable/")
    doc.save(OUTPUT)


if __name__ == "__main__":
    build()
