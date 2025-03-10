import csv
import io
from typing import List, Dict, Any

def validate_csv_headers(headers: List[str]) -> bool:
    """
    Validate that the CSV has at least the minimum required headers
    """
    required_headers = ['first_name']
    return all(header in headers for header in required_headers)

def parse_csv_file(file_stream) -> List[Dict[str, Any]]:
    """
    Parse a CSV file stream and return a list of dictionaries
    """
    # Decode the file stream
    stream = io.StringIO(file_stream.read().decode("UTF8"), newline=None)
    
    # Create a CSV reader
    reader = csv.DictReader(stream)
    
    # Validate headers
    if not validate_csv_headers(reader.fieldnames):
        raise ValueError("CSV file must contain at least a 'first_name' column")
    
    # Parse rows
    contacts = []
    for row in reader:
        # Skip rows without a first name
        if not row.get('first_name'):
            continue
        
        contacts.append({
            'first_name': row.get('first_name', ''),
            'last_name': row.get('last_name', ''),
            'email': row.get('email', ''),
            'phone': row.get('phone', ''),
            'address': row.get('address', ''),
            'notes': row.get('notes', '')
        })
    
    return contacts

def generate_csv_file(contacts: List[Dict[str, Any]]) -> io.BytesIO:
    """
    Generate a CSV file from a list of contact dictionaries
    """
    # Create a StringIO object
    output = io.StringIO()
    
    # Create a CSV writer
    writer = csv.writer(output)
    
    # Write headers
    writer.writerow(['first_name', 'last_name', 'email', 'phone', 'address', 'notes'])
    
    # Write data
    for contact in contacts:
        writer.writerow([
            contact.get('first_name', ''),
            contact.get('last_name', ''),
            contact.get('email', ''),
            contact.get('phone', ''),
            contact.get('address', ''),
            contact.get('notes', '')
        ])
    
    # Get the content as bytes
    output.seek(0)
    return io.BytesIO(output.getvalue().encode('utf-8')) 