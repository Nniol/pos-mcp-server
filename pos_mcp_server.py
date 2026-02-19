#!/usr/bin/env python3
"""
Point of Sale (POS) MCP Server — Lab Demo

A self-contained MCP server backed by in-memory fake data.
Communicates over stdio — watsonx Orchestrate ADK spawns this process directly
via uvx, pulling the package straight from the GitHub repo.

Invocation (used in mcp_servers.json):
  uvx --from git+https://<PAT>@github.ibm.com/<org>/<repo>.git pos-mcp-server

watsonx Orchestrate config (~/.orchestrate/mcp_servers.json):
  {
    "pos_mcp": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://<PAT>@github.ibm.com/<org>/<repo>.git",
        "pos-mcp-server"
      ]
    }
  }
"""

import json
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Server init
# ---------------------------------------------------------------------------
mcp = FastMCP("pos_mcp")

# ---------------------------------------------------------------------------
# Fake in-memory data store
# ---------------------------------------------------------------------------
PRODUCTS: dict[str, dict] = {
    "P001": {
        "id": "P001",
        "name": "Espresso Blend Coffee",
        "category": "Beverages",
        "price": 12.99,
        "stock": 142,
    },
    "P002": {
        "id": "P002",
        "name": "Oat Milk (1L)",
        "category": "Dairy Alt",
        "price": 2.49,
        "stock": 38,
    },
    "P003": {
        "id": "P003",
        "name": "Croissant",
        "category": "Bakery",
        "price": 3.50,
        "stock": 24,
    },
    "P004": {
        "id": "P004",
        "name": "Green Tea Matcha",
        "category": "Beverages",
        "price": 9.99,
        "stock": 76,
    },
    "P005": {
        "id": "P005",
        "name": "Sparkling Water (500ml)",
        "category": "Beverages",
        "price": 1.20,
        "stock": 200,
    },
    "P006": {
        "id": "P006",
        "name": "Blueberry Muffin",
        "category": "Bakery",
        "price": 3.99,
        "stock": 18,
    },
    "P007": {
        "id": "P007",
        "name": "Whole Milk (1L)",
        "category": "Dairy",
        "price": 1.89,
        "stock": 55,
    },
    "P008": {
        "id": "P008",
        "name": "Dark Chocolate Bar",
        "category": "Snacks",
        "price": 4.50,
        "stock": 90,
    },
    "P009": {
        "id": "P009",
        "name": "Granola Bar",
        "category": "Snacks",
        "price": 2.20,
        "stock": 11,
    },
    "P010": {
        "id": "P010",
        "name": "Orange Juice (1L)",
        "category": "Beverages",
        "price": 3.75,
        "stock": 0,
    },
}

TRANSACTIONS: list[dict] = [
    {
        "tx_id": "TX1001",
        "date": "2025-06-01",
        "product_id": "P001",
        "qty": 3,
        "total": 38.97,
        "terminal": "T1",
        "cashier": "Anna",
    },
    {
        "tx_id": "TX1002",
        "date": "2025-06-01",
        "product_id": "P003",
        "qty": 5,
        "total": 17.50,
        "terminal": "T2",
        "cashier": "Ben",
    },
    {
        "tx_id": "TX1003",
        "date": "2025-06-02",
        "product_id": "P004",
        "qty": 2,
        "total": 19.98,
        "terminal": "T1",
        "cashier": "Anna",
    },
    {
        "tx_id": "TX1004",
        "date": "2025-06-02",
        "product_id": "P008",
        "qty": 4,
        "total": 18.00,
        "terminal": "T3",
        "cashier": "Clara",
    },
    {
        "tx_id": "TX1005",
        "date": "2025-06-03",
        "product_id": "P001",
        "qty": 6,
        "total": 77.94,
        "terminal": "T2",
        "cashier": "Ben",
    },
    {
        "tx_id": "TX1006",
        "date": "2025-06-03",
        "product_id": "P006",
        "qty": 3,
        "total": 11.97,
        "terminal": "T1",
        "cashier": "Anna",
    },
    {
        "tx_id": "TX1007",
        "date": "2025-06-04",
        "product_id": "P002",
        "qty": 8,
        "total": 19.92,
        "terminal": "T3",
        "cashier": "Clara",
    },
    {
        "tx_id": "TX1008",
        "date": "2025-06-04",
        "product_id": "P005",
        "qty": 10,
        "total": 12.00,
        "terminal": "T2",
        "cashier": "Ben",
    },
    {
        "tx_id": "TX1009",
        "date": "2025-06-05",
        "product_id": "P009",
        "qty": 2,
        "total": 4.40,
        "terminal": "T1",
        "cashier": "Anna",
    },
    {
        "tx_id": "TX1010",
        "date": "2025-06-05",
        "product_id": "P003",
        "qty": 7,
        "total": 24.50,
        "terminal": "T3",
        "cashier": "Clara",
    },
    {
        "tx_id": "TX1011",
        "date": "2025-06-05",
        "product_id": "P004",
        "qty": 1,
        "total": 9.99,
        "terminal": "T2",
        "cashier": "Ben",
    },
    {
        "tx_id": "TX1012",
        "date": "2025-06-06",
        "product_id": "P001",
        "qty": 4,
        "total": 51.96,
        "terminal": "T1",
        "cashier": "Anna",
    },
]

