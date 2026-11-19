"""Render the manuscript's vector artwork from the accompanying plot data."""
import json
from pathlib import Path

import matplotlib as mpl

mpl.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import FancyArrowPatch, Rectangle
import numpy as np

HERE = Path(__file__).resolve().parent
FIGURES = HERE.parent / "figures"
DATA = json.loads((HERE / "plot_data.json").read_text())

INK = "#222222"
GREY = "#656565"
RULE = "#9a9a9a"
GRID = "#e3e3e3"
BLUE = "#235882"
RUST = "#a04428"
TEAL = "#2a6e67"
PURPLE = "#704983"
WIDTH = 6.35

mpl.rcParams.update({
    "font.family": "Liberation Serif",
    "mathtext.fontset": "stix",
    "font.size": 9.5,
    "axes.labelsize": 9.5,
    "axes.linewidth": 0.65,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "text.color": INK,
    "axes.labelcolor": INK,
    "axes.edgecolor": INK,
    "xtick.color": INK,
    "ytick.color": INK,
    "xtick.major.size": 3.0,
    "ytick.major.size": 3.0,
    "xtick.major.width": 0.65,
    "ytick.major.width": 0.65,
    "axes.spines.top": False,
    "axes.spines.right": False,
    "legend.fontsize": 8.7,
    "legend.frameon": False,
    "legend.borderaxespad": 0.25,
    "legend.handlelength": 1.55,
    "legend.handletextpad": 0.50,
    "hatch.linewidth": 0.45,
    "pdf.fonttype": 42,
    "pdf.compression": 9,
    "savefig.facecolor": "white",
})

def save(fig, name):
    fig.savefig(FIGURES / f"{name}.pdf", metadata={"CreationDate": None, "ModDate": None})
    if name == "sequential_disclosure":
        fig.savefig(FIGURES / f"{name}.png", dpi=240)
    plt.close(fig)

def blank(fig, position=(0, 0, 1, 1)):
    ax = fig.add_axes(position, xlim=(0, 1), ylim=(0, 1))
    ax.set_axis_off()
    return ax

def text(ax, x, y, label, **kwargs):
    kwargs.setdefault("ha", "center")
    kwargs.setdefault("va", "center")
    return ax.text(x, y, label, **kwargs)

def line(ax, start, end, color=RULE, width=0.65, **kwargs):
    ax.plot((start[0], end[0]), (start[1], end[1]), color=color, lw=width, **kwargs)

def arrow(ax, start, end, color=GREY, width=0.8):
    patch = FancyArrowPatch(start, end, arrowstyle="-|>", shrinkA=0, shrinkB=0,
                            mutation_scale=8, color=color, lw=width)
    ax.add_patch(patch)

def heading(ax, letter, label, pad=8):
    ax.set_title(f"({letter})  {label}", loc="left", fontsize=10, pad=pad)

def diagram_heading(ax, letter, label):
    text(ax, .015, .95, f"({letter})  {label}", ha="left", fontsize=10, fontweight="bold")

def grid(ax, direction="x"):
    ax.set_axisbelow(True)
    ax.grid(axis=direction, color=GRID, linewidth=.55)

def categories(ax, ticks, labels):
    ax.set_yticks(ticks, labels)
    ax.tick_params(axis="y", length=0, pad=5)
    ax.spines["left"].set_visible(False)

def legend(fig, handles, x, y, columns=2, **kwargs):
    fig.legend(handles=handles, loc="center", bbox_to_anchor=(x, y),
               ncols=columns, columnspacing=1.25, **kwargs)

