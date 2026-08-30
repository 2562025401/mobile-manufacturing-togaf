# Mobile Manufacturing Enterprise Architecture Case (mobile-manufacturing-togaf)

> A **complete Enterprise Architecture (EA) planning case study for the mobile-phone manufacturing industry**, covering the four TOGAF architecture domains (Business / Data / Application / Technology) plus Strategy and Implementation — and including a **requirements & design document that can directly drive AI-assisted coding** to build an enterprise-architecture visualization system.

This repository is for: enterprise architects, digital-transformation leads, consultants, and engineering teams who want to use **AI Coding** to quickly stand up an architecture-asset visualization platform.

---

## 1. What's Inside

```
mobile-manufacturing-togaf/
├── 第0章 手机厂商企业架构规划总纲.md        # Overview: scope, method, 4A relations, LTC spine
├── 第1章_企业战略与业务目标.md              # Strategy: PEST, strategy house, strategy map, KPIs
├── 第2章_业务架构.md                        # Business Arch.: capability map, value streams, LTC, RACI
├── 第3章_数据架构.md                        # Data Arch.: subject domains, conceptual/logical models, MDM
├── 第4章_应用架构.md                        # Application Arch.: portfolio, capability centers, API, microservices
├── 第5章_技术架构.md                        # Technology Arch.: tech mid-platform, cloud, deployment, DR
├── 第6章_实施规划.md                        # Implementation: roadmap, migration waves, benefits, governance
├── 架构可视化浏览系统_需求与设计方案.md      # ★ Blueprint to implement the whole system via AI coding (see §3)
├── html/                                   # 76 ECharts / D3 visualization HTML prototypes (open in browser)
├── image/                                  # Diagram assets (Excel screenshots / HTML renders, ~55MB)
├── ea-ltc-demo/                            # Runnable LTC knowledge-graph prototype (Python + interactive HTML)
└── 附件/                                   # 50+ Excel / Word source-data attachments
```

| Category | Volume | Notes |
|----------|--------|-------|
| Planning docs | 7 Markdown files (Ch.0–6) | Full-chain EA planning, strategy → implementation |
| Visualization prototypes | 76 HTML files in `html/` | Strategy house, capability map, data model, microservice split, etc. |
| Knowledge-graph prototype | `ea-ltc-demo/` | Runnable LTC end-to-end knowledge network (Python + HTML) |
| Raw data | 50+ files in `附件/` | Structured Excel attachments + 1 Word note |
| Diagram assets | `image/` ~55MB | PNG diagrams |

> Note: the repo contains binary assets (`image/` ~55MB, xlsx in `附件/`), totaling ~60MB — keep this in mind when cloning.

---

## 2. What This Case Study Helps You Do

1. **Learn TOGAF in practice** — see how a real industry (mobile manufacturing) decomposes strategy down to business domains → capabilities → data objects → applications → technology platforms, with **LTC (Lead-to-Cash) end-to-end process** as the贯穿 (through-line).
2. **Reuse as your own EA plan** — the chapter structure, table schemas, and charts are generic templates; swap in your industry content.
3. **Drive development directly** — §3 explains how, using only `架构可视化浏览系统_需求与设计方案.md`, an AI coding tool can **generate the entire EA visualization system end-to-end**.

---

## 3. 🤖 Build the "Whole EA Visualization System" with AI Coding

> **Key point**: `架构可视化浏览系统_需求与设计方案.md` is not a vague idea doc — it is a **structured engineering blueprint ready to be fed to an AI coding tool**. It pins down the tech stack, logical architecture, database tables, API groups, and every page's layout & visualization library. Therefore **no one needs to hand-write the system from scratch** — hand this document (together with the 6 chapters, the Excel attachments, and the existing `html/` & `ea-ltc-demo/` prototypes) to an AI coding tool and it can generate a runnable system.

### 3.1 Why It Is "AI-Coding Ready"

What the design doc already specifies:

- **Tech stack**: Backend `Python 3.11+ / Flask / SQLite`; Frontend `React 18 + TypeScript + Vite + Shadcn UI + Tailwind CSS`; Visualization `AntV X6 / ECharts / Mermaid`.
- **Logical architecture**: React frontend → Flask REST API → SQLite metadata model → raw-asset layer (Markdown / Excel / HTML diagrams).
- **Database tables**: document, business-architecture, data-architecture, application-architecture, technology-architecture, LTC-mapping, API, matrix, generic-relation-edge, version.
- **API groups**: Document / Architecture / LTC / Matrix / Impact / Metadata / Import / Search.
- **Ten modules**: Overview, Business Arch., Data Arch., Application Arch., Technology Arch., LTC drill-through, Matrix analysis, Impact analysis, Metadata management, Document library — each with **page-layout sketch + tree hierarchy + right-pane rendering spec**.
- **Visualization mapping**: which chart uses X6, ECharts, Mermaid, or Shadcn Table is specified per page.

