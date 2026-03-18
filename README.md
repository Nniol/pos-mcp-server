# Lab: Import a POS MCP Server into watsonx Orchestrate

**Duration:** ~15 minutes  
**Level:** Introductory  

---

## Overview

In this lab you will import a ready-made **Point of Sale (POS) MCP server** into watsonx Orchestrate. The server is published as a public package on PyPI and is pulled on demand using `uvx` — no manual cloning, `pip install`, or access token required.

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

## Part 1 — Register the server in watsonx Orchestrate (5 min)

### Use the GUI

1. Open your watsonx Orchestrate instance in a browser.
2. Click **☰ menu → Build → Tools → Create Tool + → MCP Server → Add MCP Server + -> Local MCP Server → Next**.
3. Fill in the form:

   | Field | Value |
   |---|---|
   | **Server name** | `pos-mcp` |
   | **Description** | `pos-mcp` |
   | **Install Command** | `uvx --from pos-mcp-server pos-mcp-server` |
   | **Select Connection (optional)** | Leave blank |

4. Click **Import** — all 5 tools should appear after a little wait.

To see the imported tools in the cli

```bash
orchestrate tookits list
```

---

## Part 2 — Assign tools to an agent (2 min)

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

## Part 3 — Test the agent (4 min)

In the  **Chat** try each prompt below. Each one targets a different tool.

| Prompt | Tool called |
|---|---|
| *"List all products in the Beverages category"* | `pos_list_products` |
| *"What is the price and stock level of product P003?"* | `pos_get_product` |
| *"Show me Anna's sales on 1 June 2025"* | `pos_sales_report` |
| *"Which items have fewer than 25 units in stock?"* | `pos_inventory_alerts` |
| *"Are all POS terminals currently online?"* | `pos_terminal_status` |

---

## Part 4 — Build a ReAct-style agent (5 min)

### What is ReAct?

**ReAct** (Reason + Act) is a prompting pattern where the agent explicitly alternates between:

- **Thought** — reasoning about what is known and what is still needed
- **Action** — calling a tool
- **Observation** — reading the tool result
- ...repeating until enough information is gathered...
- **Final Answer** — a synthesised response to the user

This is better than the default style for multi-tool questions because the agent decides its *next* tool based on what the *previous* tool returned, rather than planning all calls upfront or stopping after one.

```
User question
    │
    ▼
Thought: what do I know? what do I need?
    │
    ▼
Action: call tool A
    │
    ▼
Observation: result from tool A
    │
    ▼
Thought: what does this tell me? do I need more data?
    │
    ▼
Action: call tool B  ◄─── decision driven by Observation above
    │
    ▼
Observation: result from tool B
    │
    ▼
Thought: I have enough to answer.
    │
    ▼
Final Answer: synthesised response
```

---

### Create the agent

1. **Navigation menu (☰ top-left) → Build → Create Agent + → Create from Scratch**
2. Name: `POS ReAct Agent`
3. Description: `Uses step-by-step reasoning to answer complex operational questions by chaining multiple POS tools`
4. Create
5. **Toolset (on the left) → Add tool + → Local Instance**
6. Select all 5 tools (`pos_list_products`, `pos_get_product`, `pos_sales_report`, `pos_inventory_alerts`, `pos_terminal_status`)
7. Add to Agent
8. **Behavior (on the left) → Paste the following into `Instructions`**

```
You are an operations assistant for a coffee shop chain. You reason step by step
before acting, following the ReAct pattern strictly.

Available tools:
  - pos_list_products    — browse the product catalogue, optionally by category
  - pos_get_product      — get price and stock for a specific product ID
  - pos_sales_report     — revenue and transaction data, filterable by date and cashier
  - pos_inventory_alerts — products at or below a stock threshold (default: 20 units)
  - pos_terminal_status  — current online/offline status of all POS terminals

For every user question, work through this loop until you have enough information:

  Thought: <reason about what you know and what you still need>
  Action: <name of tool to call>
  Action Input: <parameters to pass>
  Observation: <result returned by the tool>

Repeat Thought / Action / Observation as many times as needed.
When you have enough information, write:

  Thought: I now have enough information to answer.
  Final Answer: <clear, concise response to the user>

Rules:
- Never skip the Thought step — always reason before acting.
- Only call a tool when the Thought step identifies a genuine need for it.
- Base each Action on the Observations you have already collected, not assumptions.
- If a single tool is sufficient, use only that tool — do not make unnecessary calls.
```

---

### Test the ReAct agent (multi-tool prompts)

These prompts require the agent to chain tools based on intermediate results.

| Prompt | Expected ReAct chain |
|---|---|
| *"Give me a full store health check"* | `pos_terminal_status` → observe offline terminals → `pos_inventory_alerts` → combine both into summary |
| *"Which low-stock items have been selling the most?"* | `pos_inventory_alerts` → extract product IDs → `pos_sales_report` → correlate stock vs revenue |
| *"What did Anna sell on June 1st and are any of those items running low?"* | `pos_sales_report` (Anna, June 1) → extract product IDs → `pos_get_product` for each → flag low stock |
| *"List all Bakery products and show their recent sales"* | `pos_list_products` (Bakery) → `pos_sales_report` → match products to revenue |

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