def contract():
    fig = plt.figure(figsize=(WIDTH, 4.72))
    ax = blank(fig, (0, 0, 1, .975))
    kg_tint, eval_tint, gray_tint = "#edf5f2", "#edf3f8", "#f4f5f6"

    def block(x, y, w, h, fill="white", edge=RULE):
        ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge,
                               linewidth=.7, zorder=.2))

    def cells(x, y, rows, w, h, color):
        for i, row in enumerate(rows):
            for j, observed in enumerate(row):
                block(x + j*w, y - i*h, w - .004, h - .005,
                      color if observed else "white", color)

    def panel_title(letter, title, y, color=INK, subtitle=None):
        text(ax, .024, y, f"({letter})  {title}", ha="left",
             fontsize=10.7, color=color, fontweight="bold")
        if subtitle:
            text(ax, .178, y, subtitle, ha="left", fontsize=9.4)

    panel_title("a", "Comparison contract", .976)
    text(ax, .974, .976, r"$\mathcal{C}=(\tau,\nu,s,\alpha,\mathcal{G})$",
         ha="right", fontsize=12)
    block(.024, .865, .952, .078, gray_tint)
    for i, (symbol, description) in enumerate((
        (r"$\tau$", "Target and reference"),
        (r"$\nu$", "Unit IDs and weights"),
        (r"$s$", "Metric"),
        (r"$\alpha$", "Aggregation"),
        (r"$\mathcal{G}$", "Admissible changes"),
    )):
        left = .024 + i * .1904
        if i:
            line(ax, (left, .878), (left, .930), color=RULE, width=.55)
        text(ax, left + .0952, .919, symbol, fontsize=11.5)
        text(ax, left + .0952, .888, description, fontsize=8.8)
    text(ax, .50, .842,
         r"Reference-defined comparisons  $\ker(U^{\mathsf{T}})=\mathrm{range}(Q)$",
         fontsize=9.6)

    panel_title("b", "PAIR-KG", .807, TEAL, "Compile a molecular contrast")
    signs = (("+", "−"), ("−", "+"))
    for i, row in enumerate(signs):
        for j, sign in enumerate(row):
            x, y = .036 + j*.035, .749 - i*.031
            color = TEAL if sign == "+" else RUST
            block(x, y, .029, .026, kg_tint if sign == "+" else "white", color)
            text(ax, x + .0145, y + .013, sign, fontsize=11, color=color)
    cells(.123, .753, ((1, 1, 0), (0, 1, 1), (1, 0, 1)), .024, .022, TEAL)
    text(ax, .069, .696, "Contrast", fontsize=8.4)
    text(ax, .157, .696, "TRAIN mask", fontsize=8.4)
    text(ax, .107, .661, r"Registered $F_R$", fontsize=8.7)

    block(.229, .683, .173, .084, kg_tint, TEAL)
    block(.449, .683, .232, .084, kg_tint, TEAL)
    block(.749, .683, .227, .084, kg_tint, TEAL)
    text(ax, .3155, .743, "Estimability", fontweight="bold")
    text(ax, .3155, .708, r"$a^{\mathsf{T}}U=0$", fontsize=11)
    text(ax, .565, .785, r"$h^{\mathsf{T}}=a^{\mathsf{T}}X_EF_R$", fontsize=9.8)
    text(ax, .565, .743, "Declared sources", fontweight="bold")
    text(ax, .565, .708, r"$a^{\mathsf{T}}R_E=h^{\mathsf{T}}R_R$", fontsize=10.8)
    text(ax, .717, .785, "Verify witness", fontsize=8.8)
    text(ax, .8625, .743, "Qualified contrast", fontweight="bold", color=TEAL)
    text(ax, .8625, .708, r"Local witness $(a,h,z)$", fontsize=9.3)
    for start, end in ((.201, .229), (.402, .449), (.681, .749)):
        arrow(ax, (start, .725), (end, .725), color=TEAL, width=1.05)

    block(.749, .627, .227, .036)
    block(.749, .581, .227, .036)
    text(ax, .8625, .645, "Measurement only", fontsize=9.1)
    text(ax, .8625, .599, "Refuse", fontsize=9.1)
    line(ax, (.618, .683), (.618, .645), color=GREY, linestyle="--")
    arrow(ax, (.618, .645), (.749, .645), color=GREY)
    text(ax, .687, .660, "Unbound maps", fontsize=8.3)
    for x in (.3155, .484):
        line(ax, (x, .683), (x, .599), color=GREY, linestyle="--")
    arrow(ax, (.3155, .599), (.749, .599), color=GREY)
    text(ax, .599, .614, "Failed or unresolved check", fontsize=8.3)

    line(ax, (.024, .565), (.976, .565), color=GRID)
    panel_title("c", "PAIR-Eval", .542, BLUE, "Verify a model comparison")
    for x, label in zip((.047, .091, .135), (r"$p_A$", r"$p_B$", r"$y$")):
        text(ax, x, .472, label, fontsize=9.2)
    cells(.029, .442, ((1, 1, 1), (1, 1, 0)), .044, .026, BLUE)
    text(ax, .090, .394, "Fixed predictions", fontsize=8.6)
    text(ax, .090, .368, "or recorded scores", fontsize=8.6)
    line(ax, (.164, .447), (.186, .447), color=BLUE)
    line(ax, (.186, .447), (.186, .515), color=BLUE)
    line(ax, (.186, .515), (.856, .515), color=BLUE)

    for left, center, title in (
        (.207, .329, "Response target"),
        (.469, .591, "Observation measure"),
        (.734, .855, "Decision bounds"),
    ):
        block(left, .313, .242, .187, "white", BLUE)
        arrow(ax, (center, .515), (center, .500), color=BLUE)
        block(left, .465, .242, .035, eval_tint, BLUE)
        text(ax, center, .4825, title, fontsize=9.6, color=BLUE, fontweight="bold")

    arrow(ax, (.231, .375), (.352, .375), color=TEAL, width=1.1)
    arrow(ax, (.231, .375), (.352, .446), color=BLUE, width=1.1)
    line(ax, (.352, .375), (.352, .446), color=GREY, linestyle="--")
    text(ax, .302, .439, r"$e_m$", color=BLUE, fontsize=10.3)
    text(ax, .294, .357, r"$Qe_m$", color=TEAL, fontsize=10.0)
    text(ax, .405, .444, "FULL", fontsize=8.5, color=BLUE)
    text(ax, .405, .376, "ID", fontsize=8.6, color=TEAL)
    text(ax, .329, .331, "Target-specific preference", fontsize=8.5)

    for xs in ((.484, .506, .528), (.619, .641, .663)):
        for x in xs:
            block(x, .373, .017, .032, BLUE, BLUE)
    block(.641, .405, .017, .030, "#f3e3d9", RUST)
    text(ax, .514, .444, "Declared", fontsize=8.5)
    text(ax, .653, .444, "After join", fontsize=8.5)
    arrow(ax, (.555, .388), (.608, .388), color=GREY)
    text(ax, .591, .331, "Key-repair witness", fontsize=8.5)

    text(ax, .855, .448, "Archived-label disclosure", fontsize=8.3)
    line(ax, (.885, .365), (.885, .431), color=GREY, linestyle="--")
    for y, start, end, label, color in (
        (.420, .819, .956, "Before", RUST),
        (.383, .828, .866, "After", TEAL),
    ):
        text(ax, .742, y, label, ha="left", fontsize=8.3)
        line(ax, (start, y), (end, y), color=color, width=1.6)
        ax.plot((start, end), (y, y), "|", markersize=6, markeredgewidth=1.0, color=color)
    text(ax, .885, .352, r"$0$", fontsize=8.5)
    text(ax, .855, .331, "Certificate or open bound", fontsize=8.5)

    panel_title("d", "Versioned assertions and queries", .286)
    for y, label, detail, fill, edge in (
        (.187, "Molecular records", "Qualified or measurement only", kg_tint, TEAL),
        (.107, "Evaluation records", "Preference, repair or bound", eval_tint, BLUE),
    ):
        block(.024, y, .240, .058, fill, edge)
        text(ax, .144, y + .040, label, fontsize=9.3, fontweight="bold", color=edge)
        text(ax, .144, y + .016, detail, fontsize=8.25)
    line(ax, (.264, .216), (.303, .216))
    line(ax, (.264, .136), (.303, .136))
    line(ax, (.303, .136), (.303, .216))
    arrow(ax, (.303, .153), (.353, .153))
    block(.353, .106, .349, .075, gray_tint, INK)
    text(ax, .5275, .156, "Comparison assertion", fontsize=10.3, fontweight="bold")
    text(ax, .5275, .126, "Outcome and numerical witness", fontsize=8.8)
    for x, label in ((.353, "Contract and version"), (.532, "Source evidence")):
        block(x, .211, .170, .035)
        text(ax, x + .085, .2285, label, fontsize=8.6)
        arrow(ax, (x + .085, .181), (x + .085, .211))
    arrow(ax, (.702, .153), (.759, .153))
    block(.759, .106, .217, .108)
    text(ax, .8675, .187, "SPARQL", fontsize=9.7, fontweight="bold")
    text(ax, .8675, .157, "Current comparisons", fontsize=8.6)
    text(ax, .8675, .128, "Certificates and budgets", fontsize=8.45)
    text(ax, .50, .057, "Rebind and verify when the comparison contract changes",
         fontsize=9.0, color=GREY)
    save(fig, "comparison_contract")

