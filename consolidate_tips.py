#!/usr/bin/env python3
"""
Script to consolidate multiple concatenated JSON objects from tips.json
into a single valid JSON structure.
"""

import json
import re
from typing import List, Dict, Any

def extract_json_objects(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract individual JSON objects from a file containing multiple concatenated JSON objects.
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find all JSON objects by looking for patterns that start with { and end with }
    # We'll use a simple approach: split by lines that contain only "{"
    lines = content.split('\n')
    json_objects = []
    current_object_lines = []
    brace_count = 0
    in_object = False
    
    for line in lines:
        stripped_line = line.strip()
        
        # Start of a new JSON object
        if stripped_line == '{' and not in_object:
            if current_object_lines:
                # Process previous object
                try:
                    obj_str = '\n'.join(current_object_lines)
                    obj = json.loads(obj_str)
                    json_objects.append(obj)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON object: {e}")
                    print(f"Object content: {obj_str[:200]}...")
            
            current_object_lines = [line]
            brace_count = 1
            in_object = True
        elif in_object:
            current_object_lines.append(line)
            # Count braces to know when object ends
            brace_count += line.count('{') - line.count('}')
            
            if brace_count == 0:
                # Object is complete
                try:
                    obj_str = '\n'.join(current_object_lines)
                    obj = json.loads(obj_str)
                    json_objects.append(obj)
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON object: {e}")
                    print(f"Object content: {obj_str[:200]}...")
                
                current_object_lines = []
                in_object = False
    
    # Handle last object if file doesn't end properly
    if current_object_lines and in_object:
        try:
            obj_str = '\n'.join(current_object_lines)
            obj = json.loads(obj_str)
            json_objects.append(obj)
        except json.JSONDecodeError as e:
            print(f"Error parsing final JSON object: {e}")
    
    return json_objects

def consolidate_tip_data(json_objects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Consolidate multiple tip JSON objects into a single structure.
    """
    all_tips = []
    total_page_count = 0
    
    for obj in json_objects:
        if 'data' in obj and 'myTips' in obj['data']:
            tips_data = obj['data']['myTips']
            if 'results' in tips_data:
                all_tips.extend(tips_data['results'])
            
            if 'paginate' in tips_data and 'page_count' in tips_data['paginate']:
                total_page_count += tips_data['paginate']['page_count']
    
    # Remove duplicates based on transaction ID
    unique_tips = {}
    for tip in all_tips:
        tip_id = tip.get('id') or tip.get('transaction_id')
        if tip_id and tip_id not in unique_tips:
            unique_tips[tip_id] = tip
    
    # Sort by issued_at date (newest first)
    sorted_tips = sorted(
        unique_tips.values(),
        key=lambda x: x.get('issued_at', ''),
        reverse=True
    )
    
    # Create consolidated structure
    consolidated = {
        "data": {
            "myTips": {
                "results": sorted_tips,
                "paginate": {
                    "exclusive_start_key": None,
                    "page_count": total_page_count,
                    "__typename": "TransactionPaginate"
                },
                "__typename": "TipTransactions"
            }
        }
    }
    
    return consolidated

def analyze_tips(tips_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze the consolidated tips data and provide statistics.
    """
    tips = tips_data['data']['myTips']['results']
    
    stats = {
        'total_transactions': len(tips),
        'deposits': 0,
        'withdrawals': 0,
        'currencies': {},
        'total_by_currency': {},
        'date_range': {'earliest': None, 'latest': None},
        'top_senders': {},
        'top_receivers': {},
        'public_transactions': 0,
        'private_transactions': 0
    }
    
    for tip in tips:
        # Transaction type
        if tip.get('type') == 'Tip Deposit':
            stats['deposits'] += 1
        elif tip.get('type') == 'Tip Withdraw':
            stats['withdrawals'] += 1
        
        # Currency analysis
        currency = tip.get('currency_code', 'Unknown')
        amount = tip.get('amount', 0)
        
        if currency not in stats['currencies']:
            stats['currencies'][currency] = 0
            stats['total_by_currency'][currency] = 0
        
        stats['currencies'][currency] += 1
        stats['total_by_currency'][currency] += amount
        
        # Date range
        issued_at = tip.get('issued_at')
        if issued_at:
            if not stats['date_range']['earliest'] or issued_at < stats['date_range']['earliest']:
                stats['date_range']['earliest'] = issued_at
            if not stats['date_range']['latest'] or issued_at > stats['date_range']['latest']:
                stats['date_range']['latest'] = issued_at
        
        # Sender/Receiver analysis
        sender = tip.get('sender_username')
        receiver = tip.get('receiver_username')
        
        if sender:
            stats['top_senders'][sender] = stats['top_senders'].get(sender, 0) + 1
        if receiver:
            stats['top_receivers'][receiver] = stats['top_receivers'].get(receiver, 0) + 1
        
        # Privacy
        if tip.get('is_public', True):
            stats['public_transactions'] += 1
        else:
            stats['private_transactions'] += 1
    
    # Sort top senders and receivers
    stats['top_senders'] = dict(sorted(stats['top_senders'].items(), key=lambda x: x[1], reverse=True)[:10])
    stats['top_receivers'] = dict(sorted(stats['top_receivers'].items(), key=lambda x: x[1], reverse=True)[:10])
    
    return stats

def main():
    input_file = 'tips.json'
    output_file = 'tips_consolidated.json'
    stats_file = 'tips_analysis.json'
    
    print("Extracting JSON objects from tips.json...")
    json_objects = extract_json_objects(input_file)
    print(f"Found {len(json_objects)} JSON objects")
    
    print("Consolidating tip data...")
    consolidated_data = consolidate_tip_data(json_objects)
    
    print("Analyzing tip data...")
    stats = analyze_tips(consolidated_data)
    
    # Save consolidated data
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(consolidated_data, f, indent=2, ensure_ascii=False)
    
    # Save analysis
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    
    print(f"\n=== CONSOLIDATION COMPLETE ===")
    print(f"Consolidated data saved to: {output_file}")
    print(f"Analysis saved to: {stats_file}")
    print(f"\n=== QUICK STATS ===")
    print(f"Total transactions: {stats['total_transactions']}")
    print(f"Deposits: {stats['deposits']}")
    print(f"Withdrawals: {stats['withdrawals']}")
    print(f"Currencies: {list(stats['currencies'].keys())}")
    print(f"Date range: {stats['date_range']['earliest']} to {stats['date_range']['latest']}")
    print(f"Public transactions: {stats['public_transactions']}")
    print(f"Private transactions: {stats['private_transactions']}")

if __name__ == "__main__":
    main()
