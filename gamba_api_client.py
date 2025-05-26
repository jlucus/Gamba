#!/usr/bin/env python3
"""
Gamba API Client for fetching race data and player standings.
Handles GraphQL queries and authentication for live data retrieval.
"""

import requests
import json
import time
from typing import Dict, Any, List, Optional
from urllib.parse import quote
import hashlib

class GambaAPIClient:
    """Client for interacting with Gamba's GraphQL API."""
    
    def __init__(self, auth_token: str = None):
        self.base_url = "https://gamba.com/_api/@"
        self.auth_token = auth_token
        self.session = requests.Session()
        self.setup_headers()
    
    def setup_headers(self):
        """Setup default headers for API requests."""
        self.session.headers.update({
            'accept': '*/*',
            'accept-encoding': 'gzip, deflate, br, zstd',
            'accept-language': 'en-US,en;q=0.9,es;q=0.8',
            'content-type': 'application/json',
            'sec-ch-ua': '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'sec-fetch-dest': 'empty',
            'sec-fetch-mode': 'cors',
            'sec-fetch-site': 'same-origin',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        })
        
        if self.auth_token:
            self.session.headers['authorization'] = f'Bearer {self.auth_token}'
    
    def get_race_by_id(self, race_id: int) -> Optional[Dict[str, Any]]:
        """
        Fetch race data by race ID.
        
        Args:
            race_id: The ID of the race to fetch
            
        Returns:
            Race data dictionary or None if failed
        """
        try:
            # Prepare GraphQL query parameters
            variables = {"raceId": race_id}
            extensions = {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "c682a2e9795a0f35f291d417f01543135f4be142180598bcb6159c26ba2177ef"
                }
            }
            
            # URL encode the parameters
            variables_encoded = quote(json.dumps(variables))
            extensions_encoded = quote(json.dumps(extensions))
            
            # Build the URL
            url = f"{self.base_url}?operationName=getRaceById&variables={variables_encoded}&extensions={extensions_encoded}"
            
            # Make the request
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ API request failed for race {race_id}: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"❌ Failed to parse JSON response for race {race_id}: {e}")
            return None
        except Exception as e:
            print(f"❌ Unexpected error fetching race {race_id}: {e}")
            return None
    
    def get_multiple_races(self, race_ids: List[int], delay: float = 1.0) -> List[Dict[str, Any]]:
        """
        Fetch multiple races with rate limiting.
        
        Args:
            race_ids: List of race IDs to fetch
            delay: Delay between requests in seconds
            
        Returns:
            List of race data dictionaries
        """
        races = []
        
        for i, race_id in enumerate(race_ids):
            print(f"📡 Fetching race {race_id} ({i+1}/{len(race_ids)})...")
            
            race_data = self.get_race_by_id(race_id)
            if race_data:
                races.append(race_data)
                print(f"✅ Successfully fetched race {race_id}")
            else:
                print(f"❌ Failed to fetch race {race_id}")
            
            # Rate limiting
            if i < len(race_ids) - 1:
                time.sleep(delay)
        
        return races
    
    def get_race_range(self, start_id: int, end_id: int, delay: float = 1.0) -> List[Dict[str, Any]]:
        """
        Fetch a range of race IDs.
        
        Args:
            start_id: Starting race ID
            end_id: Ending race ID (inclusive)
            delay: Delay between requests in seconds
            
        Returns:
            List of race data dictionaries
        """
        race_ids = list(range(start_id, end_id + 1))
        return self.get_multiple_races(race_ids, delay)
    
    def save_races_to_file(self, races: List[Dict[str, Any]], filename: str = 'fetched_races.json'):
        """
        Save fetched race data to JSON file.
        
        Args:
            races: List of race data dictionaries
            filename: Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(races, f, indent=2, ensure_ascii=False)
            print(f"💾 Saved {len(races)} races to {filename}")
        except Exception as e:
            print(f"❌ Failed to save races to {filename}: {e}")
    
    def get_player_standings(self, race_id: int) -> Optional[List[Dict[str, Any]]]:
        """
        Extract player standings from race data.
        
        Args:
            race_id: Race ID to get standings for
            
        Returns:
            List of competitor dictionaries or None if failed
        """
        race_data = self.get_race_by_id(race_id)
        if not race_data:
            return None
        
        race_info = race_data.get('data', {}).get('getRaceById', {})
        competitors = race_info.get('competitors', [])
        
        # Sort by position
        competitors.sort(key=lambda x: x.get('position', 999))
        
        return competitors
    
    def monitor_race_updates(self, race_id: int, interval: int = 300) -> None:
        """
        Monitor a race for updates (useful for live races).
        
        Args:
            race_id: Race ID to monitor
            interval: Check interval in seconds
        """
        print(f"🔄 Starting race monitor for race {race_id} (checking every {interval}s)")
        
        last_data = None
        
        while True:
            try:
                current_data = self.get_race_by_id(race_id)
                
                if current_data and current_data != last_data:
                    print(f"📊 Race {race_id} updated at {time.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # Save update
                    timestamp = int(time.time())
                    filename = f"race_{race_id}_update_{timestamp}.json"
                    self.save_races_to_file([current_data], filename)
                    
                    last_data = current_data
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                print(f"\n🛑 Stopped monitoring race {race_id}")
                break
            except Exception as e:
                print(f"❌ Error monitoring race {race_id}: {e}")
                time.sleep(interval)

def create_sample_payloads() -> Dict[str, Any]:
    """Create sample API payloads for documentation."""
    
    samples = {
        "get_race_by_id": {
            "description": "Fetch race data by ID",
            "method": "GET",
            "url_template": "https://gamba.com/_api/@?operationName=getRaceById&variables={variables}&extensions={extensions}",
            "variables": {"raceId": 98},
            "extensions": {
                "persistedQuery": {
                    "version": 1,
                    "sha256Hash": "c682a2e9795a0f35f291d417f01543135f4be142180598bcb6159c26ba2177ef"
                }
            },
            "headers": {
                "accept": "*/*",
                "authorization": "Bearer YOUR_TOKEN_HERE",
                "content-type": "application/json",
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
            "example_response": {
                "data": {
                    "getRaceById": {
                        "id": "98",
                        "prize_pool": 3,
                        "currency_id": "404",
                        "race_name": "$500 BetOnGamba",
                        "competitors": [
                            {
                                "display_name": "PlayerName",
                                "total_wagered": 1000.0,
                                "winner_amount": 50.0,
                                "position": 1,
                                "vip_level_name": "PLATINUM 1"
                            }
                        ]
                    }
                }
            }
        },
        "batch_fetch": {
            "description": "Fetch multiple races sequentially",
            "race_ids": [34, 98, 99, 100],
            "rate_limit": "1 request per second recommended",
            "total_time_estimate": "4 seconds for 4 races"
        },
        "monitoring": {
            "description": "Monitor live race for updates",
            "check_interval": 300,
            "use_case": "Track live competition standings"
        }
    }
    
    return samples

def main():
    """Main function for testing and demonstration."""
    print("🎮 Gamba API Client")
    print("=" * 50)
    
    # Create sample payloads
    samples = create_sample_payloads()
    with open('sample_race_queries.json', 'w', encoding='utf-8') as f:
        json.dump(samples, f, indent=2, ensure_ascii=False)
    print("📋 Sample payloads saved to sample_race_queries.json")
    
    # Example usage (commented out to avoid making actual API calls)
    """
    # Initialize client (add your auth token)
    client = GambaAPIClient(auth_token="YOUR_TOKEN_HERE")
    
    # Fetch a single race
    race_data = client.get_race_by_id(98)
    if race_data:
        print("✅ Successfully fetched race data")
    
    # Fetch multiple races
    races = client.get_multiple_races([34, 98], delay=1.0)
    client.save_races_to_file(races, 'new_races.json')
    
    # Get player standings
    standings = client.get_player_standings(98)
    if standings:
        print(f"🏆 Top player: {standings[0]['display_name']}")
    """
    
    print("\n💡 To use this client:")
    print("1. Add your Gamba auth token")
    print("2. Call client.get_race_by_id(race_id)")
    print("3. Use client.get_multiple_races() for batch fetching")
    print("4. Monitor live races with client.monitor_race_updates()")

if __name__ == "__main__":
    main()