def matrix2(ax, x, y, width, height, values, col_labels, row_labels):
    for col in range(2):
        text(ax, x + (col + .5) * width, y + 2 * height + .066, col_labels[col])
    for row in range(2):
        centre_y = y + (1.5 - row) * height
        text(ax, x - .043, centre_y, row_labels[row])
        for col in range(2):
            value = values[row][col]
            centre_x = x + (col + .5) * width
            rect = Rectangle((x + col * width, centre_y - height / 2), width, height,
                             ec=RULE, fc="white", hatch="////" if value is None else None, lw=.65)
            ax.add_patch(rect)
            if value == "dot":
                ax.plot(centre_x, centre_y, "o", color=INK, ms=3.5)
            elif value is not None:
                text(ax, centre_x, centre_y, value, color=BLUE if "+" in value else RUST, fontsize=10.5)

def overview():
    fig = plt.figure(figsize=(WIDTH, 4.05))
    a = blank(fig, (.015, .526, .458, .453))
    b = blank(fig, (.517, .526, .467, .453))
    c = blank(fig, (.015, .018, .458, .453))
    d = blank(fig, (.517, .018, .467, .453))
    diagram_heading(a, "a", "Measured inputs and reference")
    text(a, .26, .786, "Evaluation cells", fontsize=9.4)
    text(a, .75, .786, "Training reference", fontsize=9.4)
    columns, rows = [r"$e_1$", r"$e_2$"], [r"$r_1$", r"$r_2$"]
    matrix2(a, .12, .295, .14, .159,
            [[r"$+Y_{11}$", r"$-Y_{12}$"], [r"$-Y_{21}$", r"$+Y_{22}$"]], columns, rows)
    matrix2(a, .61, .295, .14, .159, [["dot", None], ["dot", "dot"]], columns, rows)
    text(a, .26, .228, r"$a,\,X_E,\,Y_E$")
    text(a, .75, .228, r"$X_R,\,Y_R$")
    line(a, (.05, .156), (.95, .156), color=GRID)
    text(a, .50, .098, r"Completion $F_R$ and shared-source maps $R_R,\,R_E$", fontsize=9.6)
    text(a, .50, .015, r"$X_RF_RX_R=X_R$", fontsize=10.3)

    diagram_heading(b, "b", "Shared quotient geometry")
    text(b, .50, .775, r"$U=X_E N_R,\qquad Q=I-P_U$", fontsize=12)
    text(b, .21, .593, r"$y$", fontsize=13)
    text(b, .79, .593, r"$y+Ut$", fontsize=13)
    arrow(b, (.255, .528), (.443, .350), color=BLUE)
    arrow(b, (.745, .528), (.557, .350), color=BLUE)
    text(b, .32, .398, r"$Q$", fontsize=11)
    text(b, .68, .398, r"$Q$", fontsize=11)
    text(b, .50, .296, r"$Qy$", fontsize=13)
    line(b, (.05, .156), (.95, .156), color=GRID)
    text(b, .50, .063, r"$\ker(U^{\mathsf{T}})=\mathrm{range}(Q)$", fontsize=13)

    diagram_heading(c, "c", "PAIR-KG local witness")
    conditions = [
        ("Bind the completion", r"$h^{\mathsf{T}}=a^{\mathsf{T}}X_EF_R$"),
        ("Check reference support", r"$h^{\mathsf{T}}X_R=a^{\mathsf{T}}X_E$"),
        ("Check declared sources", r"$a^{\mathsf{T}}R_E=h^{\mathsf{T}}R_R$"),
        ("Verify the readout", r"$z=a^{\mathsf{T}}Y_E-h^{\mathsf{T}}Y_R$"),
    ]
    for i, (label, eq) in enumerate(conditions):
        y = .755 - .145 * i
        text(c, .035, y, label, ha="left", fontsize=9.1)
        text(c, .97, y, eq, ha="right", fontsize=10.5)
    line(c, (.035, .226), (.97, .226), color=GRID)
    text(c, .035, .118, "Qualified relation", ha="left", fontweight="bold")
    text(c, .97, .118, r"$(a,h,z)$", ha="right", fontsize=11.5)

    diagram_heading(d, "d", "PAIR-Eval loss and decision")
    text(d, .50, .773, r"$\|e_m\|^2=\|Qe_m\|^2+\|P_Ue_m\|^2,\quad e_m=y-p_m$", fontsize=11)
    line(d, (.05, .648), (.95, .648), color=INK, width=.75)
    for x, title, va, vb in [(.23, "Model", "A", "B"), (.52, "FULL", "200", "2"), (.81, "ID", "0", "2")]:
        text(d, x, .565, title, fontweight="bold")
        text(d, x, .410, va, fontsize=10.2)
        text(d, x, .290, vb, fontsize=10.2)
    line(d, (.05, .485), (.95, .485), color=RULE)
    line(d, (.05, .209), (.95, .209), color=INK, width=.75)
    text(d, .50, .093, "A strict preference has a fixed sign over completions.", fontsize=9.1)
    save(fig, "figure_01")

