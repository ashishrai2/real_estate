import json
import csv
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import matplotlib.pyplot as plt

class PropertyType(Enum):
    RESIDENTIAL = "Residential"
    COMMERCIAL = "Commercial"
    LAND = "Land"
    INDUSTRIAL = "Industrial"

class PropertyStatus(Enum):
    FOR_SALE = "For Sale"
    FOR_RENT = "For Rent"
    SOLD = "Sold"
    RENTED = "Rented"
    PENDING = "Pending"

class ClientType(Enum):
    BUYER = "Buyer"
    SELLER = "Seller"
    TENANT = "Tenant"
    LANDLORD = "Landlord"

@dataclass
class Property:
    """Class representing a real estate property"""
    property_id: str
    address: str
    city: str
    state: str
    zip_code: str
    property_type: PropertyType
    status: PropertyStatus
    price: float
    bedrooms: int
    bathrooms: float
    square_feet: int
    year_built: int
    description: str
    listing_date: str
    features: List[str]
    agent_id: Optional[str] = None

@dataclass
class Client:
    """Class representing a real estate client"""
    client_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    client_type: ClientType
    budget: float
    preferences: Dict
    interested_properties: List[str]
    notes: str

@dataclass
class Agent:
    """Class representing a real estate agent"""
    agent_id: str
    first_name: str
    last_name: str
    email: str
    phone: str
    commission_rate: float
    total_sales: float
    assigned_properties: List[str]

@dataclass
class Transaction:
    """Class representing a property transaction"""
    transaction_id: str
    property_id: str
    client_id: str
    agent_id: str
    transaction_type: str  # Sale, Rent
    amount: float
    date: str
    commission: float
    status: str  # Completed, Pending, Cancelled

