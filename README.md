# Lab: Import a POS MCP Server into watsonx Orchestrate

**Duration:** ~15 minutes  
**Level:** Introductory  

---

## Overview

In this lab you will import a ready-made **Point of Sale (POS) MCP server** into watsonx Orchestrate. The server lives in a GitHub IBM repository and is pulled on demand using `uvx` — no manual cloning or `pip install` required.

The server uses **stdio transport**: the ADK spawns it as a local subprocess by running the `uvx` command. No network port or tunnel is needed.

### POS tools provided

| Tool | What the agent can do |
|---|---|
| `pos_list_products` | List all products, optionally filtered by category |
| `pos_get_product` | Get price and stock details for one product by ID |
| `pos_sales_report` | Revenue summary filtered by date range and/or cashier |
| `pos_inventory_alerts` | Flag products at or below a configurable stock threshold |
| `pos_terminal_status` | Show all POS terminals and their online/offline status |

---

## Part 1 — Get your PAT token (2 min)

You will be given a **Personal Access Token** from GitHub IBM to let `uvx` pull the private repo.

Keep the token in your clipboard or a notepad for the next step.

---

## Part 2 — Register the server in watsonx Orchestrate (5 min)

### Use the GUI

1. Open your watsonx Orchestrate instance in a browser.
2. Click **☰ menu → Build → Tools → Create Tool + → MCP Server → Add MCP Server + -> Local MCP Server → Next**.
3. Fill in the form:

   | Field | Value |
   |---|---|
   | **Server name** | `pos-mcp` |
   | **Description** | `pos-mcp` |
   | **Install Command** | `uvx --from git+https://[PAT TOKEN]@github.ibm.com/wxo-bootcamp-labs/simple_mcp_lab.git pos-mcp-server` |
   | **Select Connection (optional)** | Leave blank |

4. Click **Import** — all 5 tools should appear after a little wait.

To see the imported tools in the cli

```bash
orchestrate tookits list
```

---

## Part 4 — Assign tools to an agent (2 min)

1. **Navigation menu (☰ top-left) → Build → Create Agent + → Create from Scratch** 
2. Name: Simple POS Query Agent
3. Description: Answers basic questions and products, sales performance, inventory levels, and terminal status at a coffee shop
4. Create
5. Toolset (on the left) → Add tool + → Local Instance
6. Select the 5 tools you just imported, they start: `simple_mcp_server:`
7. Add to Agnet
8. Behavior (on the left) → Paste the following into `Instructions`
   > *You are a retail assistant for a coffee shop chain. Use the POS tools to answer
   > questions about products, sales performance, inventory levels, and terminal status.*

---

## Part 5 — Test the agent (4 min)

In the  **Chat** try each prompt below. Each one targets a different tool.

| Prompt | Tool called |
|---|---|
| *"List all products in the Beverages category"* | `pos_list_products` |
| *"What is the price and stock level of product P003?"* | `pos_get_product` |
| *"Show me Anna's sales on 1 June 2025"* | `pos_sales_report` |
| *"Which items have fewer than 25 units in stock?"* | `pos_inventory_alerts` |
| *"Are all POS terminals currently online?"* | `pos_terminal_status` |

---

## Quick reference — fake data

### Products

| ID | Name | Category | Price | Stock |
|---|---|---|---|---|
| P001 | Espresso Blend Coffee | Beverages | $12.99 | 142 |
| P002 | Oat Milk (1L) | Dairy Alt | $2.49 | 38 |
| P003 | Croissant | Bakery | $3.50 | 24 |
| P004 | Green Tea Matcha | Beverages | $9.99 | 76 |
| P005 | Sparkling Water (500ml) | Beverages | $1.20 | 200 |
| P006 | Blueberry Muffin | Bakery | $3.99 | **18 ⚠** |
| P007 | Whole Milk (1L) | Dairy | $1.89 | 55 |
| P008 | Dark Chocolate Bar | Snacks | $4.50 | 90 |
| P009 | Granola Bar | Snacks | $2.20 | **11 ⚠** |
| P010 | Orange Juice (1L) | Beverages | $3.75 | **0 🚫** |

### Cashiers & Terminals

| Terminal | Location | Cashier | Status |
|---|---|---|---|
| T1 | Front Counter | Anna | online |
| T2 | Drive-Through | Ben | online |
| T3 | Self-Service | Clara | **offline** |

---