def retention():
    fig = plt.figure(figsize=(WIDTH, 2.70))
    ax = fig.add_axes((.142, .215, .382, .55))
    heading(ax, "a", "Compound-only dimensions", pad=17)
    panel = DATA["retention"]
    for i, row in enumerate(panel):
        value = 100 * row["retained"] / row["unsupported"]
        ax.barh(i, value, height=.33, color=BLUE, zorder=3)
        ax.text(value + .65, i, f"{value:.2f}%", va="center", fontsize=9.15)
        ax.text(.55, i + .24, f'{row["retained"]:,} / {row["unsupported"]:,}', va="top", fontsize=8.5)
    categories(ax, range(2), [row["assay"] for row in panel])
    ax.set(xlim=(0, 34), ylim=(1.63, -.47), xticks=[0, 10, 20, 30],
           xlabel="Retained / unsupported (%)")
    grid(ax)

    fig.text(.608, .878, "(b)  Replicate-common covariance", fontsize=10)
    for i, row in enumerate(DATA["covariance"]):
        start = (.575, .244)[i]
        ax = fig.add_axes((.615, start, .356, .119))
        d0, d1 = row["dimension"]
        lo, hi = row["range"]
        stop = row["scale"]
        color = BLUE if i == 0 else TEAL
        text(ax, 0, 1.60, row["assay"], ha="left", transform=ax.transAxes, fontsize=9.3, fontweight="bold")
        text(ax, 1, 1.60, rf"$d$ = {d0:,}–{d1:,}", ha="right", transform=ax.transAxes, fontsize=8.7)
        ax.hlines(.39, lo, hi, color=color, lw=1.65)
        ax.vlines([lo, hi], .25, .53, color=color, lw=1.15)
        text(ax, (lo + hi) / 2, .80, f"{lo:.3f}–{hi:.3f}", fontsize=8.7)
        ax.set(xlim=(0, stop), ylim=(0, 1.1), xticks=np.linspace(0, stop, 4),
               yticks=[])
        ax.xaxis.set_major_formatter(mpl.ticker.FormatStrFormatter("%.2f"))
        ax.spines["left"].set_visible(False)
    fig.text(.797, .067, r"Covariance $\widehat{S}$ (assay-specific scales)", ha="center", fontsize=9.4)
    save(fig, "figure_02")

