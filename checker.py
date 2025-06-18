import requests
import json
import time
from typing import Dict, Any

def check_stx_balances(address_dict: Dict[str, str], min_balance: float = 5.0) -> Dict[str, Dict[str, Any]]:
    """
    Checks the STX balance for a dictionary of name-address pairs and returns those with balances greater than the minimum.
    
    Args:
        address_dict: Dictionary with names as keys and Stacks wallet addresses as values
        min_balance: Minimum balance threshold in STX (default: 5.0)
        
    Returns:
        Dictionary with names as keys and a dict containing address and balance as values, for those exceeding the threshold
    """
    # Base URL for Stacks API
    base_url = "https://stacks-node-api.mainnet.stacks.co/extended/v1/address/"
    
    # Dictionary to store results
    qualifying_addresses = {}
    
    print(f"Checking {len(address_dict)} addresses for balances greater than {min_balance} STX...")
    
    for i, (name, address) in enumerate(address_dict.items()):
        try:
            # Clean the address - remove any quotes and whitespace
            clean_address = address.strip().replace('"', '').replace("'", '')
            
            # Format the API request URL
            url = f"{base_url}{clean_address}"
            
            # Make the API request
            response = requests.get(url)
            
            # Check if the request was successful
            if response.status_code == 200:
                data = response.json()
                
                # Extract the balance - convert from hex if needed
                balance_str = data.get('balance', '0')
                
                # Check if the balance is in hex format
                if isinstance(balance_str, str) and balance_str.startswith('0x'):
                    # Convert hex to decimal
                    balance_micro_stx = int(balance_str, 16)
                else:
                    # Already in decimal or different format
                    balance_micro_stx = int(balance_str)
                
                balance_stx = balance_micro_stx / 1_000_000
                
                print(f"Name: {name}, Address: {clean_address}, Balance: {balance_stx} STX")
                
                # Check if the balance is greater than the minimum
                if balance_stx > min_balance:
                    qualifying_addresses[name] = {
                        "address": clean_address,
                        "balance": balance_stx
                    }
                    print(f"Found qualifying address for {name}: {clean_address} with {balance_stx} STX")
            else:
                # Try alternative API endpoint if the first one fails
                fallback_url = f"https://stacks-node-api.mainnet.stacks.co/v2/accounts/{clean_address}"
                fallback_response = requests.get(fallback_url)
                
                if fallback_response.status_code == 200:
                    fallback_data = fallback_response.json()
                    
                    # Extract the balance - convert from hex if needed
                    balance_str = fallback_data.get('balance', '0')
                    
                    # Check if the balance is in hex format
                    if isinstance(balance_str, str) and balance_str.startswith('0x'):
                        # Convert hex to decimal
                        balance_micro_stx = int(balance_str, 16)
                    else:
                        # Already in decimal or different format
                        balance_micro_stx = int(balance_str)
                    
                    balance_stx = balance_micro_stx / 1_000_000
                    
                    print(f"Name: {name}, Address (fallback): {clean_address}, Balance: {balance_stx} STX")
                    
                    if balance_stx > min_balance:
                        qualifying_addresses[name] = {
                            "address": clean_address,
                            "balance": balance_stx
                        }
                        print(f"Found qualifying address for {name}: {clean_address} with {balance_stx} STX")
                else:
                    print(f"Failed to get balance for {name} ({clean_address}): HTTP {response.status_code}")
            
            # Add a small delay to avoid rate limiting
            if i > 0 and i % 5 == 0:
                print(f"Processed {i} addresses so far...")
                time.sleep(1)
                
        except Exception as e:
            print(f"Error processing address for {name} ({address}): {str(e)}")
            continue
    
    print(f"Found {len(qualifying_addresses)} addresses with more than {min_balance} STX")
    return qualifying_addresses

def main():
    # Load address dictionary from a JSON file
    try:
        with open('stacks_addresses.json', 'r') as file:
            address_dict = json.load(file)
    except FileNotFoundError:
        print("Error: stacks_addresses.json file not found")
        print("Please create a JSON file named stacks_addresses.json with names as keys and addresses as values")
        return
    except json.JSONDecodeError:
        print("Error: stacks_addresses.json is not a valid JSON file")
        return
    
    print(f"Loaded {len(address_dict)} name-address pairs from file")
    print("Sample of loaded data:")
    sample_items = list(address_dict.items())[:3] if len(address_dict) > 3 else list(address_dict.items())
    for name, address in sample_items:
        print(f"  {name}: {address}")
    
    # Set the minimum balance threshold (default is 5 STX)
    min_balance = 5.0
    
    # Check balances and get qualifying addresses
    qualifying_addresses = check_stx_balances(address_dict, min_balance)
    
    # Save results to a file
    with open('qualifying_addresses.json', 'w') as file:
        json.dump(qualifying_addresses, file, indent=2)
    
    print(f"Results saved to qualifying_addresses.json")
    
    # Also print the results to console
    if qualifying_addresses:
        print("\nQualifying addresses and their balances:")
        for name, data in qualifying_addresses.items():
            print(f"{name}: {data['address']} - {data['balance']} STX")
    else:
        print("No addresses found with balances greater than the minimum threshold.")

if _name_ == "_main_":
    main()