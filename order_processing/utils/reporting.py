"""
Reporting utility module for the order processing application.
"""
import os
import csv
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from ..models.order import Order
from ..models.payment import Payment
from ..models.customer import Customer
from ..models.product import Product

class ReportGenerator:
    """Class for generating and exporting reports."""
    
    @staticmethod
    def get_sales_data(start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get sales data for a date range.
        
        Args:
            start_date: Start date for the report
            end_date: End date for the report
            
        Returns:
            List of dictionaries containing sales data
        """
        # Get orders in the date range
        orders = Order.find_by_date_range(start_date, end_date)
        
        # Prepare data
        sales_data = []
        for order in orders:
            # Only include completed orders
            if order.status != Order.STATUS_COMPLETED:
                continue
                
            # Get customer
            customer = Customer.find_by_id(order.customer_id) if order.customer_id else None
            customer_name = customer.name if customer else "Unknown"
            
            # Get payment
            payments = Payment.find_by_order_id(order.order_id)
            payment_type = payments[0].payment_type if payments else "Unknown"
            
            # Get order items
            order_items = order.get_items()
            item_count = len(order_items)
            
            # Add to sales data
            sales_data.append({
                "order_id": order.order_id,
                "date": order.order_date,
                "customer": customer_name,
                "items": item_count,
                "total": order.total_cost,
                "payment_type": payment_type
            })
        
        return sales_data
    
    @classmethod
    def generate_daily_report(cls, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Generate a daily sales report.
        
        Args:
            date: The date for the report (defaults to today)
            
        Returns:
            List of dictionaries containing daily sales data
        """
        date = date or datetime.now()
        start_date = datetime(date.year, date.month, date.day, 0, 0, 0)
        end_date = datetime(date.year, date.month, date.day, 23, 59, 59)
        
        return cls.get_sales_data(start_date, end_date)
    
    @classmethod
    def generate_weekly_report(cls, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Generate a weekly sales report.
        
        Args:
            date: A date within the week for the report (defaults to today)
            
        Returns:
            List of dictionaries containing weekly sales data
        """
        date = date or datetime.now()
        # Find the start of the week (Monday)
        start_date = date - timedelta(days=date.weekday())
        start_date = datetime(start_date.year, start_date.month, start_date.day, 0, 0, 0)
        # End of the week (Sunday)
        end_date = start_date + timedelta(days=6)
        end_date = datetime(end_date.year, end_date.month, end_date.day, 23, 59, 59)
        
        return cls.get_sales_data(start_date, end_date)
    
    @classmethod
    def generate_monthly_report(cls, date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """Generate a monthly sales report.
        
        Args:
            date: A date within the month for the report (defaults to today)
            
        Returns:
            List of dictionaries containing monthly sales data
        """
        date = date or datetime.now()
        # First day of the month
        start_date = datetime(date.year, date.month, 1, 0, 0, 0)
        # Last day of the month
        if date.month == 12:
            end_date = datetime(date.year + 1, 1, 1, 0, 0, 0) - timedelta(seconds=1)
        else:
            end_date = datetime(date.year, date.month + 1, 1, 0, 0, 0) - timedelta(seconds=1)
        
        return cls.get_sales_data(start_date, end_date)
    
    @staticmethod
    def export_to_csv(data: List[Dict[str, Any]], filepath: str) -> bool:
        """Export data to a CSV file.
        
        Args:
            data: List of dictionaries containing report data
            filepath: Path to save the CSV file
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Format dates
            formatted_data = []
            for record in data:
                record_copy = record.copy()
                if isinstance(record_copy.get("date"), datetime):
                    record_copy["date"] = record_copy["date"].strftime("%Y-%m-%d %H:%M:%S")
                formatted_data.append(record_copy)
            
            # Write to CSV
            if formatted_data:
                with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=formatted_data[0].keys())
                    writer.writeheader()
                    writer.writerows(formatted_data)
                return True
            return False
        except Exception as e:
            print(f"CSV export failed: {e}")
            return False
    
    @staticmethod
    def export_to_pdf(data: List[Dict[str, Any]], filepath: str, title: str) -> bool:
        """Export data to a PDF file.
        
        Args:
            data: List of dictionaries containing report data
            filepath: Path to save the PDF file
            title: Title for the report
            
        Returns:
            True if export was successful, False otherwise
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Format dates
            formatted_data = []
            for record in data:
                record_copy = record.copy()
                if isinstance(record_copy.get("date"), datetime):
                    record_copy["date"] = record_copy["date"].strftime("%Y-%m-%d %H:%M:%S")
                formatted_data.append(record_copy)
            
            if not formatted_data:
                return False
            
            # Create PDF document
            doc = SimpleDocTemplate(filepath, pagesize=letter)
            elements = []
            
            # Add styles
            styles = getSampleStyleSheet()
            title_style = styles['Heading1']
            
            # Add title
            elements.append(Paragraph(title, title_style))
            elements.append(Spacer(1, 12))
            
            # Add table
            headers = list(formatted_data[0].keys())
            table_data = [headers]
            for record in formatted_data:
                row = [str(record[header]) for header in headers]
                table_data.append(row)
            
            table = Table(table_data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Build PDF
            doc.build(elements)
            return True
        except Exception as e:
            print(f"PDF export failed: {e}")
            return False
    
    @staticmethod
    def generate_product_stock_report() -> List[Dict[str, Any]]:
        """Generate a product stock report.
        
        Returns:
            List of dictionaries containing product stock data
        """
        products = Product.find_all()
        return [
            {
                "product_id": product.product_id,
                "name": product.name,
                "sku": product.sku,
                "price": product.price,
                "stock_quantity": product.stock_quantity
            }
            for product in products
        ]
    
    @staticmethod
    def generate_low_stock_report(threshold: int = 10) -> List[Dict[str, Any]]:
        """Generate a report of products with low stock.
        
        Args:
            threshold: Stock quantity threshold
            
        Returns:
            List of dictionaries containing low stock product data
        """
        products = Product.find_low_stock(threshold)
        return [
            {
                "product_id": product.product_id,
                "name": product.name,
                "sku": product.sku,
                "price": product.price,
                "stock_quantity": product.stock_quantity
            }
            for product in products
        ]