def replogle():
    fig = plt.figure(figsize=(WIDTH, 3.02))
    a = blank(fig, (.015, .593, .97, .39))
    b = blank(fig, (.015, .025, .445, .494))
    c = blank(fig, (.493, .025, .492, .494))
    diagram_heading(a, "a", "Registered response")
    for x, label, eq in [
        (.16, "Raw expression", r"$X_{ig}^{\rm raw}$"),
        (.50, "UMI normalization", r"$\widetilde X_{ig}=10^4X_{ig}^{\rm raw}/\mathrm{UMI}_i$"),
        (.835, "Matched control subtraction", r"$Y_{bpg}=P_{bpg}-C_{bg}$"),
    ]:
        text(a, x, .606, label, fontweight="bold", fontsize=9.65)
        text(a, x, .350, eq, fontsize=12.2)
    arrow(a, (.245, .352), (.309, .352))
    arrow(a, (.685, .352), (.748, .352))
    line(a, (.015, .077), (.985, .077), color=GRID)

    diagram_heading(b, "b", "Four-term query in one GEM group")
    matrix2(b, .125, .234, .156, .197, [[r"$+1$", r"$-1$"], [r"$-1$", r"$+1$"]],
            [r"$g_1$", r"$g_2$"], [r"$p_1$", r"$p_2$"])
    arrow(b, (.46, .434), (.555, .434))
    text(b, .765, .620, r"$a^{\mathsf{T}}X_E=0,\quad h=0$", fontsize=10.8)
    text(b, .765, .405, r"$a^{\mathsf{T}}R_E=0$", fontsize=10.8)
    text(b, .765, .202, r"$\delta_{\rm source}=0$", fontsize=10.8)
    text(b, .11, .070, "Coefficients", ha="left", fontsize=8.9)

    diagram_heading(c, "c", "Reference and source qualification")
    locations = [(.045, "Query", "left"), (.604, "Identifiable", "center"), (.855, "Source-safe", "center")]
    line(c, (.04, .795), (.985, .795), color=INK, width=.75)
    for x, label, align in locations:
        text(c, x, .717, label, ha=align, fontweight="bold", fontsize=9.2)
    line(c, (.04, .638), (.985, .638))
    for i, row in enumerate([
        ("Q1  Atomic", "No", "No"), ("Q2  Perturbation", "No", "Yes"),
        ("Q3  Gene", "No", "No"), ("Q4  Four-term", "Yes", "Yes")
    ]):
        for value, (x, _, align) in zip(row, locations):
            text(c, x, .554 - i * .125, value, ha=align, fontsize=9.1,
                 fontweight="bold" if i == 3 else "normal")
    line(c, (.04, .102), (.985, .102), color=INK, width=.75)
    text(c, .045, .018, "100,000 Q4 designs satisfy both conditions.", ha="left", fontsize=8.8)
    save(fig, "figure_03")