TERMINALS: dict[str, dict] = {
    "T1": {
        "id": "T1",
        "location": "Front Counter",
        "cashier": "Anna",
        "status": "online",
    },
    "T2": {
        "id": "T2",
        "location": "Drive-Through",
        "cashier": "Ben",
        "status": "online",
    },
    "T3": {
        "id": "T3",
        "location": "Self-Service",
        "cashier": "Clara",
        "status": "offline",
    },
}


# ---------------------------------------------------------------------------
# Helper utilities
# ---------------------------------------------------------------------------
def _fmt_currency(amount: float) -> str:
    return f"${amount:,.2f}"


def _product_or_error(product_id: str) -> tuple[dict | None, str | None]:
    p = PRODUCTS.get(product_id.upper())
    if not p:
        ids = ", ".join(PRODUCTS.keys())
        return None, f"Product '{product_id}' not found. Valid IDs: {ids}"
    return p, None


# ---------------------------------------------------------------------------
# Input Models
# ---------------------------------------------------------------------------
class ProductLookupInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    product_id: str = Field(
        ...,
        description="Product ID (e.g. 'P001'). Use pos_list_products to find valid IDs.",
        min_length=1,
        max_length=10,
    )


class CategoryFilterInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    category: Optional[str] = Field(
        default=None,
        description="Filter by category name, e.g. 'Beverages', 'Bakery', 'Snacks'. Omit to return all categories.",
    )


class SalesReportInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    date_from: Optional[str] = Field(
        default=None,
        description="Start date filter in YYYY-MM-DD format, e.g. '2025-06-01'. Omit to include all dates.",
    )
    date_to: Optional[str] = Field(
        default=None,
        description="End date filter in YYYY-MM-DD format, e.g. '2025-06-05'. Omit to include all dates.",
    )
    cashier: Optional[str] = Field(
        default=None,
        description="Filter by cashier name, e.g. 'Anna'. Omit to include all cashiers.",
    )


class InventoryAlertInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    threshold: int = Field(
        default=20,
        description="Stock quantity threshold. Products at or below this level are flagged. Default is 20.",
        ge=0,
        le=500,
    )


