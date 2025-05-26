#!/usr/bin/env python3
"""
Comprehensive Race Data Collection System
Fetches race data from Gamba API and stores in database with full analytics.
"""

import asyncio
import aiohttp
import json
import time
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
from race_database import RaceDatabase
from gamba_api_client import GambaAPIClient

class RaceDataCollector:
    """Advanced race data collection and storage system."""
    
    def __init__(self, auth_token: str = None, db_path: str = 'race_database.db'):
        self.auth_token = auth_token
        self.api_client = GambaAPIClient(auth_token)
        self.database = RaceDatabase(db_path)
        self.setup_logging()
    
    def setup_logging(self):
        """Setup logging for data collection operations."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('race_collection.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def collect_race_range(self, start_race_id: int, end_race_id: int, delay: float = 1.0) -> Dict[str, Any]:
        """
        Collect a range of race data and store in database.
        
        Args:
            start_race_id: Starting race ID
            end_race_id: Ending race ID (inclusive)
            delay: Delay between API calls in seconds
            
        Returns:
            Collection summary statistics
        """
        self.logger.info(f"🚀 Starting race collection: {start_race_id} to {end_race_id}")
        
        stats = {
            'total_races_attempted': 0,
            'successful_collections': 0,
            'failed_collections': 0,
            'total_players_found': 0,
            'total_prize_pool': 0,
            'total_wagered': 0,
            'unique_sponsors': set(),
            'collection_start_time': datetime.now().isoformat(),
            'collection_end_time': None,
            'errors': []
        }
        
        for race_id in range(start_race_id, end_race_id + 1):
            stats['total_races_attempted'] += 1
            
            try:
                self.logger.info(f"📡 Fetching race {race_id}...")
                
                # Fetch race data
                race_data = self.api_client.get_race_by_id(race_id)
                
                if race_data and 'data' in race_data:
                    race_info = race_data['data'].get('getRaceById')
                    
                    if race_info:
                        # Store in database
                        success = self.database.insert_race_data(race_data)
                        
                        if success:
                            stats['successful_collections'] += 1
                            
                            # Update statistics
                            competitors = race_info.get('competitors', [])
                            stats['total_players_found'] += len(competitors)
                            stats['total_prize_pool'] += race_info.get('prize_pool', 0)
                            stats['total_wagered'] += sum(c.get('total_wagered', 0) for c in competitors)
                            
                            sponsor = race_info.get('sponsor', {})
                            if sponsor.get('username'):
                                stats['unique_sponsors'].add(sponsor['username'])
                            
                            self.logger.info(f"✅ Successfully processed race {race_id}")
                        else:
                            stats['failed_collections'] += 1
                            self.logger.error(f"❌ Failed to store race {race_id} in database")
                    else:
                        stats['failed_collections'] += 1
                        self.logger.warning(f"⚠️ No race data found for race {race_id}")
                else:
                    stats['failed_collections'] += 1
                    self.logger.warning(f"⚠️ Invalid response for race {race_id}")
                
                # Rate limiting
                if race_id < end_race_id:
                    time.sleep(delay)
                    
            except Exception as e:
                stats['failed_collections'] += 1
                error_msg = f"Error processing race {race_id}: {str(e)}"
                stats['errors'].append(error_msg)
                self.logger.error(error_msg)
                
                # Continue with next race
                continue
        
        stats['collection_end_time'] = datetime.now().isoformat()
        stats['unique_sponsors'] = list(stats['unique_sponsors'])
        
        # Generate collection report
        self.generate_collection_report(stats)
        
        return stats
    
    def collect_recent_races(self, days_back: int = 30) -> Dict[str, Any]:
        """
        Collect recent races based on estimated race frequency.
        
        Args:
            days_back: Number of days to look back
            
        Returns:
            Collection summary
        """
        # Estimate race IDs based on frequency (assuming ~1-2 races per week)
        races_per_week = 1.5
        estimated_races = int(days_back / 7 * races_per_week)
        
        # Get the latest known race ID from database
        cursor = self.database.conn.execute('SELECT MAX(CAST(race_id AS INTEGER)) as max_id FROM races')
        result = cursor.fetchone()
        max_known_id = result['max_id'] if result and result['max_id'] else 100
        
        # Collect from estimated range
        start_id = max(max_known_id - estimated_races, 1)
        end_id = max_known_id + 10  # Look ahead for new races
        
        return self.collect_race_range(start_id, end_id)
    
    def monitor_new_races(self, check_interval: int = 3600, max_lookback: int = 5):
        """
        Monitor for new races continuously.
        
        Args:
            check_interval: Check interval in seconds (default: 1 hour)
            max_lookback: How many race IDs to check back from latest
        """
        self.logger.info(f"🔄 Starting race monitoring (checking every {check_interval}s)")
        
        while True:
            try:
                # Get latest race ID from database
                cursor = self.database.conn.execute('SELECT MAX(CAST(race_id AS INTEGER)) as max_id FROM races')
                result = cursor.fetchone()
                latest_id = result['max_id'] if result and result['max_id'] else 100
                
                # Check for new races
                start_check = latest_id - max_lookback
                end_check = latest_id + 10
                
                self.logger.info(f"🔍 Checking for new races: {start_check} to {end_check}")
                
                new_races_found = 0
                for race_id in range(start_check, end_check + 1):
                    # Check if race already exists
                    cursor = self.database.conn.execute('SELECT race_id FROM races WHERE race_id = ?', (str(race_id),))
                    if cursor.fetchone():
                        continue  # Race already exists
                    
                    # Try to fetch new race
                    race_data = self.api_client.get_race_by_id(race_id)
                    if race_data and 'data' in race_data and race_data['data'].get('getRaceById'):
                        success = self.database.insert_race_data(race_data)
                        if success:
                            new_races_found += 1
                            self.logger.info(f"🆕 Found and stored new race {race_id}")
                
                if new_races_found > 0:
                    self.logger.info(f"✅ Found {new_races_found} new races")
                else:
                    self.logger.info("📊 No new races found")
                
                # Wait before next check
                time.sleep(check_interval)
                
            except KeyboardInterrupt:
                self.logger.info("🛑 Race monitoring stopped by user")
                break
            except Exception as e:
                self.logger.error(f"❌ Error in race monitoring: {e}")
                time.sleep(60)  # Wait 1 minute before retrying
    
    def generate_collection_report(self, stats: Dict[str, Any]):
        """Generate a comprehensive collection report."""
        report = {
            'collection_summary': stats,
            'database_statistics': self.get_database_statistics(),
            'top_performers': self.database.get_top_players(10),
            'sponsor_analysis': self.analyze_sponsors(),
            'generated_at': datetime.now().isoformat()
        }
        
        # Save report
        with open('race_collection_report.json', 'w') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_collection_summary(stats)
    
    def get_database_statistics(self) -> Dict[str, Any]:
        """Get current database statistics."""
        stats = {}
        
        # Race statistics
        cursor = self.database.conn.execute('SELECT COUNT(*) as count, SUM(prize_pool) as total_prizes FROM races')
        result = cursor.fetchone()
        stats['total_races'] = result['count']
        stats['total_prize_pools'] = result['total_prizes'] or 0
        
        # Player statistics
        cursor = self.database.conn.execute('SELECT COUNT(*) as count FROM players')
        stats['total_players'] = cursor.fetchone()['count']
        
        # Sponsor statistics
        cursor = self.database.conn.execute('SELECT COUNT(*) as count FROM sponsors')
        stats['total_sponsors'] = cursor.fetchone()['count']
        
        # Participation statistics
        cursor = self.database.conn.execute('SELECT COUNT(*) as count, SUM(total_wagered) as total_wagered FROM race_participants')
        result = cursor.fetchone()
        stats['total_participations'] = result['count']
        stats['total_wagered'] = result['total_wagered'] or 0
        
        return stats
    
    def analyze_sponsors(self) -> List[Dict[str, Any]]:
        """Analyze sponsor performance."""
        cursor = self.database.conn.execute('''
            SELECT s.*, COUNT(r.race_id) as races_sponsored
            FROM sponsors s
            LEFT JOIN races r ON s.sponsor_id = r.sponsor_id
            GROUP BY s.sponsor_id
            ORDER BY s.total_prize_pool DESC
        ''')
        
        return [dict(row) for row in cursor.fetchall()]
    
    def print_collection_summary(self, stats: Dict[str, Any]):
        """Print a formatted collection summary."""
        print("\n" + "="*60)
        print("🏁 RACE DATA COLLECTION SUMMARY")
        print("="*60)
        print(f"📊 Races Attempted: {stats['total_races_attempted']}")
        print(f"✅ Successful: {stats['successful_collections']}")
        print(f"❌ Failed: {stats['failed_collections']}")
        print(f"👥 Players Found: {stats['total_players_found']}")
        print(f"💰 Total Prize Pool: ${stats['total_prize_pool']:,.2f}")
        print(f"🎯 Total Wagered: ${stats['total_wagered']:,.2f}")
        print(f"🏢 Unique Sponsors: {len(stats['unique_sponsors'])}")
        
        if stats['unique_sponsors']:
            print(f"📋 Sponsors: {', '.join(stats['unique_sponsors'])}")
        
        if stats['errors']:
            print(f"\n⚠️ Errors ({len(stats['errors'])}):")
            for error in stats['errors'][:5]:  # Show first 5 errors
                print(f"   • {error}")
            if len(stats['errors']) > 5:
                print(f"   • ... and {len(stats['errors']) - 5} more")
    
    def export_player_data(self, filename: str = 'player_export.json'):
        """Export all player data for analysis."""
        players = self.database.get_top_players(1000)  # Get all players
        
        # Enrich with race history
        for player in players:
            player['race_history'] = self.database.get_player_race_history(player['player_id'])
        
        with open(filename, 'w') as f:
            json.dump(players, f, indent=2, ensure_ascii=False)
        
        print(f"📤 Exported {len(players)} players to {filename}")
    
    def close(self):
        """Close database connection."""
        self.database.close()

def main():
    """Main function for race data collection."""
    import sys
    
    print("🏁 Race Data Collection System")
    print("="*50)
    
    # Initialize collector (add your auth token here)
    collector = RaceDataCollector(auth_token="YOUR_TOKEN_HERE")
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "collect":
            # Collect specific range
            start_id = int(sys.argv[2]) if len(sys.argv) > 2 else 90
            end_id = int(sys.argv[3]) if len(sys.argv) > 3 else 100
            collector.collect_race_range(start_id, end_id)
            
        elif command == "recent":
            # Collect recent races
            days = int(sys.argv[2]) if len(sys.argv) > 2 else 30
            collector.collect_recent_races(days)
            
        elif command == "monitor":
            # Monitor for new races
            interval = int(sys.argv[2]) if len(sys.argv) > 2 else 3600
            collector.monitor_new_races(interval)
            
        elif command == "export":
            # Export player data
            filename = sys.argv[2] if len(sys.argv) > 2 else 'player_export.json'
            collector.export_player_data(filename)
            
        else:
            print("❌ Unknown command")
    else:
        print("💡 Usage examples:")
        print("  python race_data_collector.py collect 90 100")
        print("  python race_data_collector.py recent 30")
        print("  python race_data_collector.py monitor 3600")
        print("  python race_data_collector.py export players.json")
    
    collector.close()

if __name__ == "__main__":
    main()