def public_targets():
    fig = plt.figure(figsize=(WIDTH, 2.66))
    a = fig.add_axes((.108, .192, .348, .585))
    b = fig.add_axes((.629, .192, .336, .585))
    heading(a, "a", "Reversals by fold", pad=17)
    heading(b, "b", "Persistent pairwise differences", pad=17)
    panel = DATA["target_reversals"]
    for key, label, color, marker, style in [
        ("r2", r"$R^2$", BLUE, "o", "-"), ("pearson", "Pearson", RUST, "s", "--")
    ]:
        a.plot([row["fold"] for row in panel], [100 * row[key] / 406 for row in panel],
               marker=marker, ls=style, ms=3.6, lw=1, color=color, label=label)
    a.set(xlim=(-.34, 9.34), ylim=(0, 9), xticks=range(10), yticks=[0, 2, 4, 6, 8],
          xlabel="Outer fold", ylabel="Reversed model pairs (%)")
    grid(a, "y")
    a.legend(loc="upper right", ncols=2, columnspacing=.9)
    panel = DATA["target_contrasts"]
    for shift, key, label, color, marker in [
        (-.12, "full", "FULL", BLUE, "o"), (.12, "id", "ID", RUST, "s"),
    ]:
        for i, row in enumerate(panel):
            lo, mid, hi = (row[key][name] for name in ("min", "median", "max"))
            b.errorbar(mid, i + shift, xerr=[[mid-lo], [hi-mid]], fmt=marker, color=color,
                       lw=1.0, capsize=2, ms=4.0, mfc="white" if key == "id" else color)
    b.axvline(0, linewidth=.75, color=RULE)
    categories(b, range(3), [row["model"] for row in panel])
    b.set(xlim=(-.20, .23), ylim=(2.63, -.56), xticks=[-.2, -.1, 0, .1, .2],
          xlabel=r"$R^2$ difference from MOLIR")
    legend(fig, [
        Line2D([], [], ls="none", marker="o", color=BLUE, label="FULL", ms=4.2),
        Line2D([], [], ls="none", marker="s", color=RUST, mfc="white", label="ID", ms=4.2),
    ], .803, .833)
    save(fig, "public_target_comparison")

def repairs():
    fig = plt.figure(figsize=(WIDTH, 2.68))
    a = fig.add_axes((.082, .190, .337, .612))
    b = fig.add_axes((.519, .190, .438, .612))
    heading(a, "a", "Minimum repair size", pad=13)
    heading(b, "b", "Change in mean-score margins", pad=13)
    panel = DATA["mean_repairs"]
    for i, row in enumerate(panel):
        n = row["keys"]
        a.barh(i, n, height=.45, color=BLUE, zorder=3)
        a.text(n + .85, i, str(n), va="center", fontsize=8.7)
        x1, x2 = (1000 * row[key] for key in ("unchecked", "repaired"))
        line(b, (x1, i), (x2, i), color=RULE, width=1)
        b.plot(x1, i, marker="o", color=RUST, mfc="white", ms=5, mew=1)
        b.plot(x2, i, marker="s", color=BLUE, ms=4.5, mew=.7)
    labels = [row["case"] for row in panel]
    for ax in (a, b):
        categories(ax, range(5), labels)
        ax.set_ylim(4.69, -.66)
    a.set(xlim=(0, 65), xticks=[0, 20, 40, 60], xlabel="Corrected lookup keys")
    b.set(xlim=(-8.1, 8.1), xticks=[-8, -4, 0, 4, 8],
          xlabel=r"Mean normalized $R^2$ difference ($10^{-3}$)")
    grid(a)
    b.axvline(0, color=GREY, lw=.75, zorder=0)
    legend(fig, [
        Line2D([], [], color=RUST, marker="o", ls="none", mfc="white", label="Unchecked", ms=4.9),
        Line2D([], [], color=BLUE, marker="s", ls="none", label="Repaired", ms=4.4),
    ], .743, .835, handlelength=1.0)
    save(fig, "repair_and_materiality")

