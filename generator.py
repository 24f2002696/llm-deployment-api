import google.generativeai as genai
import os
import base64
import json

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def generate_app(brief, checks, attachments, task, round_num):
    """Generate app files using Gemini"""
    
    # Decode attachments
    decoded_attachments = []
    for att in attachments:
        name = att['name']
        data_uri = att['url']
        # Parse data URI
        if data_uri.startswith('data:'):
            parts = data_uri.split(',', 1)
            if len(parts) == 2:
                content = base64.b64decode(parts[1]).decode('utf-8', errors='ignore')
                decoded_attachments.append({"name": name, "content": content})
    
    # Build prompt for Gemini
    prompt = f"""You are an expert web developer. Create a complete, functional single-page web application.

TASK: {brief}

CHECKS TO PASS:
{json.dumps(checks, indent=2)}

ATTACHMENTS:
{json.dumps(decoded_attachments, indent=2)}

REQUIREMENTS:
1. Create a single index.html file with embedded CSS and JavaScript
2. Use CDN links for any libraries (Bootstrap, marked, highlight.js, etc.)
3. Ensure all checks will pass when the page loads
4. Make it production-ready with proper error handling
5. Add comments explaining key sections
6. Make it visually appealing with Bootstrap styling

Return ONLY valid HTML. Start with <!DOCTYPE html> and end with </html>.
Do NOT include markdown code blocks or explanations."""

    try:
        # Try gemini-2.0-flash first
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
    except Exception as e:
        print(f"gemini-2.0-flash failed: {e}, trying gemini-1.5-pro...")
        try:
            # Fall back to gemini-1.5-pro
            model = genai.GenerativeModel('gemini-1.5-pro')
            response = model.generate_content(prompt)
        except Exception as e2:
            print(f"gemini-1.5-pro failed: {e2}, trying gemini-pro...")
            # Last resort - use gemini-pro
            model = genai.GenerativeModel('gemini-pro')
            response = model.generate_content(prompt)
    
    html_content = response.text.strip()
    
    # Clean up response if it has markdown code blocks
    if html_content.startswith('```'):
        lines = html_content.split('\n')
        html_content = '\n'.join(lines[1:-1])
    
    # Generate README
    readme_prompt = f"""Create a professional README.md for this project:

TASK: {brief}
CHECKS: {json.dumps(checks, indent=2)}

Include these sections:
1. Project Title and Description
2. Features
3. Setup Instructions
4. Usage Guide
5. Code Explanation (brief technical overview)
6. License (MIT)

Make it clear, professional, and well-formatted in Markdown."""

    try:
        readme_model = genai.GenerativeModel('gemini-2.0-flash')
        readme_response = readme_model.generate_content(readme_prompt)
    except:
        try:
            readme_model = genai.GenerativeModel('gemini-1.5-pro')
            readme_response = readme_model.generate_content(readme_prompt)
        except:
            readme_model = genai.GenerativeModel('gemini-pro')
            readme_response = readme_model.generate_content(readme_prompt)
    
    readme_content = readme_response.text.strip()
    
    # Prepare files
    files = {
        'index.html': html_content,
        'README.md': readme_content,
        'LICENSE': get_mit_license()
    }
    
    # Add attachment files if needed
    for att in decoded_attachments:
        files[att['name']] = att['content']
    
    return files

def get_mit_license():
    """Return MIT License text"""
    return """MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE."""