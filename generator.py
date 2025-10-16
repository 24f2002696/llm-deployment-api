import google.generativeai as genai
import os
import base64
import json

genai.configure(api_key=os.environ.get('GEMINI_API_KEY'))

def generate_app(brief, checks, attachments, task, round_num):
    """Generate app files using Gemini"""
    
    # Validate and decode attachments
    decoded_attachments = []
    
    for att in attachments:
        try:
            name = att.get('name', 'unknown')
            data_uri = att.get('url', '')
            
            # Validate data URI format
            if not data_uri.startswith('data:'):
                print(f"Warning: Invalid data URI format for {name}, skipping")
                continue
            
            # Parse data URI
            parts = data_uri.split(',', 1)
            if len(parts) != 2:
                print(f"Warning: Malformed data URI for {name}, skipping")
                continue
            
            try:
                content = base64.b64decode(parts[1]).decode('utf-8', errors='ignore')
                
                # Validate content size (max 1MB)
                if len(content) > 1024 * 1024:
                    print(f"Warning: Attachment {name} too large (> 1MB), skipping")
                    continue
                
                decoded_attachments.append({
                    "name": name,
                    "content": content,
                    "size": len(content)
                })
                print(f"Successfully decoded attachment: {name} ({len(content)} bytes)")
                
            except Exception as e:
                print(f"Error decoding attachment {name}: {e}")
                continue
                
        except Exception as e:
            print(f"Error processing attachment: {e}")
            continue
    
    if decoded_attachments:
        print(f"Successfully processed {len(decoded_attachments)} attachments")
    
    
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
    readme_prompt = f"""Create an EXCELLENT, professional README.md for a production web application.

TASK: {brief}
CHECKS (Requirements): {json.dumps(checks, indent=2)}

Follow this EXACT structure:

# [App Name]

## Overview
2-3 sentence overview of what the app does and its purpose.

## Features
- Feature 1: Brief description
- Feature 2: Brief description
- Feature 3: Brief description

## Technical Stack
- Frontend: HTML5, CSS3, JavaScript
- Libraries: [List any CDN libraries used]
- Data: [CSV, JSON, or none]

## Getting Started

### Prerequisites
- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection for CDN resources

### Installation
1. Clone the repository
2. Open `index.html` in a web browser
3. No build process or dependencies needed

## Usage

### How to Use
Step-by-step instructions on how to use the application.

### Examples
Provide 1-2 concrete examples of using the app.

## Code Explanation

### Architecture
Explain the overall structure of the application.

### Key Components
- Component 1: What it does and why
- Component 2: What it does and why

### Algorithm/Logic
Explain the main logic and algorithms used.

### Error Handling
Explain how errors are handled gracefully.

## Browser Compatibility
- Chrome: ✅
- Firefox: ✅
- Safari: ✅
- Edge: ✅

## Performance Considerations
- Page load time: < 2s
- Responsive design: Yes
- Accessibility: WCAG 2.1 AA

## Future Improvements
- Potential enhancement 1
- Potential enhancement 2

## License
MIT License - See LICENSE file for details.

## Author
Auto-generated using LLM Code Deployment System.

---

CRITICAL QUALITY REQUIREMENTS:
- Be specific and detailed (not generic)
- Use professional technical language
- Provide actual code references where relevant
- Explain WHY design decisions were made
- Make it suitable for code review and hiring evaluation"""

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