def disclosure():
    fig = plt.figure(figsize=(WIDTH, 2.85))
    a = fig.add_axes((.110, .207, .348, .645))
    b = fig.add_axes((.595, .207, .369, .645))
    heading(a, "a", "Labels needed for a certificate", pad=10)
    heading(b, "b", "Certificates by label budget", pad=10)
    a.plot([80, 100], [80, 100], "--", lw=.7, color=RULE)
    for metric, label, color, marker in [
        ("roc_auc", "AUC", BLUE, "o"), ("log_loss", "Log loss", RUST, "s"),
    ]:
        rows = [row for row in DATA["disclosure"] if row["metric"] == metric]
        a.scatter([100*row["random"] for row in rows], [100*row["adaptive"] for row in rows],
                  label=label, marker=marker, s=19, edgecolors=color, linewidths=.9,
                  facecolors="white" if metric == "log_loss" else color, zorder=4)
    a.set(xlim=(80, 102), ylim=(0, 105), yticks=[0, 25, 50, 75, 100], xticks=[80, 85, 90, 95, 100],
          xlabel="Mean random disclosure (%)", ylabel="Adaptive expected gain (%)")
    a.legend(loc="lower left", handlelength=1, borderaxespad=.5)
    for key, label, color, dash, marker in [
        ("adaptive_expected_gain", "Adaptive expected gain", BLUE, "-", "o"),
        ("expected_gain", "Fixed expected gain", TEAL, "--", "^"),
        ("width", "Interval width", PURPLE, "-.", "D"),
        ("entropy", "Predictive entropy", RUST, (0, (2, 1)), "s"),
        ("random", "Random", GREY, ":", "x"),
    ]:
        values = np.asarray(DATA["certificate_curves"][key]) * 100
        b.plot(values[:, 0], values[:, 1], label=label, ls=dash, lw=1.34 if key == "adaptive_expected_gain" else .9,
               color=color, marker=marker, ms=3.1, mew=.85)
    b.set(xlim=(0, 101), ylim=(0, 105), yticks=[0, 25, 50, 75, 100], xticks=[0, 25, 50, 75, 100],
          xlabel="Disclosed labels (%)", ylabel="Task-averaged certification rate (%)")
    b.legend(loc="upper left", fontsize=8.25, labelspacing=.29, handlelength=1.8, borderaxespad=.6)
    grid(a, "y")
    grid(b, "y")
    save(fig, "sequential_disclosure")

def historical():
    fig = plt.figure(figsize=(WIDTH, 2.73))
    a = fig.add_axes((.162, .194, .411, .600))
    b = blank(fig, (.633, .190, .332, .646))
    heading(a, "a", "Median foldwise pair reversals", pad=15)
    panel = DATA["historical_ldo"]
    for key, color, off, marker in [
        ("r2_median", BLUE, -.115, "o"), ("pearson_median", RUST, .115, "s"),
    ]:
        points = 100 * np.asarray(panel[key])
        a.scatter(points, np.arange(5) + off, marker=marker, s=22, color=color,
                  facecolor="white" if key == "pearson_median" else color, zorder=4)
    categories(a, range(5), panel["cohorts"])
    a.set(xlim=(0, 58), ylim=(4.62, -.62), xticks=[0, 10, 20, 30, 40, 50],
          xlabel="Reversed model pairs (%)")
    grid(a)
    legend(fig, [
        Line2D([], [], ls="none", color=BLUE, marker="o", label=r"Normalized $R^2$", ms=4),
        Line2D([], [], ls="none", color=RUST, marker="s", mfc="white", label="Normalized Pearson", ms=4),
    ], .364, .832, handlelength=1.1)
    text(b, .035, 1.085, "(b)  Persistent pairs (≥7/10 folds)", ha="left", fontsize=10)
    for x, label in [(.37, r"n$R^2$"), (.76, "nPearson")]:
        text(b, x, .938, label, fontweight="bold")
    line(b, (.12, .872), (.92, .872), color=INK)
    for i, (r2, pearson) in enumerate(zip(panel["r2_persistent"], panel["pearson_persistent"])):
        for x, value in [(.37, r2), (.76, pearson)]:
            text(b, x, .826 - .1775 * i, str(value), fontweight="bold" if value else "normal")
    line(b, (.12, .014), (.92, .014), color=INK)
    save(fig, "figure_04")

def apa_aggregation():
    fig = plt.figure(figsize=(WIDTH, 2.5))
    a = fig.add_axes((.145, .215, .318, .622))
    b = fig.add_axes((.659, .215, .306, .622))
    heading(a, "a", "Archived prediction losses", pad=10)
    heading(b, "b", "CARE versus JFE-WALS", pad=10)
    vals = DATA["archived_apa_losses"]
    for i, value in enumerate(vals["mse"]):
        a.hlines(i, 0, value, color=RULE, lw=.9)
        a.plot(value, i, "o", ms=4.3, color=BLUE)
        a.text(value + .008, i, f"{value:.5f}", va="center", fontsize=8.8)
    categories(a, range(4), vals["methods"])
    a.set(xlim=(0, .255), ylim=(3.55, -.57), xticks=[0, .1, .2], xlabel="Mean squared loss")
    grid(a)
    for i, value in enumerate(np.asarray(vals["contrasts"]) * 10000):
        color = BLUE if value < 0 else RUST
        b.hlines(i, min(0, value), max(0, value), color=color, lw=1.1)
        b.plot(value, i, marker="o" if i == 0 else "s", color=color, ms=4.2)
        b.text(value + (-.57 if value < 0 else .45), i, f"{value:+.3f}",
               ha="right" if value < 0 else "left", va="center", fontsize=8.8)
    categories(b, range(2), ["Mean of\nstored losses", "Loss of\nmean prediction"])
    b.axvline(0, color=RULE, lw=.7)
    b.set(xlim=(-8.5, 9.4), ylim=(1.54, -.51), xticks=[-5, 0, 5],
          xlabel=r"Difference in MSE ($10^{-4}$)")
    save(fig, "supp_figure_01")

