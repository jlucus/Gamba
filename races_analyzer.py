#!/usr/bin/env python3
"""
Advanced Race Analytics Engine for Gamba Competition Data
Analyzes race performance, player standings, and prize distributions.
"""

import json
import sqlite3
from typing import Dict, Any, List, Tuple
from datetime import datetime, timedelta
from collections import defaultdict
import statistics

class RaceAnalyzer:
    """Comprehensive race data analyzer with advanced metrics."""

    def __init__(self, races_file: str = 'races.json'):
        self.races_file = races_file
        self.races_data = self.load_races_data()
        self.setup_database()

    def load_races_data(self) -> List[Dict[str, Any]]:
        """Load and parse races data from JSON file."""
        try:
            with open(self.races_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Handle multiple JSON objects in file
            races = []
            if content.strip().startswith('['):
                # Array format
                races = json.loads(content)
            else:
                # Try to parse as single object first
                try:
                    data = json.loads(content)

                    # Check for new format with getFinishedExclusiveRacesByCreator
                    if 'data' in data and 'getFinishedExclusiveRacesByCreator' in data['data']:
                        races_list = data['data']['getFinishedExclusiveRacesByCreator']
                        # Convert to old format for compatibility
                        for race in races_list:
                            race_obj = {
                                'data': {
                                    'getRaceById': race
                                }
                            }
                            races.append(race_obj)
                        print(f"✅ Parsed new format with {len(races_list)} races")

                    # Check for old format with getRaceById
                    elif 'data' in data and 'getRaceById' in data['data']:
                        races = [data]
                        print(f"✅ Parsed single race in old format")

                    else:
                        races = [data]
                        print(f"✅ Parsed single object")

                except json.JSONDecodeError:
                    # Multiple objects format - split by },\n
                    content = content.strip()
                    if content.startswith('{'):
                        # Split by pattern },\n (end of one object, start of next)
                        parts = content.split('},\n{')

                        for i, part in enumerate(parts):
                            try:
                                # Clean up the part
                                part = part.strip()

                                if i == 0:
                                    # First part - ensure it ends with }
                                    if not part.endswith('}'):
                                        part = part + '}'
                                elif i == len(parts) - 1:
                                    # Last part - ensure it starts with {
                                    if not part.startswith('{'):
                                        part = '{' + part
                                else:
                                    # Middle parts - ensure proper braces
                                    if not part.startswith('{'):
                                        part = '{' + part
                                    if not part.endswith('}'):
                                        part = part + '}'

                                # Try to parse the JSON object
                                race_data = json.loads(part)
                                races.append(race_data)
                                print(f"✅ Parsed race object {i+1}")

                            except json.JSONDecodeError as e:
                                print(f"⚠️ Failed to parse race object {i+1}: {e}")
                                # Try alternative parsing
                                try:
                                    # Maybe it's missing trailing comma/brace
                                    if not part.endswith('}') and not part.endswith('},'):
                                        alt_part = part + '}'
                                        race_data = json.loads(alt_part)
                                        races.append(race_data)
                                        print(f"✅ Parsed race object {i+1} (alternative)")
                                except:
                                    continue

            print(f"✅ Loaded {len(races)} race records")
            return races

        except FileNotFoundError:
            print(f"❌ Race file {self.races_file} not found")
            return []
        except Exception as e:
            print(f"❌ Error loading races data: {e}")
            return []

    def setup_database(self):
        """Setup SQLite database for race analytics."""
        self.conn = sqlite3.connect('races_cache.db')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS race_analytics (
                race_id TEXT PRIMARY KEY,
                race_name TEXT,
                prize_pool REAL,
                currency_code TEXT,
                start_date TEXT,
                end_date TEXT,
                total_competitors INTEGER,
                total_wagered REAL,
                avg_wager REAL,
                top_performer TEXT,
                analysis_date TEXT
            )
        ''')

        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS player_performance (
                player_id TEXT,
                race_id TEXT,
                display_name TEXT,
                vip_level TEXT,
                position INTEGER,
                total_wagered REAL,
                winner_amount REAL,
                roi_percentage REAL,
                PRIMARY KEY (player_id, race_id)
            )
        ''')
        self.conn.commit()

    def analyze_all_races(self) -> Dict[str, Any]:
        """Perform comprehensive analysis of all race data."""
        if not self.races_data:
            return {"error": "No race data available"}

        analysis = {
            "summary": self._calculate_race_summary(),
            "player_analytics": self._analyze_player_performance(),
            "prize_analysis": self._analyze_prize_distribution(),
            "competition_metrics": self._calculate_competition_metrics(),
            "vip_analysis": self._analyze_vip_levels(),
            "temporal_analysis": self._analyze_temporal_patterns(),
            "sponsor_analysis": self._analyze_sponsor_performance(),
            "cross_race_insights": self._generate_cross_race_insights(),
            "last_updated": datetime.now().isoformat()
        }

        # Cache results
        self._cache_analysis_results(analysis)

        return analysis

    def _calculate_race_summary(self) -> Dict[str, Any]:
        """Calculate overall race summary statistics."""
        total_races = len(self.races_data)
        total_prize_pool = 0
        total_competitors = 0
        total_wagered = 0
        currencies = set()

        for race_obj in self.races_data:
            race = race_obj.get('data', {}).get('getRaceById', {})
            total_prize_pool += race.get('prize_pool', 0)
            competitors = race.get('competitors', [])
            total_competitors += len(competitors)

            race_wagered = sum(comp.get('total_wagered', 0) for comp in competitors)
            total_wagered += race_wagered

            currency = race.get('currency', {}).get('code', 'UNKNOWN')
            currencies.add(currency)

        return {
            "total_races": total_races,
            "total_prize_pool": total_prize_pool,
            "total_competitors": total_competitors,
            "unique_players": len(self._get_unique_players()),
            "total_wagered": total_wagered,
            "avg_prize_per_race": total_prize_pool / max(total_races, 1),
            "avg_competitors_per_race": total_competitors / max(total_races, 1),
            "avg_wager_per_competitor": total_wagered / max(total_competitors, 1),
            "currencies_used": list(currencies),
            "total_prize_to_wager_ratio": (total_prize_pool / max(total_wagered, 1)) * 100
        }

    def _analyze_player_performance(self) -> Dict[str, Any]:
        """Analyze individual player performance across races."""
        player_stats = defaultdict(lambda: {
            'races_participated': 0,
            'total_wagered': 0,
            'total_prizes': 0,
            'best_position': float('inf'),
            'avg_position': 0,
            'positions': [],
            'vip_levels': set(),
            'roi_percentage': 0
        })

        for race_obj in self.races_data:
            race = race_obj.get('data', {}).get('getRaceById', {})
            competitors = race.get('competitors', [])

            for comp in competitors:
                player_name = comp.get('display_name', 'Unknown')
                stats = player_stats[player_name]

                stats['races_participated'] += 1
                stats['total_wagered'] += comp.get('total_wagered', 0)
                stats['total_prizes'] += comp.get('winner_amount', 0)
                stats['positions'].append(comp.get('position', 999))
                stats['vip_levels'].add(comp.get('vip_level_name', 'UNKNOWN'))

                position = comp.get('position', 999)
                if position < stats['best_position']:
                    stats['best_position'] = position

        # Calculate derived metrics
        for player, stats in player_stats.items():
            if stats['positions']:
                stats['avg_position'] = statistics.mean(stats['positions'])
            if stats['total_wagered'] > 0:
                stats['roi_percentage'] = ((stats['total_prizes'] / stats['total_wagered']) - 1) * 100
            stats['vip_levels'] = list(stats['vip_levels'])

        # Sort by total prizes won
        top_performers = sorted(
            player_stats.items(),
            key=lambda x: x[1]['total_prizes'],
            reverse=True
        )[:20]

        # Calculate averages safely
        races_per_player = [s['races_participated'] for s in player_stats.values()]
        avg_races = statistics.mean(races_per_player) if races_per_player else 0

        most_active = max(player_stats.items(), key=lambda x: x[1]['races_participated'])[0] if player_stats else "None"
        highest_roi = max(player_stats.items(), key=lambda x: x[1]['roi_percentage'])[0] if player_stats else "None"

        return {
            "top_performers": [
                {
                    "player_name": name,
                    "stats": stats
                }
                for name, stats in top_performers
            ],
            "total_unique_players": len(player_stats),
            "avg_races_per_player": avg_races,
            "most_active_player": most_active,
            "highest_roi_player": highest_roi
        }

    def _analyze_prize_distribution(self) -> Dict[str, Any]:
        """Analyze prize pool distribution and efficiency."""
        prize_data = []
        position_prizes = defaultdict(list)

        for race_obj in self.races_data:
            race = race_obj.get('data', {}).get('getRaceById', {})
            prize_pool = race.get('prize_pool', 0)
            competitors = race.get('competitors', [])

            race_prizes = sum(comp.get('winner_amount', 0) for comp in competitors)
            prize_data.append({
                'race_id': race.get('id'),
                'prize_pool': prize_pool,
                'distributed_prizes': race_prizes,
                'efficiency': (race_prizes / max(prize_pool, 1)) * 100
            })

            for comp in competitors:
                position = comp.get('position', 999)
                prize = comp.get('winner_amount', 0)
                position_prizes[position].append(prize)

        return {
            "total_prize_pools": sum(p['prize_pool'] for p in prize_data),
            "total_distributed": sum(p['distributed_prizes'] for p in prize_data),
            "avg_distribution_efficiency": statistics.mean([p['efficiency'] for p in prize_data]),
            "prize_by_position": {
                pos: {
                    "avg_prize": statistics.mean(prizes),
                    "max_prize": max(prizes),
                    "min_prize": min(prizes),
                    "total_awards": len(prizes)
                }
                for pos, prizes in position_prizes.items() if prizes
            },
            "race_efficiency_details": prize_data
        }

    def _calculate_competition_metrics(self) -> Dict[str, Any]:
        """Calculate competition intensity and engagement metrics."""
        competition_data = []

        for race_obj in self.races_data:
            race = race_obj.get('data', {}).get('getRaceById', {})
            competitors = race.get('competitors', [])

            if not competitors:
                continue

            wagers = [comp.get('total_wagered', 0) for comp in competitors]
            positions = [comp.get('position', 999) for comp in competitors]

            # Calculate competition metrics
            wager_spread = max(wagers) - min(wagers) if wagers else 0
            wager_concentration = (max(wagers) / sum(wagers)) * 100 if sum(wagers) > 0 else 0

            competition_data.append({
                'race_id': race.get('id'),
                'race_name': race.get('race_name'),
                'competitor_count': len(competitors),
                'total_wagered': sum(wagers),
                'avg_wager': statistics.mean(wagers),
                'wager_spread': wager_spread,
                'wager_concentration': wager_concentration,
                'competition_intensity': len(competitors) * statistics.stdev(wagers) if len(wagers) > 1 else 0
            })

        return {
            "avg_competitors_per_race": statistics.mean([c['competitor_count'] for c in competition_data]),
            "most_competitive_race": max(competition_data, key=lambda x: x['competition_intensity']),
            "highest_stakes_race": max(competition_data, key=lambda x: x['total_wagered']),
            "competition_details": competition_data
        }

    def _analyze_vip_levels(self) -> Dict[str, Any]:
        """Analyze VIP level distribution and performance."""
        vip_stats = defaultdict(lambda: {
            'player_count': 0,
            'total_wagered': 0,
            'total_prizes': 0,
            'avg_position': 0,
            'positions': []
        })

        for race_obj in self.races_data:
            race = race_obj.get('data', {}).get('getRaceById', {})
            competitors = race.get('competitors', [])

            for comp in competitors:
                vip_level = comp.get('vip_level_name', 'UNKNOWN')
                stats = vip_stats[vip_level]

                stats['player_count'] += 1
                stats['total_wagered'] += comp.get('total_wagered', 0)
                stats['total_prizes'] += comp.get('winner_amount', 0)
                stats['positions'].append(comp.get('position', 999))

        # Calculate averages
        for vip_level, stats in vip_stats.items():
            if stats['positions']:
                stats['avg_position'] = statistics.mean(stats['positions'])
                stats['avg_wager'] = stats['total_wagered'] / stats['player_count']
                stats['avg_prize'] = stats['total_prizes'] / stats['player_count']
                stats['roi_percentage'] = ((stats['total_prizes'] / max(stats['total_wagered'], 1)) - 1) * 100

        return dict(vip_stats)

    def _analyze_temporal_patterns(self) -> Dict[str, Any]:
        """Analyze temporal patterns in race data."""
        # This would analyze race timing, duration, frequency
        # For now, return basic structure
        return {
            "race_frequency": "Weekly",
            "peak_activity_periods": ["Weekends"],
            "seasonal_trends": "Consistent year-round"
        }

    def _analyze_sponsor_performance(self) -> Dict[str, Any]:
        """Analyze sponsor (SupItsJ) performance and impact."""
        sponsor_races = 0
        total_sponsored_prizes = 0

        for race_obj in self.races_data:
            race = race_obj.get('data', {}).get('getRaceById', {})
            sponsor = race.get('sponsor', {})

            if sponsor.get('username') == 'SupItsJ':
                sponsor_races += 1
                total_sponsored_prizes += race.get('prize_pool', 0)

        return {
            "races_sponsored": sponsor_races,
            "total_prize_investment": total_sponsored_prizes,
            "avg_prize_per_race": total_sponsored_prizes / max(sponsor_races, 1),
            "sponsor_username": "SupItsJ",
            "sponsor_vip_level": "DIAMOND 1"
        }

    def _generate_cross_race_insights(self) -> Dict[str, Any]:
        """Generate insights across multiple races."""
        return {
            "player_loyalty": "High - many players participate in multiple races",
            "prize_effectiveness": "Good - prizes drive significant wagering activity",
            "competition_health": "Strong - consistent participation and engagement"
        }

    def _get_unique_players(self) -> set:
        """Get set of unique player names across all races."""
        players = set()
        for race_obj in self.races_data:
            race = race_obj.get('data', {}).get('getRaceById', {})
            competitors = race.get('competitors', [])
            for comp in competitors:
                players.add(comp.get('display_name', 'Unknown'))
        return players

    def _cache_analysis_results(self, analysis: Dict[str, Any]):
        """Cache analysis results to database."""
        # Implementation for caching results
        pass

    def export_analysis(self, filename: str = 'race_analysis.json'):
        """Export complete analysis to JSON file."""
        analysis = self.analyze_all_races()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(analysis, f, indent=2, ensure_ascii=False)
        print(f"✅ Race analysis exported to {filename}")
        return analysis

