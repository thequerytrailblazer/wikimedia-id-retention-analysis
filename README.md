# Wikimedia Indonesia Data & Technology Program Analytics (2025–2026)

## Overview
This repository contains data analytics pipelines, data cleaning scripts, and post-event retention tracking models for the **Data and Technology Team of Wikimedia Indonesia**. The primary goal is to evaluate training outcomes, editor engagement, and long-term retention, with a specific focus on contributions to the **[Wikidata](https://www.wikidata.org)** project.

The dataset covers campaign activities from 2025 through 2026, capturing cohort performance across regional workshops, university training programs (*Wikilatih*), and edit-a-thons (*Geodatathon* / *Datathon*).

---

## Data Source & Attribution
All data in this repository is sourced publicly from the **Wikimedia Outreach Dashboard**:
* **Campaign Overview:** [Wikimedia Indonesia Data and Technology Campaign 2025](https://outreachdashboard.wmflabs.org/campaigns/data_dan_teknologi_wikimedia_indonesia_2025/overview)
* **Target Project:** [Wikidata](https://www.wikidata.org/wiki/Wikidata:Main_Page)

---

## Campaign Summary Statistics
Key metrics extracted from the Outreach Dashboard datasets:
* **Total Training Events:** 33 activities
* **Total Student Enrollments:** 446 enrollments (372 unique editors)
* **Total Revisions:** Over 370,000 edits
* **Total Wikidata Items Created:** Over 7,600 items

---

## Methodology & Retention Framework
1. **Data Cleaning & Standardization:** Resolving string/numeric data type mismatches, normalizing usernames, and mapping local wiki IDs against global CentralAuth identifiers.
2. **Cohort Segmentation:** Isolating **New Users** from **Existing Editors** to eliminate pre-existing activity bias when evaluating training effectiveness.
3. **Cross-Platform Conversion Tracking:** Measuring editor progression from event-specific Wikidata training to subsequent post-event edits on Wikidata and the Indonesian Wikipedia ([id.wikipedia.org](https://id.wikipedia.org)).

---

## License
All data and content in this repository are licensed under the **[Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)](https://creativecommons.org/licenses/by-sa/4.0/)** license.

Under this license, you are free to:
* **Share:** Copy and redistribute the material in any medium or format.
* **Adapt:** Remix, transform, and build upon the material for any purpose, even commercially.

**Under the following terms:**
* **Attribution:** You must give appropriate credit to Wikimedia Indonesia and the Wikimedia Outreach Dashboard.
* **ShareAlike:** If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.