def k562_status():
    fig = plt.figure(figsize=(WIDTH, 1.82))
    ax = fig.add_axes((.227, .28, .689, .59))
    vals = DATA["k562_compiler"]
    for i, (key, color) in enumerate([("nonidentifiable", GREY), ("retained", BLUE)]):
        size = vals[key]
        ax.barh(i, size, height=.4, color=color, zorder=3)
        ax.text(size + 42, i, f"{size:,}", va="center")
    categories(ax, range(2), ["Non-identifiable", "Retained comparison"])
    ax.set(xlim=(0, 3200), ylim=(1.53, -.54), xticks=[0, 1000, 2000, 3000], xlabel="Archived requests")
    grid(ax)
    save(fig, "supp_figure_02")

def shared_action():
    fig = plt.figure(figsize=(WIDTH, 2.74))
    a = fig.add_axes((.127, .184, .318, .64))
    b = blank(fig, (.510, .123, .466, .735))
    heading(a, "a", "Quotient projection", pad=10)
    text(b, .025, 1.027, "(b)  Loss and shared translation", ha="left", fontsize=10)
    a.plot([1, 1], [0, 3], "--", color=RULE, lw=.8)
    a.plot(0, 0, "o", color=INK, ms=4.5, clip_on=False)
    a.plot(1, 3, "o", color=BLUE, ms=5)
    a.plot(1, 0, "o", color=BLUE, ms=4.5, mfc="white", clip_on=False)
    a.plot(2, 0, "s", color=RUST, ms=4.8, clip_on=False)
    a.text(.12, .23, r"$y=(0,0)$", fontsize=9.5)
    a.text(1.10, 3.02, r"$p_A=(1,3)$", fontsize=9.5)
    a.text(2.09, .23, r"$p_B=(2,0)$", fontsize=9.5)
    a.set(xlim=(0, 3.15), ylim=(0, 3.78), xticks=range(4), yticks=range(4),
          xlabel="Identified coordinate", ylabel="Unresolved coordinate")
    line(b, (.025, .823), (.972, .823), color=INK, width=.75)
    for x, label in [(.12, "Target"), (.51, r"$L_A$"), (.68, r"$L_B$"), (.86, "Lower loss")]:
        text(b, x, .74, label, fontweight="bold")
    line(b, (.025, .66), (.972, .66), color=RULE)
    for y, row in [(.581, ("FULL", "10", "4", "B")), (.449, ("ID", "1", "4", "A"))]:
        for x, value in zip((.12, .51, .68, .86), row):
            text(b, x, y, value)
    line(b, (.025, .355), (.972, .355), color=INK, width=.75)
    text(b, .49, .249, r"$Q=\mathrm{diag}(1,0)$", fontsize=11)
    text(b, .49, .092, r"$(y+u)-(p_m+u)=y-p_m$", fontsize=12)
    save(fig, "supp_figure_03")

def encode():
    fig = plt.figure(figsize=(WIDTH, 2.35))
    ax = fig.add_axes((.237, .206, .727, .598))
    panel = DATA["encode_losses"]
    for i, (compound, unit) in enumerate(zip(panel["compound"], panel["unitwise"])):
        left, right = 1000*compound, 1000*unit
        ax.hlines(i, left, right, color=RULE, lw=1.0)
        ax.plot(left, i, marker="o", color=BLUE, ms=5.0)
        ax.plot(right, i, marker="s", color=RUST, ms=4.8, mfc="white")
        text(ax, left - .114, i, f"{left:.3f}", ha="right", fontsize=8.9)
        text(ax, right + .112, i, f"{right:.3f}", ha="left", fontsize=8.9)
    categories(ax, range(3), panel["models"])
    ax.set(xlim=(1.5, 6.6), ylim=(2.53, -.58), xticks=[2, 3, 4, 5, 6],
           xlabel=r"Loss on the scored component ($10^{-3}$)")
    grid(ax)
    legend(fig, [
        Line2D([], [], ls="none", color=BLUE, marker="o", label="Compound-only", ms=5),
        Line2D([], [], ls="none", color=RUST, marker="s", mfc="white", label="Unitwise-supported", ms=5),
    ], .601, .870)
    save(fig, "supp_figure_04")

if __name__ == "__main__":
    FIGURES.mkdir(exist_ok=True)
    for draw in (contract, overview, retention, replogle, public_targets, repairs,
                 disclosure, historical, apa_aggregation, k562_status, shared_action, encode):
        draw()