# ---------------------------------------------------------------------------
# Tool 1 — List Products
# ---------------------------------------------------------------------------
@mcp.tool(
    name="pos_list_products",
    annotations={
        "title": "List POS Products",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def pos_list_products(params: CategoryFilterInput) -> str:
    """List all products in the Point of Sale system, optionally filtered by category.

    Returns product ID, name, category, unit price, and current stock level.
    Use this tool first to discover valid product IDs before calling pos_get_product.

    Args:
        params (CategoryFilterInput):
            - category (Optional[str]): Category name to filter on. Omit for all products.

    Returns:
        str: JSON array of product objects, each with keys:
             id, name, category, price, stock

    Examples:
        - "Show me all beverages" → params with category="Beverages"
        - "List every product"   → params with no category
    """
    products = list(PRODUCTS.values())
    if params.category:
        products = [
            p for p in products if p["category"].lower() == params.category.lower()
        ]
        if not products:
            cats = sorted({p["category"] for p in PRODUCTS.values()})
            return json.dumps(
                {
                    "error": f"No products in category '{params.category}'.",
                    "available_categories": cats,
                }
            )

    return json.dumps(products, indent=2)


# ---------------------------------------------------------------------------
# Tool 2 — Get single product
# ---------------------------------------------------------------------------
@mcp.tool(
    name="pos_get_product",
    annotations={
        "title": "Get POS Product Details",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def pos_get_product(params: ProductLookupInput) -> str:
    """Retrieve full details for a single product by its ID.

    Args:
        params (ProductLookupInput):
            - product_id (str): Product ID such as 'P001'.

    Returns:
        str: JSON object with keys: id, name, category, price, stock
             or an error message if the ID is not found.

    Examples:
        - "What's the price of P003?"      → params with product_id="P003"
        - "How much stock does P010 have?" → params with product_id="P010"
    """
    product, err = _product_or_error(params.product_id)
    if err:
        return json.dumps({"error": err})
    return json.dumps(product, indent=2)


# ---------------------------------------------------------------------------
# Tool 3 — Sales report
# ---------------------------------------------------------------------------
@mcp.tool(
    name="pos_sales_report",
    annotations={
        "title": "POS Sales Report",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def pos_sales_report(params: SalesReportInput) -> str:
    """Generate a sales summary report from POS transactions.

    Filters transactions by date range and/or cashier, then summarises
    total revenue, number of transactions, and a per-product breakdown.

    Args:
        params (SalesReportInput):
            - date_from (Optional[str]): Start date, YYYY-MM-DD.
            - date_to   (Optional[str]): End date, YYYY-MM-DD.
            - cashier   (Optional[str]): Cashier name to scope the report.

    Returns:
        str: JSON object with keys:
             filters_applied, transaction_count, total_revenue, by_product[]

    Examples:
        - "Revenue this week?"         → no filters
        - "Anna's sales on 2025-06-01" → date_from="2025-06-01", date_to="2025-06-01", cashier="Anna"
        - "Total for June 3–5"         → date_from="2025-06-03", date_to="2025-06-05"
    """
    txs = list(TRANSACTIONS)

    if params.date_from:
        txs = [t for t in txs if t["date"] >= params.date_from]
    if params.date_to:
        txs = [t for t in txs if t["date"] <= params.date_to]
    if params.cashier:
        txs = [t for t in txs if t["cashier"].lower() == params.cashier.lower()]

    if not txs:
        return json.dumps({"error": "No transactions match the given filters."})

    total_revenue = sum(t["total"] for t in txs)

    # Per-product aggregation
    by_product: dict[str, dict] = {}
    for t in txs:
        pid = t["product_id"]
        if pid not in by_product:
            name = PRODUCTS[pid]["name"] if pid in PRODUCTS else pid
            by_product[pid] = {
                "product_id": pid,
                "name": name,
                "qty_sold": 0,
                "revenue": 0.0,
            }
        by_product[pid]["qty_sold"] += t["qty"]
        by_product[pid]["revenue"] += t["total"]

    product_list = sorted(by_product.values(), key=lambda x: x["revenue"], reverse=True)

    report = {
        "filters_applied": {
            "date_from": params.date_from,
            "date_to": params.date_to,
            "cashier": params.cashier,
        },
        "transaction_count": len(txs),
        "total_revenue": round(total_revenue, 2),
        "by_product": product_list,
    }
    return json.dumps(report, indent=2)


# ---------------------------------------------------------------------------
# Tool 4 — Inventory alert
# ---------------------------------------------------------------------------
@mcp.tool(
    name="pos_inventory_alerts",
    annotations={
        "title": "POS Inventory Alerts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def pos_inventory_alerts(params: InventoryAlertInput) -> str:
    """Return a list of products that are at or below the specified stock threshold.

    Use this tool to identify items that need restocking before the next shift.

    Args:
        params (InventoryAlertInput):
            - threshold (int): Stock quantity at-or-below which a product is flagged.
                               Default 20. Range 0–500.

    Returns:
        str: JSON object with keys:
             threshold, alert_count, alerts[]
             Each alert has: id, name, category, stock, status ("out_of_stock" or "low_stock")

    Examples:
        - "What's running low?"        → threshold=20 (default)
        - "Anything completely out?"   → threshold=0
        - "Flag anything under 50"     → threshold=50
    """
    alerts = []
    for p in PRODUCTS.values():
        if p["stock"] <= params.threshold:
            alerts.append(
                {
                    "id": p["id"],
                    "name": p["name"],
                    "category": p["category"],
                    "stock": p["stock"],
                    "status": "out_of_stock" if p["stock"] == 0 else "low_stock",
                }
            )

    alerts.sort(key=lambda x: x["stock"])

    return json.dumps(
        {
            "threshold": params.threshold,
            "alert_count": len(alerts),
            "alerts": alerts,
        },
        indent=2,
    )


# ---------------------------------------------------------------------------
# Tool 5 — Terminal status
# ---------------------------------------------------------------------------
@mcp.tool(
    name="pos_terminal_status",
    annotations={
        "title": "POS Terminal Status",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False,
    },
)
async def pos_terminal_status() -> str:
    """List all POS terminals and their current online/offline status.

    Returns the terminal ID, physical location, assigned cashier, and status.
    No parameters required.

    Returns:
        str: JSON array of terminal objects with keys:
             id, location, cashier, status

    Examples:
        - "Which terminals are offline?" → use this tool, then filter by status
        - "Who is on terminal T2?"       → use this tool, look up T2
    """
    return json.dumps(list(TERMINALS.values()), indent=2)


# ---------------------------------------------------------------------------
# Entry point — stdio transport (watsonx Orchestrate ADK spawns this process)
# ---------------------------------------------------------------------------
def main() -> None:
    """Called by uvx via the [project.scripts] entry point in pyproject.toml."""
    mcp.run()  # stdio by default


if __name__ == "__main__":
    main()