→ To an AI coding tool this is essentially "requirements spec + technical design", enough to generate the scaffold and most business code.

### 3.2 Recommended Flow (4 steps)

```
Step 1  Ingest & structure assets
        Parse the 6 chapters + 50+ Excel → extract into SQLite metadata
        (business domains/capabilities, data domains/objects, apps/APIs,
         tech components, LTC mappings, relation edges)

Step 2  Backend scaffold (Flask + SQLite)
        Implement the 8 API groups from the doc; add SQLAlchemy models
        and an import script that loads Markdown/Excel into SQLite

Step 3  Frontend + visualization (React + TS + Vite + Shadcn + Tailwind)
        Build the ten module pages; X6 for architecture/drill-through,
        ECharts for knowledge-graph/radar/heatmap, Mermaid for flowcharts,
        Markdown Viewer for chapters

Step 4  Reuse existing prototypes — don't rebuild from zero
        The 76 ECharts prototypes in html/ are chart seeds;
        ea-ltc-demo/ LTC knowledge graph is the base for Impact/Network views
```

### 3.3 Sample Prompt for an AI Coding Tool (copy-paste)

> Use this as the first message and provide the repo as workspace context:

```
Based on 《架构可视化浏览系统_需求与设计方案.md》 plus Ch.0–6, the Excel
files in 附件/, and the html/ & ea-ltc-demo/ prototypes, build an
enterprise-architecture visualization system:

- Backend: Python 3.11 + Flask + SQLite. Implement the 8 REST API groups
  (Document/Architecture/LTC/Matrix/Impact/Metadata/Import/Search) from the
  doc; write an import script that extracts architecture metadata from the
  Markdown and Excel and loads it into SQLite.
- Frontend: React 18 + TypeScript + Vite + Shadcn UI + Tailwind CSS. Implement
  the ten modules with the left tree-browser + right workspace layout.
- Visualization: AntV X6 for architecture & LTC drill-through; ECharts for
  knowledge graph / radar / heatmap; Mermaid for flowcharts; reuse html/ and
  ea-ltc-demo/ as seeds.
- Pause for my confirmation after each module before continuing.
```

### 3.4 Supported Tools

| Tool | How to use |
|------|------------|
| **WorkBuddy / Claude Code** | Load the repo as skill/project context and paste the §3.3 prompt to trigger multi-step implementation |
| **Codex / Cursor / Cline / Aider** | Inject the design doc + `ea-ltc-demo/` + `html/` as context; generate in batches per the 4-step flow |
| Any AI coding agent that "reads repos + runs commands" | Same — the key is **first have the agent read `架构可视化浏览系统_需求与设计方案.md`** |

---

## 4. View Locally (No Install Needed)

- **Visualization prototypes**: double-click any `.html` in `html/` (e.g. `图2-3_业务能力地图.html`) — interactive in the browser.
- **LTC knowledge graph**: open `ea-ltc-demo/LTC知识网络图.html` in a browser; to regenerate, run `python build_ltc_knowledge_graph.py` (Python 3.11+).
- **Excel attachments**: open the `.xlsx` files in `附件/` with Excel / WPS / an online spreadsheet.

---

## 5. License

Released under the **MIT License** — free to study, modify, and redistribute. Attribution is appreciated if used in commercial consulting. See [LICENSE](./LICENSE).

---

## 6. Quick Index

| You want to… | Go to |
|--------------|-------|
| Understand the overall method | `第0章 手机厂商企业架构规划总纲.md` |
| See how strategy is set | `第1章_企业战略与业务目标.md` |
| See business architecture / process | `第2章_业务架构.md` |
| See data architecture / models | `第3章_数据架构.md` |
| See apps / API / mid-platform | `第4章_应用架构.md` |
| See tech mid-platform / deployment | `第5章_技术架构.md` |
| See the implementation roadmap | `第6章_实施规划.md` |
| **Have AI build the whole system** | `架构可视化浏览系统_需求与设计方案.md` |
| Grab ready-made charts | `html/` |
| Grab the LTC knowledge-graph prototype | `ea-ltc-demo/` |
| Grab raw structured data | `附件/` |
