#!/usr/bin/env python3
"""
Advanced cryptocurrency portfolio analyzer with comprehensive market data integration.
Features: Real-time prices, historical data, tax calculations, risk analysis, and more.
"""

import json
import requests
import sqlite3
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
import statistics
import hashlib
import time

class CryptoDataFetcher:
    """Advanced cryptocurrency data fetcher with multiple API sources and caching."""

    def __init__(self):
        self.currency_mapping = {
            'BTC': 'bitcoin',
            'ETH': 'ethereum',
            'USDT': 'tether',
            'USDC': 'usd-coin',
            'XRP': 'ripple',
            'ADA': 'cardano',
            'SOL': 'solana',
            'DOT': 'polkadot',
            'MATIC': 'matic-network',
            'LTC': 'litecoin',
            'TRX': 'tron'
        }
        self.setup_cache_db()

    def setup_cache_db(self):
        """Setup SQLite database for caching price data."""
        self.conn = sqlite3.connect('crypto_cache.db')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS price_cache (
                currency TEXT,
                timestamp INTEGER,
                price REAL,
                market_cap REAL,
                volume_24h REAL,
                price_change_24h REAL,
                price_change_7d REAL,
                PRIMARY KEY (currency, timestamp)
            )
        ''')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS historical_prices (
                currency TEXT,
                date TEXT,
                price REAL,
                PRIMARY KEY (currency, date)
            )
        ''')
        self.conn.commit()

    def fetch_current_prices(self) -> Dict[str, Dict[str, float]]:
        """Fetch comprehensive current market data."""
        try:
            coin_ids = ','.join(self.currency_mapping.values())
            url = f"https://api.coingecko.com/api/v3/simple/price?ids={coin_ids}&vs_currencies=usd&include_market_cap=true&include_24hr_vol=true&include_24hr_change=true&include_7d_change=true"

            response = requests.get(url, timeout=15)
            response.raise_for_status()
            price_data = response.json()

            enhanced_prices = {}
            current_timestamp = int(time.time())

            for currency_code, coin_id in self.currency_mapping.items():
                if coin_id in price_data:
                    data = price_data[coin_id]
                    enhanced_prices[currency_code] = {
                        'price': data.get('usd', 0),
                        'market_cap': data.get('usd_market_cap', 0),
                        'volume_24h': data.get('usd_24h_vol', 0),
                        'price_change_24h': data.get('usd_24h_change', 0),
                        'price_change_7d': data.get('usd_7d_change', 0),
                        'last_updated': current_timestamp
                    }

                    # Cache the data
                    self.conn.execute('''
                        INSERT OR REPLACE INTO price_cache
                        (currency, timestamp, price, market_cap, volume_24h, price_change_24h, price_change_7d)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                    ''', (currency_code, current_timestamp, enhanced_prices[currency_code]['price'],
                          enhanced_prices[currency_code]['market_cap'], enhanced_prices[currency_code]['volume_24h'],
                          enhanced_prices[currency_code]['price_change_24h'], enhanced_prices[currency_code]['price_change_7d']))

            self.conn.commit()
            return enhanced_prices

        except Exception as e:
            print(f"Error fetching current prices: {e}")
            return self.get_fallback_prices()

    def get_fallback_prices(self) -> Dict[str, Dict[str, float]]:
        """Return fallback prices with estimated market data."""
        fallback_data = {
            'BTC': {'price': 45000, 'market_cap': 880000000000, 'volume_24h': 15000000000},
            'ETH': {'price': 2500, 'market_cap': 300000000000, 'volume_24h': 8000000000},
            'USDT': {'price': 1.0, 'market_cap': 95000000000, 'volume_24h': 25000000000},
            'USDC': {'price': 1.0, 'market_cap': 25000000000, 'volume_24h': 3000000000},
            'XRP': {'price': 0.6, 'market_cap': 32000000000, 'volume_24h': 1200000000},
            'ADA': {'price': 0.4, 'market_cap': 14000000000, 'volume_24h': 400000000},
            'SOL': {'price': 100, 'market_cap': 45000000000, 'volume_24h': 1800000000},
            'DOT': {'price': 7, 'market_cap': 9000000000, 'volume_24h': 200000000},
            'MATIC': {'price': 0.8, 'market_cap': 8000000000, 'volume_24h': 300000000},
            'LTC': {'price': 70, 'market_cap': 5200000000, 'volume_24h': 400000000},
            'TRX': {'price': 0.1, 'market_cap': 9000000000, 'volume_24h': 800000000}
        }

        for currency in fallback_data:
            fallback_data[currency].update({
                'price_change_24h': 0,
                'price_change_7d': 0,
                'last_updated': int(time.time())
            })

        return fallback_data

    def fetch_historical_prices(self, currency: str, days: int = 365) -> List[Tuple[str, float]]:
        """Fetch historical price data for trend analysis."""
        try:
            coin_id = self.currency_mapping.get(currency)
            if not coin_id:
                return []

            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart?vs_currency=usd&days={days}&interval=daily"
            response = requests.get(url, timeout=15)
            response.raise_for_status()

            data = response.json()
            prices = data.get('prices', [])

            historical_data = []
            for timestamp, price in prices:
                date = datetime.fromtimestamp(timestamp / 1000).strftime('%Y-%m-%d')
                historical_data.append((date, price))

                # Cache historical data
                self.conn.execute('''
                    INSERT OR REPLACE INTO historical_prices (currency, date, price)
                    VALUES (?, ?, ?)
                ''', (currency, date, price))

            self.conn.commit()
            return historical_data

        except Exception as e:
            print(f"Error fetching historical data for {currency}: {e}")
            return []