class RealEstateManagementSystem:
    """Main system for managing real estate operations"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.properties: Dict[str, Property] = {}
        self.clients: Dict[str, Client] = {}
        self.agents: Dict[str, Agent] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.load_data()
    
    def load_data(self):
        """Load data from JSON files"""
        try:
            # Load properties
            with open(f"{self.data_dir}/properties.json", "r") as f:
                properties_data = json.load(f)
                for prop in properties_data:
                    prop['property_type'] = PropertyType(prop['property_type'])
                    prop['status'] = PropertyStatus(prop['status'])
                    self.properties[prop['property_id']] = Property(**prop)
        except FileNotFoundError:
            self.properties = {}
        
        try:
            # Load clients
            with open(f"{self.data_dir}/clients.json", "r") as f:
                clients_data = json.load(f)
                for client in clients_data:
                    client['client_type'] = ClientType(client['client_type'])
                    self.clients[client['client_id']] = Client(**client)
        except FileNotFoundError:
            self.clients = {}
    
    def save_data(self):
        """Save data to JSON files"""
        # Save properties
        properties_data = [asdict(prop) for prop in self.properties.values()]
        for prop in properties_data:
            prop['property_type'] = prop['property_type'].value
            prop['status'] = prop['status'].value
        
        with open(f"{self.data_dir}/properties.json", "w") as f:
            json.dump(properties_data, f, indent=2)
        
        # Save clients
        clients_data = [asdict(client) for client in self.clients.values()]
        for client in clients_data:
            client['client_type'] = client['client_type'].value
        
        with open(f"{self.data_dir}/clients.json", "w") as f:
            json.dump(clients_data, f, indent=2)
    
    def add_property(self, property_data: dict):
        """Add a new property to the system"""
        property_id = f"PROP{len(self.properties) + 1:04d}"
        property_data['property_id'] = property_id
        property_data['property_type'] = PropertyType(property_data['property_type'])
        property_data['status'] = PropertyStatus(property_data['status'])
        
        property = Property(**property_data)
        self.properties[property_id] = property
        self.save_data()
        print(f"Property added successfully! ID: {property_id}")
        return property_id
    
    def add_client(self, client_data: dict):
        """Add a new client to the system"""
        client_id = f"CLI{len(self.clients) + 1:04d}"
        client_data['client_id'] = client_id
        client_data['client_type'] = ClientType(client_data['client_type'])
        client_data['interested_properties'] = client_data.get('interested_properties', [])
        
        client = Client(**client_data)
        self.clients[client_id] = client
        self.save_data()
        print(f"Client added successfully! ID: {client_id}")
        return client_id
    
    def search_properties(self, **criteria) -> List[Property]:
        """Search properties based on criteria"""
        results = []
        for prop in self.properties.values():
            match = True
            
            for key, value in criteria.items():
                if hasattr(prop, key):
                    prop_value = getattr(prop, key)
                    if isinstance(prop_value, PropertyType) or isinstance(prop_value, PropertyStatus):
                        prop_value = prop_value.value
                    
                    if isinstance(value, str) and isinstance(prop_value, str):
                        if value.lower() not in prop_value.lower():
                            match = False
                            break
                    elif value != prop_value:
                        match = False
                        break
            
            if match:
                results.append(prop)
        
        return results
    
    def search_clients(self, **criteria) -> List[Client]:
        """Search clients based on criteria"""
        results = []
        for client in self.clients.values():
            match = True
            
            for key, value in criteria.items():
                if hasattr(client, key):
                    client_value = getattr(client, key)
                    if isinstance(client_value, ClientType):
                        client_value = client_value.value
                    
                    if isinstance(value, str) and isinstance(client_value, str):
                        if value.lower() not in client_value.lower():
                            match = False
                            break
                    elif value != client_value:
                        match = False
                        break
            
            if match:
                results.append(client)
        
        return results
    
    def update_property_status(self, property_id: str, new_status: PropertyStatus):
        """Update property status"""
        if property_id in self.properties:
            self.properties[property_id].status = new_status
            self.save_data()
            print(f"Property {property_id} status updated to {new_status.value}")
        else:
            print(f"Property {property_id} not found")
    
    def generate_property_report(self, filename: str = "property_report.csv"):
        """Generate a CSV report of all properties"""
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['ID', 'Address', 'City', 'Type', 'Status', 'Price', 'Bedrooms', 'Bathrooms', 'Square Feet']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for prop in self.properties.values():
                writer.writerow({
                    'ID': prop.property_id,
                    'Address': prop.address,
                    'City': prop.city,
                    'Type': prop.property_type.value,
                    'Status': prop.status.value,
                    'Price': f"${prop.price:,.2f}",
                    'Bedrooms': prop.bedrooms,
                    'Bathrooms': prop.bathrooms,
                    'Square Feet': f"{prop.square_feet:,}"
                })
        
        print(f"Report generated: {filename}")
    
    def analyze_market_trends(self):
        """Analyze property market trends"""
        if not self.properties:
            print("No properties available for analysis")
            return
        
        # Calculate average prices by property type
        type_prices = {}
        type_counts = {}
        
        for prop in self.properties.values():
            prop_type = prop.property_type.value
            if prop_type not in type_prices:
                type_prices[prop_type] = 0
                type_counts[prop_type] = 0
            
            type_prices[prop_type] += prop.price
            type_counts[prop_type] += 1
        
        print("\n=== MARKET ANALYSIS ===")
        for prop_type in type_prices:
            avg_price = type_prices[prop_type] / type_counts[prop_type]
            print(f"{prop_type}: {type_counts[prop_type]} properties, Average Price: ${avg_price:,.2f}")
        
        # Price distribution
        prices = [prop.price for prop in self.properties.values()]
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        print(f"\nOverall Statistics:")
        print(f"Total Properties: {len(self.properties)}")
        print(f"Average Price: ${avg_price:,.2f}")
        print(f"Minimum Price: ${min_price:,.2f}")
        print(f"Maximum Price: ${max_price:,.2f}")
    
    def calculate_mortgage(self, property_price: float, down_payment: float, 
                          interest_rate: float, loan_term: int) -> Dict:
        """Calculate monthly mortgage payments"""
        loan_amount = property_price - down_payment
        monthly_rate = interest_rate / 100 / 12
        num_payments = loan_term * 12
        
        if monthly_rate > 0:
            monthly_payment = loan_amount * (
                monthly_rate * (1 + monthly_rate) ** num_payments
            ) / ((1 + monthly_rate) ** num_payments - 1)
        else:
            monthly_payment = loan_amount / num_payments
        
        total_payment = monthly_payment * num_payments
        total_interest = total_payment - loan_amount
        
        return {
            'loan_amount': loan_amount,
            'monthly_payment': monthly_payment,
            'total_payment': total_payment,
            'total_interest': total_interest
        }
    
    def match_clients_to_properties(self):
        """Match clients with suitable properties based on preferences"""
        matches = {}
        
        for client in self.clients.values():
            if client.client_type == ClientType.BUYER:
                suitable_properties = []
                budget = client.budget
                preferences = client.preferences
                
                for prop in self.properties.values():
                    if prop.status in [PropertyStatus.FOR_SALE, PropertyStatus.PENDING]:
                        # Check if property fits budget
                        if prop.price <= budget * 1.1:  # Allow 10% over budget
                            match_score = 0
                            
                            # Check preferences
                            if 'property_type' in preferences:
                                if prop.property_type.value == preferences['property_type']:
                                    match_score += 30
                            
                            if 'bedrooms' in preferences:
                                if prop.bedrooms >= preferences['bedrooms']:
                                    match_score += 25
                            
                            if 'city' in preferences:
                                if preferences['city'].lower() in prop.city.lower():
                                    match_score += 20
                            
                            if 'max_price' in preferences:
                                if prop.price <= preferences['max_price']:
                                    match_score += 15
                            
                            if match_score >= 40:  # Minimum threshold
                                suitable_properties.append({
                                    'property': prop,
                                    'match_score': match_score
                                })
                
                # Sort by match score
                suitable_properties.sort(key=lambda x: x['match_score'], reverse=True)
                matches[client.client_id] = suitable_properties[:5]  # Top 5 matches
        
        return matches

class RealEstateApp:
    """Command-line interface for the Real Estate Management System"""
    
    def __init__(self):
        self.system = RealEstateManagementSystem()
    
    def display_menu(self):
        """Display main menu"""
        print("\n=== REAL ESTATE MANAGEMENT SYSTEM ===")
        print("1. Add Property")
        print("2. Add Client")
        print("3. Search Properties")
        print("4. Search Clients")
        print("5. Update Property Status")
        print("6. Generate Reports")
        print("7. Market Analysis")
        print("8. Mortgage Calculator")
        print("9. Client-Property Matching")
        print("10. Exit")
    
    def add_property_interactive(self):
        """Interactive property addition"""
        print("\n--- Add New Property ---")
        property_data = {
            'address': input("Address: "),
            'city': input("City: "),
            'state': input("State: "),
            'zip_code': input("ZIP Code: "),
            'property_type': input("Property Type (Residential/Commercial/Land/Industrial): ").title(),
            'status': input("Status (For Sale/For Rent/Sold/Rented/Pending): ").title(),
            'price': float(input("Price: $")),
            'bedrooms': int(input("Bedrooms: ")),
            'bathrooms': float(input("Bathrooms: ")),
            'square_feet': int(input("Square Feet: ")),
            'year_built': int(input("Year Built: ")),
            'description': input("Description: "),
            'listing_date': datetime.now().strftime("%Y-%m-%d"),
            'features': input("Features (comma-separated): ").split(',')
        }
        
        self.system.add_property(property_data)
    
    def add_client_interactive(self):
        """Interactive client addition"""
        print("\n--- Add New Client ---")
        client_data = {
            'first_name': input("First Name: "),
            'last_name': input("Last Name: "),
            'email': input("Email: "),
            'phone': input("Phone: "),
            'client_type': input("Client Type (Buyer/Seller/Tenant/Landlord): ").title(),
            'budget': float(input("Budget: $")),
            'preferences': {
                'property_type': input("Preferred Property Type: ").title(),
                'bedrooms': int(input("Minimum Bedrooms: ")),
                'city': input("Preferred City: ")
            },
            'notes': input("Notes: ")
        }
        
        self.system.add_client(client_data)
    
    def search_properties_interactive(self):
        """Interactive property search"""
        print("\n--- Search Properties ---")
        print("Enter search criteria (press Enter to skip)")
        
        criteria = {}
        fields = ['city', 'property_type', 'status', 'bedrooms', 'min_price', 'max_price']
        
        for field in fields:
            value = input(f"{field.replace('_', ' ').title()}: ")
            if value:
                if field in ['bedrooms']:
                    criteria[field] = int(value)
                elif field in ['min_price', 'max_price']:
                    criteria['price_range'] = criteria.get('price_range', (0, float('inf')))
                    if field == 'min_price':
                        criteria['price_range'] = (float(value), criteria['price_range'][1])
                    else:
                        criteria['price_range'] = (criteria['price_range'][0], float(value))
                else:
                    criteria[field] = value
        
        # Custom filtering for price range
        results = self.system.search_properties(**{k: v for k, v in criteria.items() 
                                                  if k not in ['min_price', 'max_price']})
        
        if 'price_range' in criteria:
            min_price, max_price = criteria['price_range']
            results = [p for p in results if min_price <= p.price <= max_price]
        
        if results:
            print(f"\nFound {len(results)} properties:")
            for prop in results:
                print(f"\nID: {prop.property_id}")
                print(f"Address: {prop.address}, {prop.city}")
                print(f"Type: {prop.property_type.value} | Status: {prop.status.value}")
                print(f"Price: ${prop.price:,.2f} | {prop.bedrooms} BR | {prop.bathrooms} BA")
                print(f"Square Feet: {prop.square_feet:,}")
        else:
            print("No properties found matching your criteria.")
    
    def run(self):
        """Run the application"""
        while True:
            self.display_menu()
            choice = input("\nEnter your choice (1-10): ")
            
            if choice == '1':
                self.add_property_interactive()
            elif choice == '2':
                self.add_client_interactive()
            elif choice == '3':
                self.search_properties_interactive()
            elif choice == '4':
                self.search_clients_interactive()
            elif choice == '5':
                self.update_property_status_interactive()
            elif choice == '6':
                self.system.generate_property_report()
            elif choice == '7':
                self.system.analyze_market_trends()
            elif choice == '8':
                self.mortgage_calculator_interactive()
            elif choice == '9':
                self.client_matching_interactive()
            elif choice == '10':
                print("Thank you for using Real Estate Management System!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def search_clients_interactive(self):
        """Interactive client search"""
        print("\n--- Search Clients ---")
        criteria = {}
        name = input("Client Name (or part of name): ")
        if name:
            results = [c for c in self.system.clients.values() 
                      if name.lower() in f"{c.first_name} {c.last_name}".lower()]
        else:
            results = list(self.system.clients.values())
        
        if results:
            print(f"\nFound {len(results)} clients:")
            for client in results:
                print(f"\nID: {client.client_id}")
                print(f"Name: {client.first_name} {client.last_name}")
                print(f"Type: {client.client_type.value} | Budget: ${client.budget:,.2f}")
                print(f"Email: {client.email} | Phone: {client.phone}")
        else:
            print("No clients found.")
    
    def update_property_status_interactive(self):
        """Interactive property status update"""
        print("\n--- Update Property Status ---")
        prop_id = input("Property ID: ")
        
        if prop_id in self.system.properties:
            print(f"Current Status: {self.system.properties[prop_id].status.value}")
            new_status = input("New Status (For Sale/For Rent/Sold/Rented/Pending): ").title()
            
            try:
                status_enum = PropertyStatus(new_status)
                self.system.update_property_status(prop_id, status_enum)
            except ValueError:
                print("Invalid status entered.")
        else:
            print("Property not found.")
    
    def mortgage_calculator_interactive(self):
        """Interactive mortgage calculator"""
        print("\n--- Mortgage Calculator ---")
        property_price = float(input("Property Price: $"))
        down_payment = float(input("Down Payment: $"))
        interest_rate = float(input("Annual Interest Rate (%): "))
        loan_term = int(input("Loan Term (years): "))
        
        result = self.system.calculate_mortgage(property_price, down_payment, interest_rate, loan_term)
        
        print(f"\n=== MORTGAGE CALCULATION ===")
        print(f"Loan Amount: ${result['loan_amount']:,.2f}")
        print(f"Monthly Payment: ${result['monthly_payment']:,.2f}")
        print(f"Total Payment: ${result['total_payment']:,.2f}")
        print(f"Total Interest: ${result['total_interest']:,.2f}")
    
    def client_matching_interactive(self):
        """Interactive client-property matching"""
        print("\n--- Client-Property Matching ---")
        matches = self.system.match_clients_to_properties()
        
        for client_id, properties in matches.items():
            client = self.system.clients[client_id]
            print(f"\n=== Matches for {client.first_name} {client.last_name} ===")
            
            if properties:
                for match in properties:
                    prop = match['property']
                    score = match['match_score']
                    print(f"\nProperty: {prop.address}")
                    print(f"Score: {score}/100")
                    print(f"Price: ${prop.price:,.2f} | Type: {prop.property_type.value}")
                    print(f"Bedrooms: {prop.bedrooms} | Bathrooms: {prop.bathrooms}")
            else:
                print("No suitable properties found.")
        
        if not matches:
            print("No buyer clients found for matching.")

# Sample data initialization
def initialize_sample_data():
    """Initialize the system with sample data"""
    sample_properties = [
        {
            "property_id": "PROP0001",
            "address": "123 Main St",
            "city": "New York",
            "state": "NY",
            "zip_code": "10001",
            "property_type": "Residential",
            "status": "For Sale",
            "price": 750000.00,
            "bedrooms": 3,
            "bathrooms": 2.5,
            "square_feet": 2200,
            "year_built": 2010,
            "description": "Beautiful modern townhouse",
            "listing_date": "2024-01-15",
            "features": ["Garage", "Garden", "Pool"]
        },
        {
            "property_id": "PROP0002",
            "address": "456 Oak Ave",
            "city": "Los Angeles",
            "state": "CA",
            "zip_code": "90001",
            "property_type": "Commercial",
            "status": "For Rent",
            "price": 5000.00,
            "bedrooms": 0,
            "bathrooms": 2.0,
            "square_feet": 1500,
            "year_built": 2015,
            "description": "Prime commercial space",
            "listing_date": "2024-01-10",
            "features": ["Parking", "Security", "AC"]
        }
    ]
    
    sample_clients = [
        {
            "client_id": "CLI0001",
            "first_name": "John",
            "last_name": "Doe",
            "email": "john@example.com",
            "phone": "555-0101",
            "client_type": "Buyer",
            "budget": 800000.00,
            "preferences": {
                "property_type": "Residential",
                "bedrooms": 3,
                "city": "New York"
            },
            "interested_properties": ["PROP0001"],
            "notes": "Looking for family home"
        }
    ]
    
    # Create data directory if it doesn't exist
    import os
    os.makedirs("data", exist_ok=True)
    
    # Save sample data
    with open("data/properties.json", "w") as f:
        json.dump(sample_properties, f, indent=2)
    
    with open("data/clients.json", "w") as f:
        json.dump(sample_clients, f, indent=2)
    
    print("Sample data initialized successfully!")

# Additional utility functions
def create_listing_template():
    """Create a property listing template"""
    template = {
        "address": "",
        "city": "",
        "state": "",
        "zip_code": "",
        "property_type": "Residential",  # Options: Residential, Commercial, Land, Industrial
        "status": "For Sale",  # Options: For Sale, For Rent, Sold, Rented, Pending
        "price": 0.0,
        "bedrooms": 0,
        "bathrooms": 0.0,
        "square_feet": 0,
        "year_built": 0,
        "description": "",
        "listing_date": datetime.now().strftime("%Y-%m-%d"),
        "features": []
    }
    return template

def calculate_property_value(property_data: dict, comps: List[dict]) -> float:
    """Calculate property value using comparable sales"""
    if not comps:
        return property_data.get('price', 0)
    
    # Simple average of comparable properties
    total_price = sum(comp['price'] for comp in comps)
    avg_price = total_price / len(comps)
    
    # Adjust for property features
    adjustments = 0
    base_features = ['Garage', 'Pool', 'Renovated']
    
    for feature in base_features:
        if feature in property_data.get('features', []):
            adjustments += property_data.get('price', 0) * 0.05  # 5% per feature
    
    return avg_price + adjustments

# Main execution
if __name__ == "__main__":
    # Initialize with sample data (comment out if you want empty system)
    initialize_sample_data()
    
    # Run the application
    app = RealEstateApp()
    app.run()
