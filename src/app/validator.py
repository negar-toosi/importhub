
from decimal import Decimal, InvalidOperation
from typing import Optional
from src.app.utils.enums import ShipmentStatus
import pandas as pd

class ShipmentRecordValidator:
    def shipment_code(shipment_code: Optional[str]):
        if type(shipment_code) is None or pd.NA:
            return "shipment code is null"
        if type(shipment_code) != str:
            return "shipment code is not a string object"
        
    def customer_name(customer_name: Optional[str]):
        if type(customer_name) is None:
            return "customer name is null"
        if type(customer_name) != str:
            return "customer name is not a string object"
        if len(customer_name) > 50:
            return "maximum charecter for customer name must be 50"
        
    def origin_city(origin_city: Optional[str]):
        if type(origin_city) is None:
            return "origin city is null"
        if type(origin_city) != str:
            return "origin city is not a string object"
        
    def destination_city(destination_city: Optional[str]):
        if type(destination_city) is None:
            return "destination city is null"
        if type(destination_city) != str:
            return "destination city is not a string object"
    
    def weight_kg(value) -> Optional[str]:
        if value is None:
            return "weight_kg is null"
        if not isinstance(value, (int, float, Decimal)):
            return "weight_kg is not a decimal number"
        try:
            d = Decimal(str(value))
        except InvalidOperation:
            return "weight_kg is not a valid decimal number"
        if d <= 0:
            return "weight_kg must be greater than 0"
        _, digits, exponent = d.as_tuple()
        decimal_places = max(0, -exponent)
        total_digits = len(digits)
        if decimal_places > 3:
            return "weight_kg must have at most 3 decimal places"
        if total_digits > 10:
            return "weight_kg must have at most 10 digits"
    
    def price(value) -> Optional[str]:
        if value is None:
            return "weight_kg is null"
        if not isinstance(value, (int, float, Decimal)):
            return "weight_kg is not a decimal number"
        try:
            d = Decimal(str(value))
        except InvalidOperation:
            return "weight_kg is not a valid decimal number"
        if d < 0:
            return "weight_kg must be greater than 0"
        _, digits, exponent = d.as_tuple()
        decimal_places = max(0, -exponent)
        total_digits = len(digits)
        if decimal_places > 3:
            return "weight_kg must have at most 3 decimal places"
        if total_digits > 10:
            return "weight_kg must have at most 10 digits"
    
    def status(value) -> Optional[str]:
        if value is None:
            return "status is null"
        if value not in ShipmentStatus._value2member_map_:
            return f"status must be one of: {', '.join(s.value for s in ShipmentStatus)}"

