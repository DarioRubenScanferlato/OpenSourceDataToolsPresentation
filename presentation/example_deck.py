"""Reference deck - one slide per helper in ``template/``.

Run it:      uv run marimo edit presentation/example_deck.py
Present it:  uv run marimo run presentation/example_deck.py --include-code

Copy this file as the starting point for the real talk, delete what you don't
need, and keep ``layouts/example_deck.slides.json`` in step with the cell list
(see the last cell, or rebuild the layout in the app-preview dropdown).
"""

import marimo

__generated_with = "0.24.0"
app = marimo.App(
    width="medium",
    layout_file="layouts/example_deck.slides.json",
    css_file="template/nearform.css",
)


@app.cell
def _():
    import marimo as mo

    from template import assets, nf, theme

    return assets, mo, nf


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # notes
    The increases in main-memory sizes over the last decade have made pure in-memory database systems feasible, and in-memory systems offer unprecedented performance. However, DRAM is still relatively expensive, and the growth of main-memory sizes has slowed down. In contrast, the prices for SSDs have fallen substantially in the last years, and their read bandwidth has increased to gigabytes per second. This makes it attractive to combine a large in-memory buffer with fast SSDs as storage devices, combining the excellent performance for the in-memory working set with the scalability of a disk-based system.
    - SSAS vertipaq import mode can be considered in-memory
    """)
    return


@app.cell
def _(nf):
    nf.title_slide(
        "From raw data to dashboard with open source software",
        event="Ticino Data Conference - 2026",
        author="Dario Ruben Scanferlato, Nearform",
    )
    return


@app.cell
def _(assets, nf):
    nf.speaker(
        name="Dario Ruben Scanferlato",
        role="Senior Data Engineer @ Nearform",
        handle="dario.scanferlato@gmail.com",
        photo=assets.img("images/profilepic.jpg"),
        page=2,
    )
    return


@app.cell
def _(nf):
    nf.section("What we are building", kicker="OS Data Platform")
    return


@app.cell
def _(nf):
    nf.slide(
        nf.lead(
            "Every layer of the stack is open source, and every layer has a "
            "managed equivalent someone will try to sell you."
        ),
        nf.bullets(
            [
                "**Ingestion** - the part everyone underestimates",
                "**Storage** - object storage plus an open table format",
                "**Transformation** - where the lock-in usually hides",
                "**Serving** - the only layer your users actually see",
            ]
        ),
        title="Four layers",
        page=4,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.stats(
            [
                ("15m+", "Downloads", "every week"),
                ("1192k+", "Contributions", "every year"),
                ("166+", "Packages", "maintained by us"),
                ("10+", "Years", "of open source at Nearform"),
            ]
        ),
        title="Open source at Nearform",
        kicker="Why us",
        page=5,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.two_col(
            nf.body(
                "Node.js is an open source, cross-platform JavaScript runtime. "
                "Nearform has been instrumental to its development since the "
                "earliest releases."
            ),
            nf.metrics(
                [
                    ("57.3m", "Lines of code changed"),
                    ("25", "Employee contributors"),
                    ("7.1k", "Contributions"),
                    ("7th", "Most active contributor"),
                ]
            ),
            ratio=(3, 2),
        ),
        title="We love Node.js",
        kicker="Nearform OSS",
        page=6,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.quote(
            "At the heart of Nearform's mission is a profound commitment to the "
            "Node.js ecosystem and the OpenJS Foundation.",
            author="Robin Ginn",
            role="Executive Director, OpenJS Foundation",
        ),
        page=7,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.cards(
            [
                ("Iceberg", "Open table format. Catalog is the hard part."),
                ("DuckDB", "The engine that made local analytics fun again."),
                ("marimo", "This deck. Reactive notebook, reveal.js underneath."),
            ]
        ),
        title="The pieces",
        page=8,
    )
    return


@app.cell
def _(nf):
    nf.slide(
        nf.code(
            """
            import duckdb

            con = duckdb.connect()
            con.sql("INSTALL iceberg; LOAD iceberg;")
            con.sql("SELECT count(*) FROM iceberg_scan('s3://lake/events')")
            """
        ),
        nf.caption("Runs against the local MinIO stack - no cloud account needed."),
        title="Reading the lake",
        page=9,
    )
    return


@app.cell
def _(mo, nf):
    # Anything marimo can render drops straight into a slide.
    _demo = mo.ui.slider(1, 10, value=4, label="partitions")
    nf.slide(_demo, title="Live, on the slide", kicker="Demo", page=10)
    return


@app.cell
def _(nf):
    nf.slide(
        nf.bullets(
            [
                "Nearform Brand Hub - logos, fonts, the full deck template",
                "github.com/nearform - everything we maintain",
                "nearform.com/careers - we're hiring",
            ],
            tone="pale",
        ),
        title="Resources",
        tone="pale",
        page=11,
    )
    return


@app.cell
def _(nf):
    nf.closing("Questions", page=12)
    return


@app.cell
def _():
    # Rebuild layouts/example_deck.slides.json after adding or removing cells.
    # One entry per cell, in order - the first one is the import cell, hence SKIP.
    #
    #     from template import SKIP, Cell, write_slides_layout
    #     write_slides_layout(
    #         "presentation/example_deck.py",
    #         [SKIP, Cell(notes="30s - who I am"), ...],
    #     )
    return


if __name__ == "__main__":
    app.run()
