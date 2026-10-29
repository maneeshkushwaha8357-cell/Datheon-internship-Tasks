"""Stock portfolio valuation and CSV reporting utility.

Sample prices are illustrative only. Use --live to request current prices
through yfinance (optional dependency), or provide a trusted price CSV.
"""

import argparse
import csv
from datetime import datetime, timezone
from pathlib import Path

DEFAULT_PRICE_FILE = Path(__file__).with_name("sample_stock_prices.csv")
DEFAULT_OUTPUT_FILE = Path("portfolio_summary.csv")


def load_prices(csv_path: Path) -> dict[str, float]:
    """Load ticker-to-price mappings from a CSV with symbol and current_price columns."""
    prices: dict[str, float] = {}
    with csv_path.open("r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        required = {"symbol", "current_price"}
        if not reader.fieldnames or not required.issubset(set(reader.fieldnames)):
            raise ValueError("Price CSV must contain 'symbol' and 'current_price' columns.")
        for row in reader:
            symbol = (row.get("symbol") or "").strip().upper()
            raw_price = (row.get("current_price") or "").strip()
            if not symbol or not raw_price:
                continue
            try:
                price = float(raw_price)
            except ValueError:
                continue
            if price > 0:
                prices[symbol] = price
    return prices


def fetch_live_price(symbol: str) -> float:
    """Fetch the latest available price using optional yfinance package."""
    try:
        import yfinance as yf
    except ImportError as exc:
        raise RuntimeError(
            "Live quotes require yfinance. Install it with: pip install yfinance"
        ) from exc

    history = yf.Ticker(symbol).history(period="5d", auto_adjust=False)
    if history.empty or "Close" not in history:
        raise ValueError(f"No recent market price was returned for {symbol}.")
    close_values = history["Close"].dropna()
    if close_values.empty:
        raise ValueError(f"No valid closing price was returned for {symbol}.")
    price = float(close_values.iloc[-1])
    if price <= 0:
        raise ValueError(f"Invalid market price returned for {symbol}.")
    return price


def read_positions() -> list[dict[str, float | str]]:
    """Collect positions from the terminal until the user enters a blank ticker."""
    positions: list[dict[str, float | str]] = []
    print("Enter each holding. Leave the ticker blank when finished.")
    while True:
        symbol = input("Ticker symbol: ").strip().upper()
        if not symbol:
            break
        if not symbol.replace(".", "").replace("-", "").isalnum():
            print("Ticker should contain letters, digits, dots, or hyphens.")
            continue

        try:
            buy_price = float(input("Purchase price per share: ").strip())
            shares = float(input("Number of shares: ").strip())
        except ValueError:
            print("Please enter valid numeric values.")
            continue

        if buy_price <= 0 or shares <= 0:
            print("Purchase price and share quantity must both be greater than zero.")
            continue

        positions.append({
            "symbol": symbol,
            "buy_price": buy_price,
            "shares": shares,
        })
    return positions


def value_positions(
    positions: list[dict[str, float | str]],
    prices: dict[str, float],
    live: bool = False,
) -> list[dict[str, float | str]]:
    """Calculate cost basis, market value, profit/loss and percentage per position."""
    results: list[dict[str, float | str]] = []
    for position in positions:
        symbol = str(position["symbol"]).upper()
        buy_price = float(position["buy_price"])
        shares = float(position["shares"])

        if live:
            current_price = fetch_live_price(symbol)
        else:
            if symbol not in prices:
                raise ValueError(
                    f"No sample/current price found for {symbol}. Add it to the price CSV "
                    "or rerun with --live."
                )
            current_price = prices[symbol]

        cost_basis = buy_price * shares
        market_value = current_price * shares
        profit_loss = market_value - cost_basis
        profit_loss_pct = (profit_loss / cost_basis) * 100

        results.append({
            "symbol": symbol,
            "buy_price": round(buy_price, 4),
            "current_price": round(current_price, 4),
            "shares": round(shares, 4),
            "cost_basis": round(cost_basis, 2),
            "market_value": round(market_value, 2),
            "profit_loss": round(profit_loss, 2),
            "profit_loss_pct": round(profit_loss_pct, 2),
        })
    return results


def write_summary(
    results: list[dict[str, float | str]],
    output_path: Path,
    price_source: str,
) -> None:
    """Write position-level calculations and a portfolio total row to CSV."""
    columns = [
        "symbol", "buy_price", "current_price", "shares", "cost_basis",
        "market_value", "profit_loss", "profit_loss_pct",
    ]
    total_cost = sum(float(row["cost_basis"]) for row in results)
    total_value = sum(float(row["market_value"]) for row in results)
    total_pl = total_value - total_cost
    total_pct = (total_pl / total_cost * 100) if total_cost else 0.0

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=columns)
        writer.writeheader()
        writer.writerows(results)
        writer.writerow({
            "symbol": "PORTFOLIO_TOTAL",
            "buy_price": "",
            "current_price": "",
            "shares": "",
            "cost_basis": round(total_cost, 2),
            "market_value": round(total_value, 2),
            "profit_loss": round(total_pl, 2),
            "profit_loss_pct": round(total_pct, 2),
        })

    print("\nPORTFOLIO SUMMARY")
    print("-" * 76)
    print(f"{'Ticker':<12}{'Shares':>10}{'Cost basis':>15}{'Market value':>17}{'P/L':>12}")
    for row in results:
        print(
            f"{str(row['symbol']):<12}{float(row['shares']):>10.2f}"
            f"{float(row['cost_basis']):>15.2f}{float(row['market_value']):>17.2f}"
            f"{float(row['profit_loss']):>12.2f}"
        )
    print("-" * 76)
    print(f"{'TOTAL':<22}{total_cost:>15.2f}{total_value:>17.2f}{total_pl:>12.2f}")
    print(f"Total return: {total_pct:.2f}%")
    print(f"Price source: {price_source}")
    print(f"CSV report saved to: {output_path.resolve()}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Calculate stock portfolio performance.")
    parser.add_argument(
        "--prices", type=Path, default=DEFAULT_PRICE_FILE,
        help="CSV containing symbol,current_price (default: bundled sample prices)",
    )
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT_FILE,
        help="Path for the generated portfolio summary CSV",
    )
    parser.add_argument(
        "--live", action="store_true",
        help="Fetch recent market prices using optional yfinance (network required)",
    )
    args = parser.parse_args()

    print("Stock Portfolio Performance Tracker")
    print("Note: this tool reports calculations; it is not investment advice.")
    positions = read_positions()
    if not positions:
        print("No positions entered; nothing to calculate.")
        return 0

    try:
        prices = {} if args.live else load_prices(args.prices)
        results = value_positions(positions, prices, live=args.live)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Unable to calculate portfolio: {error}")
        return 1

    source = "yfinance recent market data" if args.live else f"CSV prices: {args.prices}"
    write_summary(results, args.output, source)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
