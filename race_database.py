#!/usr/bin/env python3
"""
Comprehensive Race Database System for Gamba Competition Data
Stores races, players, wagers, sponsors, and performance metrics.
"""

import sqlite3
import json
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import hashlib

class RaceDatabase:
    """Comprehensive database for race analytics and player tracking."""
    
    def __init__(self, db_path: str = 'race_database.db'):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # Enable dict-like access
        self.setup_database()
    
    def setup_database(self):
        """Create all necessary tables for race analytics."""
        
        # Sponsors/Affiliates table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS sponsors (
                sponsor_id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                vip_level TEXT,
                total_races_sponsored INTEGER DEFAULT 0,
                total_prize_pool REAL DEFAULT 0,
                avg_prize_per_race REAL DEFAULT 0,
                first_race_date TEXT,
                last_race_date TEXT,
                preferences TEXT,  -- JSON string
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Races table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS races (
                race_id TEXT PRIMARY KEY,
                sponsor_id TEXT,
                race_name TEXT NOT NULL,
                prize_pool REAL NOT NULL,
                currency_id TEXT,
                currency_code TEXT,
                start_date TEXT,
                end_date TEXT,
                style TEXT,
                total_competitors INTEGER DEFAULT 0,
                total_wagered REAL DEFAULT 0,
                avg_wager_per_competitor REAL DEFAULT 0,
                prize_distribution_efficiency REAL DEFAULT 0,
                competition_intensity REAL DEFAULT 0,
                status TEXT DEFAULT 'active',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sponsor_id) REFERENCES sponsors (sponsor_id)
            )
        ''')
        
        # Players table
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS players (
                player_id TEXT PRIMARY KEY,
                display_name TEXT NOT NULL,
                vip_level TEXT,
                total_races_participated INTEGER DEFAULT 0,
                total_wagered REAL DEFAULT 0,
                total_prizes_won REAL DEFAULT 0,
                best_position INTEGER DEFAULT 999,
                avg_position REAL DEFAULT 999,
                win_rate REAL DEFAULT 0,
                roi_percentage REAL DEFAULT 0,
                avatar_url TEXT,
                first_race_date TEXT,
                last_race_date TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Race participants (many-to-many relationship)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS race_participants (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                race_id TEXT,
                player_id TEXT,
                position INTEGER,
                total_wagered REAL,
                winner_amount REAL,
                roi_percentage REAL,
                participation_date TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (race_id) REFERENCES races (race_id),
                FOREIGN KEY (player_id) REFERENCES players (player_id),
                UNIQUE(race_id, player_id)
            )
        ''')
        
        # Sponsor codes/eligibility
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS sponsor_codes (
                code_id TEXT PRIMARY KEY,
                race_id TEXT,
                code TEXT NOT NULL,
                usage_limit INTEGER,
                usage_count INTEGER DEFAULT 0,
                total_wagered REAL DEFAULT 0,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (race_id) REFERENCES races (race_id)
            )
        ''')
        
        # Player performance history
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS player_performance_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                player_id TEXT,
                race_id TEXT,
                date TEXT,
                position INTEGER,
                wagered REAL,
                prize_won REAL,
                competitors_count INTEGER,
                performance_score REAL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (player_id) REFERENCES players (player_id),
                FOREIGN KEY (race_id) REFERENCES races (race_id)
            )
        ''')
        
        # Analytics cache for performance
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS analytics_cache (
                cache_key TEXT PRIMARY KEY,
                data TEXT,  -- JSON string
                expires_at TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes for performance
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_races_sponsor ON races(sponsor_id)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_participants_race ON race_participants(race_id)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_participants_player ON race_participants(player_id)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_performance_player ON player_performance_history(player_id)')
        self.conn.execute('CREATE INDEX IF NOT EXISTS idx_performance_date ON player_performance_history(date)')
        
        self.conn.commit()
        print("✅ Database schema created successfully")
    
    def insert_race_data(self, race_data: Dict[str, Any]) -> bool:
        """Insert complete race data including sponsor, players, and participants."""
        try:
            race_info = race_data.get('data', {}).get('getRaceById', {})
            if not race_info:
                return False
            
            # Insert sponsor
            sponsor = race_info.get('sponsor', {})
            if sponsor:
                self.insert_sponsor(sponsor)
            
            # Insert race
            race_id = race_info.get('id')
            self.insert_race(race_info)
            
            # Insert sponsor codes
            eligibility = race_info.get('eligibility', [])
            for code_info in eligibility:
                self.insert_sponsor_code(race_id, code_info)
            
            # Insert competitors
            competitors = race_info.get('competitors', [])
            for competitor in competitors:
                player_id = competitor.get('competitor_id') or competitor.get('id')
                
                # Insert/update player
                self.insert_player(competitor)
                
                # Insert race participation
                self.insert_race_participant(race_id, player_id, competitor)
                
                # Insert performance history
                self.insert_performance_history(player_id, race_id, competitor, len(competitors))
            
            # Update aggregated statistics
            self.update_race_statistics(race_id)
            self.update_player_statistics()
            self.update_sponsor_statistics()
            
            self.conn.commit()
            print(f"✅ Successfully inserted race {race_id}")
            return True
            
        except Exception as e:
            print(f"❌ Error inserting race data: {e}")
            self.conn.rollback()
            return False
    
    def insert_sponsor(self, sponsor_data: Dict[str, Any]):
        """Insert or update sponsor information."""
        sponsor_id = sponsor_data.get('id')
        username = sponsor_data.get('username')
        vip_level = sponsor_data.get('vip_level_name')
        preferences = json.dumps(sponsor_data.get('preferences', {}))
        
        self.conn.execute('''
            INSERT OR REPLACE INTO sponsors 
            (sponsor_id, username, vip_level, preferences, updated_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (sponsor_id, username, vip_level, preferences, datetime.now().isoformat()))
    
    def insert_race(self, race_data: Dict[str, Any]):
        """Insert race information."""
        race_id = race_data.get('id')
        sponsor_id = race_data.get('sponsor_id')
        race_name = race_data.get('race_name')
        prize_pool = race_data.get('prize_pool', 0)
        currency_id = race_data.get('currency_id')
        currency_code = race_data.get('currency', {}).get('code')
        start_date = race_data.get('start_date')
        end_date = race_data.get('end_date')
        style = race_data.get('style')
        
        competitors = race_data.get('competitors', [])
        total_competitors = len(competitors)
        total_wagered = sum(comp.get('total_wagered', 0) for comp in competitors)
        avg_wager = total_wagered / max(total_competitors, 1)
        
        self.conn.execute('''
            INSERT OR REPLACE INTO races 
            (race_id, sponsor_id, race_name, prize_pool, currency_id, currency_code,
             start_date, end_date, style, total_competitors, total_wagered, 
             avg_wager_per_competitor, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (race_id, sponsor_id, race_name, prize_pool, currency_id, currency_code,
              start_date, end_date, style, total_competitors, total_wagered, 
              avg_wager, datetime.now().isoformat()))
    
    def insert_player(self, player_data: Dict[str, Any]):
        """Insert or update player information."""
        player_id = player_data.get('competitor_id') or player_data.get('id')
        display_name = player_data.get('display_name')
        vip_level = player_data.get('vip_level_name')
        avatar_url = player_data.get('avatar')
        
        self.conn.execute('''
            INSERT OR IGNORE INTO players 
            (player_id, display_name, vip_level, avatar_url)
            VALUES (?, ?, ?, ?)
        ''', (player_id, display_name, vip_level, avatar_url))
        
        # Update if exists
        self.conn.execute('''
            UPDATE players SET 
                display_name = ?, vip_level = ?, avatar_url = ?, updated_at = ?
            WHERE player_id = ?
        ''', (display_name, vip_level, avatar_url, datetime.now().isoformat(), player_id))
    
    def insert_race_participant(self, race_id: str, player_id: str, participant_data: Dict[str, Any]):
        """Insert race participation record."""
        position = participant_data.get('position')
        total_wagered = participant_data.get('total_wagered', 0)
        winner_amount = participant_data.get('winner_amount', 0)
        roi_percentage = ((winner_amount / max(total_wagered, 1)) - 1) * 100 if total_wagered > 0 else 0
        
        self.conn.execute('''
            INSERT OR REPLACE INTO race_participants 
            (race_id, player_id, position, total_wagered, winner_amount, roi_percentage, participation_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (race_id, player_id, position, total_wagered, winner_amount, roi_percentage, datetime.now().isoformat()))
    
    def insert_sponsor_code(self, race_id: str, code_data: Dict[str, Any]):
        """Insert sponsor code information."""
        code_id = code_data.get('id')
        code = code_data.get('code')
        usage_limit = code_data.get('usage_limit')
        usage_count = code_data.get('usage_count', 0)
        total_wagered = code_data.get('total_wagered', 0)
        
        self.conn.execute('''
            INSERT OR REPLACE INTO sponsor_codes 
            (code_id, race_id, code, usage_limit, usage_count, total_wagered)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code_id, race_id, code, usage_limit, usage_count, total_wagered))
    
    def insert_performance_history(self, player_id: str, race_id: str, participant_data: Dict[str, Any], total_competitors: int):
        """Insert player performance history record."""
        position = participant_data.get('position')
        wagered = participant_data.get('total_wagered', 0)
        prize_won = participant_data.get('winner_amount', 0)
        
        # Calculate performance score (0-100, higher is better)
        position_score = max(0, (total_competitors - position + 1) / total_competitors * 50)
        roi_score = min(50, max(0, ((prize_won / max(wagered, 1)) - 1) * 100))
        performance_score = position_score + roi_score
        
        self.conn.execute('''
            INSERT OR REPLACE INTO player_performance_history 
            (player_id, race_id, date, position, wagered, prize_won, competitors_count, performance_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (player_id, race_id, datetime.now().isoformat(), position, wagered, prize_won, total_competitors, performance_score))
    
    def update_race_statistics(self, race_id: str):
        """Update aggregated race statistics."""
        # Calculate prize distribution efficiency
        cursor = self.conn.execute('''
            SELECT r.prize_pool, SUM(rp.winner_amount) as distributed_prizes
            FROM races r
            LEFT JOIN race_participants rp ON r.race_id = rp.race_id
            WHERE r.race_id = ?
            GROUP BY r.race_id
        ''', (race_id,))
        
        result = cursor.fetchone()
        if result:
            prize_pool = result['prize_pool']
            distributed_prizes = result['distributed_prizes'] or 0
            efficiency = (distributed_prizes / max(prize_pool, 1)) * 100
            
            self.conn.execute('''
                UPDATE races SET prize_distribution_efficiency = ?, updated_at = ?
                WHERE race_id = ?
            ''', (efficiency, datetime.now().isoformat(), race_id))
    
    def update_player_statistics(self):
        """Update aggregated player statistics."""
        self.conn.execute('''
            UPDATE players SET 
                total_races_participated = (
                    SELECT COUNT(*) FROM race_participants WHERE player_id = players.player_id
                ),
                total_wagered = (
                    SELECT COALESCE(SUM(total_wagered), 0) FROM race_participants WHERE player_id = players.player_id
                ),
                total_prizes_won = (
                    SELECT COALESCE(SUM(winner_amount), 0) FROM race_participants WHERE player_id = players.player_id
                ),
                best_position = (
                    SELECT MIN(position) FROM race_participants WHERE player_id = players.player_id
                ),
                avg_position = (
                    SELECT AVG(position) FROM race_participants WHERE player_id = players.player_id
                ),
                updated_at = ?
        ''', (datetime.now().isoformat(),))
        
        # Update ROI percentage
        self.conn.execute('''
            UPDATE players SET 
                roi_percentage = CASE 
                    WHEN total_wagered > 0 THEN ((total_prizes_won / total_wagered) - 1) * 100
                    ELSE 0
                END
        ''')
    
    def update_sponsor_statistics(self):
        """Update aggregated sponsor statistics."""
        self.conn.execute('''
            UPDATE sponsors SET 
                total_races_sponsored = (
                    SELECT COUNT(*) FROM races WHERE sponsor_id = sponsors.sponsor_id
                ),
                total_prize_pool = (
                    SELECT COALESCE(SUM(prize_pool), 0) FROM races WHERE sponsor_id = sponsors.sponsor_id
                ),
                updated_at = ?
        ''', (datetime.now().isoformat(),))
        
        # Update average prize per race
        self.conn.execute('''
            UPDATE sponsors SET 
                avg_prize_per_race = CASE 
                    WHEN total_races_sponsored > 0 THEN total_prize_pool / total_races_sponsored
                    ELSE 0
                END
        ''')
    
    def get_top_players(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top performing players."""
        cursor = self.conn.execute('''
            SELECT * FROM players 
            WHERE total_races_participated > 0
            ORDER BY total_prizes_won DESC, roi_percentage DESC
            LIMIT ?
        ''', (limit,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_sponsor_performance(self, sponsor_id: str) -> Dict[str, Any]:
        """Get detailed sponsor performance metrics."""
        cursor = self.conn.execute('''
            SELECT s.*, 
                   COUNT(r.race_id) as races_count,
                   AVG(r.total_competitors) as avg_competitors,
                   AVG(r.total_wagered) as avg_total_wagered,
                   AVG(r.prize_distribution_efficiency) as avg_efficiency
            FROM sponsors s
            LEFT JOIN races r ON s.sponsor_id = r.sponsor_id
            WHERE s.sponsor_id = ?
            GROUP BY s.sponsor_id
        ''', (sponsor_id,))
        
        result = cursor.fetchone()
        return dict(result) if result else {}
    
    def get_player_race_history(self, player_id: str) -> List[Dict[str, Any]]:
        """Get complete race history for a player."""
        cursor = self.conn.execute('''
            SELECT rp.*, r.race_name, r.prize_pool, r.start_date, r.total_competitors
            FROM race_participants rp
            JOIN races r ON rp.race_id = r.race_id
            WHERE rp.player_id = ?
            ORDER BY r.start_date DESC
        ''', (player_id,))
        
        return [dict(row) for row in cursor.fetchall()]
    
    def close(self):
        """Close database connection."""
        self.conn.close()

def main():
    """Test the database system."""
    db = RaceDatabase()
    
    # Test with sample data
    try:
        with open('sample_races.json', 'r') as f:
            content = f.read()
            # Parse multiple JSON objects
            objects = content.strip().split('},\n{')
            for i, obj in enumerate(objects):
                if i == 0:
                    obj = obj + '}' if not obj.endswith('}') else obj
                elif i == len(objects) - 1:
                    obj = '{' + obj if not obj.startswith('{') else obj
                else:
                    obj = '{' + obj + '}'
                
                try:
                    race_data = json.loads(obj)
                    db.insert_race_data(race_data)
                except json.JSONDecodeError:
                    continue
        
        print("\n🏆 TOP PLAYERS:")
        top_players = db.get_top_players(5)
        for i, player in enumerate(top_players, 1):
            print(f"{i}. {player['display_name']}: ${player['total_prizes_won']:.2f} ({player['total_races_participated']} races)")
        
    except FileNotFoundError:
        print("Sample races file not found")
    
    db.close()

if __name__ == "__main__":
    main()
