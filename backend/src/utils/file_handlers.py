"""
File Handling Utilities

This module contains functions for handling file I/O operations,
particularly for generating and saving campaign outputs.
"""

import os
from datetime import datetime


def create_campaign_website(result, filename="campaign_website.html"):
    """
    Generate and save a campaign presentation website from workflow results.
    
    Args:
        result: Workflow result containing artifacts
        filename: Output filename (default: "campaign_website.html")
        
    Features:
    - Automatic directory creation
    - HTML validation and cleanup
    - Comprehensive statistics reporting
    - Error handling and fallbacks
    """
    # Try to get validated HTML first, fall back to original if not available
    html_validation = result.get('artifacts', {}).get('html_validation', {})
    
    if html_validation and html_validation.get('status') in ['success', 'warning']:
        campaign_website_content = html_validation.get('corrected_html', '')
        validation_used = True
        print("🔍 Using validated and corrected HTML")
    else:
        # Try multiple paths to find the HTML content
        campaign_website_content = (
            result.get('web_developer', {}).get('campaign_website', '') or
            result.get('artifacts', {}).get('web_developer', {}).get('campaign_website', '') or
            ''
        )
        validation_used = False
        print("⚠️ Using original HTML (validation not available)")
    
    if campaign_website_content:
        try:
            # Create outputs directory if it doesn't exist
            outputs_dir = "outputs"
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir)
                print(f"📁 Created {outputs_dir} directory")
            
            # Add timestamp to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(outputs_dir, filename)
            
            # Basic validation if not already validated
            if not validation_used:
                # Ensure proper HTML structure
                if not campaign_website_content.strip().find('<!DOCTYPE html>') == -1:
                    print("⚠️ Warning: Adding missing DOCTYPE declaration")
                    campaign_website_content = '<!DOCTYPE html>\n' + campaign_website_content
                
                if '<html' not in campaign_website_content:
                    campaign_website_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Campaign Presentation</title>
</head>
<body>
{campaign_website_content}
</body>
</html>"""
            
            # Clean up any code block markers that might be in the content
            campaign_website_content = campaign_website_content.replace('```html', '').replace('```', '')
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(campaign_website_content)
            
            # Calculate content statistics
            content_length = len(campaign_website_content)
            sections_count = campaign_website_content.count('<section') + campaign_website_content.count('<div class="section')
            cta_count = campaign_website_content.count('button') + campaign_website_content.count('cta')
            presentation_elements = campaign_website_content.count('presentation') + campaign_website_content.count('campaign')
            visual_elements = campaign_website_content.count('img') + campaign_website_content.count('image') + campaign_website_content.count('visual')
            
            print(f"✅ Comprehensive campaign presentation website saved as {filepath}")
            print(f"📊 Website Statistics:")
            print(f"   - Content Length: {content_length:,} characters")
            print(f"   - Sections: {sections_count}")
            print(f"   - Interactive Elements: {cta_count}")
            print(f"   - Presentation Elements: {presentation_elements}")
            print(f"   - Visual Elements: {visual_elements}")
            print(f"   - Campaign Data Used: {len(result.get('artifacts', {}))} artifacts")
            print(f"   - HTML Validation: {'✅ Validated & Corrected' if validation_used else '⚠️ Basic validation only'}")
            
            # Check for image integration
            if result.get('artifacts', {}).get('visual', {}).get('image_url'):
                print(f"   - 🎨 Visual Concepts: Image integrated prominently")
            else:
                print(f"   - ⚠️ Visual Concepts: No image URL found")
            
            # Display validation results if available
            if validation_used and html_validation:
                print(f"   - 🔍 Validation Summary: {html_validation.get('validation_summary', 'N/A')}")
                if html_validation.get('original_issues'):
                    print(f"   - 🔧 Issues Fixed: {len(html_validation.get('original_issues', []))}")
                if html_validation.get('corrected_issues'):
                    print(f"   - ⚠️ Remaining Issues: {len(html_validation.get('corrected_issues', []))}")
            
        except Exception as e:
            print(f"❌ Failed to save campaign website: {e}")
    else:
        print("❌ No campaign website content found in artifacts")


def save_campaign_pdf(content, filename="campaign_report.pdf"):
    """
    Save campaign PDF content to file.
    
    Args:
        content: PDF content to save
        filename: Output filename (default: "campaign_report.pdf")
    """
    try:
        # Create outputs directory if it doesn't exist
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            os.makedirs(outputs_dir)
        
        # Add timestamp to filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{filename}"
        filepath = os.path.join(outputs_dir, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Campaign PDF report saved as {filepath}")
        
    except Exception as e:
        print(f"❌ Failed to save campaign PDF: {e}")


def download_image(url, filename="generated_ad.png"):
    """
    Download image from URL and save to outputs directory.
    
    Args:
        url: Image URL to download
        filename: Output filename (default: "generated_ad.png")
    """
    try:
        import requests
        
        response = requests.get(url)
        if response.status_code == 200:
            # Create outputs directory if it doesn't exist
            outputs_dir = "outputs"
            if not os.path.exists(outputs_dir):
                os.makedirs(outputs_dir)
            
            # Add timestamp to filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{filename}"
            filepath = os.path.join(outputs_dir, filename)
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            print(f"✅ Image saved to {filepath}")
        else:
            print("❌ Failed to download image")
            
    except Exception as e:
        print(f"❌ Error downloading image: {e}")


def clean_output_directory(max_files=10):
    """
    Clean up old files in outputs directory, keeping only the most recent ones.
    
    Args:
        max_files: Maximum number of files to keep per type
    """
    try:
        outputs_dir = "outputs"
        if not os.path.exists(outputs_dir):
            return
        
        # Get all files in outputs directory
        files = []
        for filename in os.listdir(outputs_dir):
            filepath = os.path.join(outputs_dir, filename)
            if os.path.isfile(filepath):
                files.append((filepath, os.path.getmtime(filepath)))
        
        # Sort by modification time (newest first)
        files.sort(key=lambda x: x[1], reverse=True)
        
        # Keep only the most recent files
        if len(files) > max_files:
            for filepath, _ in files[max_files:]:
                os.remove(filepath)
                print(f"🗑️ Removed old file: {os.path.basename(filepath)}")
        
    except Exception as e:
        print(f"❌ Error cleaning output directory: {e}") 