class AdvancedPortfolioAnalyzer:
    """Comprehensive portfolio analysis with advanced metrics and insights."""

    def __init__(self, tips_data: Dict[str, Any], market_data: Dict[str, Dict[str, float]]):
        self.tips_data = tips_data
        self.market_data = market_data
        self.tips = tips_data['data']['myTips']['results']

    def calculate_comprehensive_portfolio(self) -> Dict[str, Any]:
        """Calculate comprehensive portfolio metrics with advanced analytics."""

        # Basic portfolio calculations
        sent_totals = {}
        received_totals = {}
        transaction_counts = {}
        monthly_activity = {}
        counterparty_analysis = {}

        for tip in self.tips:
            currency = tip.get('currency_code', 'UNKNOWN')
            amount = tip.get('amount', 0)
            tip_type = tip.get('type', '')
            date = tip.get('issued_at', '')
            sender = tip.get('sender_username', '')
            receiver = tip.get('receiver_username', '')

            # Initialize tracking
            if currency not in sent_totals:
                sent_totals[currency] = 0
                received_totals[currency] = 0
                transaction_counts[currency] = {'sent': 0, 'received': 0}

            # Monthly activity tracking
            if date:
                month_key = date[:7]  # YYYY-MM
                if month_key not in monthly_activity:
                    monthly_activity[month_key] = {'sent': 0, 'received': 0, 'volume': 0}

            # Process transactions
            if tip_type == 'Tip Withdraw' and amount < 0:
                sent_totals[currency] += abs(amount)
                transaction_counts[currency]['sent'] += 1
                if date:
                    monthly_activity[month_key]['sent'] += abs(amount)
                    monthly_activity[month_key]['volume'] += abs(amount)

                # Counterparty analysis
                if receiver and receiver != 'SupItsJ':
                    if receiver not in counterparty_analysis:
                        counterparty_analysis[receiver] = {'sent': 0, 'received': 0, 'transactions': 0}
                    counterparty_analysis[receiver]['sent'] += abs(amount)
                    counterparty_analysis[receiver]['transactions'] += 1

            elif tip_type == 'Tip Deposit' and amount > 0:
                received_totals[currency] += amount
                transaction_counts[currency]['received'] += 1
                if date:
                    monthly_activity[month_key]['received'] += amount
                    monthly_activity[month_key]['volume'] += amount

                # Counterparty analysis
                if sender and sender != 'SupItsJ':
                    if sender not in counterparty_analysis:
                        counterparty_analysis[sender] = {'sent': 0, 'received': 0, 'transactions': 0}
                    counterparty_analysis[sender]['received'] += amount
                    counterparty_analysis[sender]['transactions'] += 1

        # Calculate USD values and advanced metrics
        portfolio_metrics = self._calculate_advanced_metrics(
            sent_totals, received_totals, transaction_counts,
            monthly_activity, counterparty_analysis
        )

        return portfolio_metrics

    def _calculate_advanced_metrics(self, sent_totals, received_totals, transaction_counts,
                                  monthly_activity, counterparty_analysis) -> Dict[str, Any]:
        """Calculate advanced portfolio metrics and insights."""

        # USD calculations
        sent_usd_total = 0
        received_usd_total = 0
        portfolio_breakdown = {}
        risk_metrics = {}

        all_currencies = set(list(sent_totals.keys()) + list(received_totals.keys()))

        for currency in all_currencies:
            market_info = self.market_data.get(currency, {})
            current_price = market_info.get('price', 0)

            sent_amount = sent_totals.get(currency, 0)
            received_amount = received_totals.get(currency, 0)
            net_amount = received_amount - sent_amount

            sent_usd = sent_amount * current_price
            received_usd = received_amount * current_price
            net_usd = net_amount * current_price

            sent_usd_total += sent_usd
            received_usd_total += received_usd

            # Portfolio breakdown per currency
            portfolio_breakdown[currency] = {
                'amounts': {
                    'sent': sent_amount,
                    'received': received_amount,
                    'net': net_amount
                },
                'usd_values': {
                    'sent': sent_usd,
                    'received': received_usd,
                    'net': net_usd
                },
                'market_data': market_info,
                'transaction_counts': transaction_counts.get(currency, {'sent': 0, 'received': 0}),
                'avg_transaction_size': {
                    'sent': sent_amount / max(transaction_counts.get(currency, {}).get('sent', 1), 1),
                    'received': received_amount / max(transaction_counts.get(currency, {}).get('received', 1), 1)
                }
            }

            # Risk metrics per currency
            risk_metrics[currency] = {
                'volatility_24h': abs(market_info.get('price_change_24h', 0)),
                'volatility_7d': abs(market_info.get('price_change_7d', 0)),
                'market_cap_rank': self._estimate_market_cap_rank(market_info.get('market_cap', 0)),
                'liquidity_score': self._calculate_liquidity_score(market_info),
                'concentration_risk': abs(net_usd) / max(received_usd_total, 1) if received_usd_total > 0 else 0
            }

        # Calculate portfolio-wide metrics
        net_usd_total = received_usd_total - sent_usd_total
        roi_percentage = ((net_usd_total / max(sent_usd_total, 1)) * 100) if sent_usd_total > 0 else 0

        # Advanced analytics
        diversification_score = self._calculate_diversification_score(portfolio_breakdown)
        activity_trends = self._analyze_activity_trends(monthly_activity)
        top_counterparties = self._analyze_counterparties(counterparty_analysis)
        tax_implications = self._calculate_tax_implications(portfolio_breakdown)

        return {
            'summary': {
                'total_sent_usd': sent_usd_total,
                'total_received_usd': received_usd_total,
                'net_position_usd': net_usd_total,
                'roi_percentage': roi_percentage,
                'total_transactions': len(self.tips),
                'unique_currencies': len(all_currencies),
                'last_updated': datetime.now().isoformat()
            },
            'portfolio_breakdown': portfolio_breakdown,
            'risk_analysis': {
                'overall_risk_score': self._calculate_overall_risk_score(risk_metrics),
                'currency_risks': risk_metrics,
                'diversification_score': diversification_score,
                'largest_position_risk': max([abs(p['usd_values']['net']) for p in portfolio_breakdown.values()]) / max(received_usd_total, 1) if received_usd_total > 0 else 0
            },
            'activity_analysis': {
                'monthly_trends': activity_trends,
                'top_counterparties': top_counterparties,
                'transaction_patterns': self._analyze_transaction_patterns()
            },
            'tax_analysis': tax_implications,
            'market_context': self._get_market_context()
        }

    def _estimate_market_cap_rank(self, market_cap: float) -> str:
        """Estimate market cap ranking category."""
        if market_cap > 100_000_000_000:
            return "Large Cap"
        elif market_cap > 10_000_000_000:
            return "Mid Cap"
        elif market_cap > 1_000_000_000:
            return "Small Cap"
        else:
            return "Micro Cap"

    def _calculate_liquidity_score(self, market_info: Dict[str, float]) -> float:
        """Calculate liquidity score based on volume and market cap."""
        volume = market_info.get('volume_24h', 0)
        market_cap = market_info.get('market_cap', 1)
        return min((volume / market_cap) * 100, 100) if market_cap > 0 else 0

    def _calculate_diversification_score(self, portfolio_breakdown: Dict[str, Any]) -> float:
        """Calculate portfolio diversification score (0-100)."""
        if not portfolio_breakdown:
            return 0

        total_value = sum(abs(p['usd_values']['net']) for p in portfolio_breakdown.values())
        if total_value == 0:
            return 0

        # Calculate Herfindahl-Hirschman Index for diversification
        hhi = sum((abs(p['usd_values']['net']) / total_value) ** 2 for p in portfolio_breakdown.values())
        diversification_score = (1 - hhi) * 100
        return min(diversification_score, 100)

    def _calculate_overall_risk_score(self, risk_metrics: Dict[str, Dict[str, float]]) -> float:
        """Calculate overall portfolio risk score."""
        if not risk_metrics:
            return 0

        total_risk = 0
        for currency_risk in risk_metrics.values():
            volatility_risk = (currency_risk['volatility_24h'] + currency_risk['volatility_7d']) / 2
            concentration_risk = currency_risk['concentration_risk'] * 100
            liquidity_risk = 100 - currency_risk['liquidity_score']

            currency_total_risk = (volatility_risk + concentration_risk + liquidity_risk) / 3
            total_risk += currency_total_risk

        return min(total_risk / len(risk_metrics), 100)

    def _analyze_activity_trends(self, monthly_activity: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        """Analyze monthly activity trends."""
        if not monthly_activity:
            return {}

        months = sorted(monthly_activity.keys())
        volumes = [monthly_activity[month]['volume'] for month in months]

        # Calculate trends
        avg_volume = statistics.mean(volumes) if volumes else 0
        peak_month = months[volumes.index(max(volumes))] if volumes else None

        # Growth analysis
        growth_trend = "stable"
        if len(volumes) >= 3:
            recent_avg = statistics.mean(volumes[-3:])
            earlier_avg = statistics.mean(volumes[:-3]) if len(volumes) > 3 else volumes[0]
            if recent_avg > earlier_avg * 1.2:
                growth_trend = "increasing"
            elif recent_avg < earlier_avg * 0.8:
                growth_trend = "decreasing"

        return {
            'monthly_data': monthly_activity,
            'average_monthly_volume': avg_volume,
            'peak_activity_month': peak_month,
            'growth_trend': growth_trend,
            'total_months_active': len(months)
        }

    def _analyze_counterparties(self, counterparty_analysis: Dict[str, Dict[str, float]]) -> List[Dict[str, Any]]:
        """Analyze top counterparties."""
        counterparties = []
        for username, data in counterparty_analysis.items():
            total_volume = data['sent'] + data['received']
            counterparties.append({
                'username': username,
                'total_volume': total_volume,
                'sent': data['sent'],
                'received': data['received'],
                'net_flow': data['received'] - data['sent'],
                'transactions': data['transactions']
            })

        return sorted(counterparties, key=lambda x: x['total_volume'], reverse=True)[:10]

    def _analyze_transaction_patterns(self) -> Dict[str, Any]:
        """Analyze transaction patterns and behaviors."""
        transaction_sizes = []
        hourly_distribution = {}
        daily_distribution = {}

        for tip in self.tips:
            amount = abs(tip.get('amount', 0))
            if amount > 0:
                transaction_sizes.append(amount)

            # Time analysis
            date_str = tip.get('issued_at', '')
            if date_str:
                try:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    hour = dt.hour
                    day = dt.strftime('%A')

                    hourly_distribution[hour] = hourly_distribution.get(hour, 0) + 1
                    daily_distribution[day] = daily_distribution.get(day, 0) + 1
                except:
                    pass

        return {
            'average_transaction_size': statistics.mean(transaction_sizes) if transaction_sizes else 0,
            'median_transaction_size': statistics.median(transaction_sizes) if transaction_sizes else 0,
            'largest_transaction': max(transaction_sizes) if transaction_sizes else 0,
            'smallest_transaction': min(transaction_sizes) if transaction_sizes else 0,
            'most_active_hour': max(hourly_distribution.items(), key=lambda x: x[1])[0] if hourly_distribution else None,
            'most_active_day': max(daily_distribution.items(), key=lambda x: x[1])[0] if daily_distribution else None,
            'hourly_distribution': hourly_distribution,
            'daily_distribution': daily_distribution
        }

    def _calculate_tax_implications(self, portfolio_breakdown: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential tax implications (simplified)."""
        total_gains = 0
        total_losses = 0
        taxable_events = 0

        for currency, data in portfolio_breakdown.items():
            net_usd = data['usd_values']['net']
            if net_usd > 0:
                total_gains += net_usd
            else:
                total_losses += abs(net_usd)

            # Count transactions as potential taxable events
            taxable_events += data['transaction_counts']['sent'] + data['transaction_counts']['received']

        return {
            'total_realized_gains': total_gains,
            'total_realized_losses': total_losses,
            'net_tax_position': total_gains - total_losses,
            'taxable_events_count': taxable_events,
            'note': "This is a simplified calculation. Consult a tax professional for accurate tax advice."
        }

    def _get_market_context(self) -> Dict[str, Any]:
        """Get current market context and insights."""
        total_market_cap = sum(data.get('market_cap', 0) for data in self.market_data.values())
        avg_24h_change = statistics.mean([data.get('price_change_24h', 0) for data in self.market_data.values()])

        market_sentiment = "neutral"
        if avg_24h_change > 5:
            market_sentiment = "bullish"
        elif avg_24h_change < -5:
            market_sentiment = "bearish"

        return {
            'total_tracked_market_cap': total_market_cap,
            'average_24h_change': avg_24h_change,
            'market_sentiment': market_sentiment,
            'currencies_tracked': len(self.market_data),
            'last_updated': datetime.now().isoformat()
        }

def main():
    """Main function to run comprehensive portfolio analysis."""
    # Load consolidated tips data
    try:
        with open('tips_consolidated.json', 'r', encoding='utf-8') as f:
            tips_data = json.load(f)
    except FileNotFoundError:
        print("Error: tips_consolidated.json not found. Please run consolidate_tips.py first.")
        return

    print("🚀 Starting Advanced Portfolio Analysis...")

    # Initialize data fetcher and get market data
    data_fetcher = CryptoDataFetcher()
    print("📊 Fetching current market data...")
    market_data = data_fetcher.fetch_current_prices()

    # Initialize portfolio analyzer
    analyzer = AdvancedPortfolioAnalyzer(tips_data, market_data)
    print("🔍 Calculating comprehensive portfolio metrics...")
    portfolio_analysis = analyzer.calculate_comprehensive_portfolio()

    # Save comprehensive analysis
    with open('advanced_portfolio_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(portfolio_analysis, f, indent=2, ensure_ascii=False)

    # Display summary
    summary = portfolio_analysis['summary']
    risk = portfolio_analysis['risk_analysis']

    print("\n" + "="*60)
    print("🎯 ADVANCED PORTFOLIO ANALYSIS SUMMARY")
    print("="*60)
    print(f"💸 Total Sent: ${summary['total_sent_usd']:,.2f}")
    print(f"💰 Total Received: ${summary['total_received_usd']:,.2f}")
    print(f"📊 Net Position: ${summary['net_position_usd']:,.2f}")
    print(f"📈 ROI: {summary['roi_percentage']:.2f}%")
    print(f"🔢 Total Transactions: {summary['total_transactions']}")
    print(f"🪙 Unique Currencies: {summary['unique_currencies']}")

    print(f"\n🎲 RISK ANALYSIS")
    print(f"Overall Risk Score: {risk['overall_risk_score']:.1f}/100")
    print(f"Diversification Score: {risk['diversification_score']:.1f}/100")
    print(f"Largest Position Risk: {risk['largest_position_risk']*100:.1f}%")

    print(f"\n💾 Analysis saved to: advanced_portfolio_analysis.json")
    print("🌐 Ready for web viewer!")

if __name__ == "__main__":
    main()