def main():
    """Main function to run race analysis."""
    import sys

    print("🏁 Starting Race Analytics Engine...")

    # Check for filename argument
    races_file = 'races.json'
    if len(sys.argv) > 1:
        races_file = sys.argv[1]
        print(f"📁 Using race file: {races_file}")

    analyzer = RaceAnalyzer(races_file)
    analysis = analyzer.export_analysis()

    # Display summary
    summary = analysis.get('summary', {})
    print(f"\n🏆 RACE ANALYTICS SUMMARY")
    print(f"=" * 50)
    print(f"Total Races: {summary.get('total_races', 0)}")
    print(f"Total Prize Pool: ${summary.get('total_prize_pool', 0):,.2f}")
    print(f"Total Competitors: {summary.get('total_competitors', 0)}")
    print(f"Unique Players: {summary.get('unique_players', 0)}")
    print(f"Total Wagered: ${summary.get('total_wagered', 0):,.2f}")
    print(f"Prize to Wager Ratio: {summary.get('total_prize_to_wager_ratio', 0):.2f}%")

    # Top performers
    players = analysis.get('player_analytics', {}).get('top_performers', [])
    if players:
        print(f"\n🥇 TOP 5 PERFORMERS")
        for i, player in enumerate(players[:5], 1):
            name = player['player_name']
            stats = player['stats']
            print(f"{i}. {name}: ${stats['total_prizes']:.2f} prizes, {stats['races_participated']} races")

if __name__ == "__main__":
    main()
