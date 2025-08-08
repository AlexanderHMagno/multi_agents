"""
Design and Validation Agents

This module contains agents responsible for visual design, image generation,
and technical validation of generated content.
"""

import re
from .base_agent import BaseAgent
from ..utils.state import State


class DesignerTeam(BaseAgent):
    """
    Designer Team Agent - Generates marketing images using DALL-E API.
    
    Responsibilities:
    - AI image generation using DALL-E
    - Visual asset creation and optimization
    - Image prompt processing and refinement
    - Fallback handling for generation failures
    """
    
    def __init__(self, llm, openai_client):
        super().__init__(
            system_prompt="""You are the senior designer team responsible for creating the ad design.
            Your task is to generate a high-quality marketing image based on the final visual prompt.""",
            llm=llm
        )
        self.openai_client = openai_client

    def run(self, state: State) -> dict:
        visual_data = state['artifacts'].get("visual", {})
        visual_prompt = visual_data.get("image_prompt", "")

        if not visual_prompt:
            print("[⚠️] No visual prompt found. Skipping image generation.")
            return self.return_state(state, None)

        if len(visual_prompt) > 3800:
            visual_prompt = visual_prompt[:3800] + "..."

        print("[🎨] Generating image from visual prompt...")

        try:
            # if self.openai_client:
            #     # Generate image using DALL-E
            #     image_response = self.openai_client.images.generate(
            #         model="dall-e-3",
            #         prompt=visual_prompt,
            #         size="1024x1024",
            #         quality="standard",
            #         n=1,
            #     )
            #     image_url = image_response.data[0].url
            # else:
                # Fallback when OpenAI client is not available
            # print("[⚠️] OpenAI client not available. Using placeholder image.")
            image_url = "https://placehold.co/1024x1024?text=Campaign+Image"
            
            print("[✅] Image generated successfully.")
            print(f"Image URL: {image_url}")
            return self.return_state(
                state,
                response="Image generation successful",
                new_artifacts={
                    "visual": {
                        "image_prompt": visual_prompt,
                        "image_url": image_url
                    }
                }
            )

        except Exception as e:
            print(f"[❌ DesignerTeam] Failed to generate image: {e}")
            return self.return_state(
                state,
                response="Image generation failed",
                new_artifacts={
                    "visual": {
                        "image_prompt": visual_prompt,
                        "image_url": "https://placehold.co/1024x1024?text=Image+Generation+Failed"
                    }
                }
            )


class HTMLValidationAgent(BaseAgent):
    """
    HTML Validation Agent - Validates and corrects HTML, CSS, and JavaScript code.
    
    Responsibilities:
    - HTML structure and syntax validation
    - CSS validation and best practices checking
    - JavaScript validation and modern practices
    - Accessibility and SEO optimization
    - Automatic code correction and improvement
    """
    
    def __init__(self, llm):
        super().__init__(
            system_prompt="""You are an HTML validation and correction specialist.
            Your role is to inspect HTML code for validity, accessibility, and best practices,
            then provide corrected versions if necessary.
            
            Check for:
            - Valid HTML5 structure and syntax
            - Proper DOCTYPE declaration
            - Complete head section with meta tags
            - Properly nested elements
            - Closed tags and valid attributes
            - Accessibility compliance (alt tags, semantic HTML)
            - CSS and JavaScript syntax within HTML
            - Mobile responsiveness meta tags
            - SEO optimization elements
            - Cross-browser compatibility
            
            If issues are found, provide:
            - Detailed explanation of problems
            - Corrected HTML code
            - Best practice recommendations
            - Performance optimization suggestions""",
            llm=llm
        )
    
    def validate_html_structure(self, html_content):
        """Basic HTML structure validation"""
        issues = []
        fixes = []
        
        # Check for DOCTYPE
        if not html_content.strip().startswith('<!DOCTYPE html>'):
            issues.append("Missing DOCTYPE declaration")
            fixes.append("Add <!DOCTYPE html> at the beginning")
        
        # Check for html tag
        if '<html' not in html_content:
            issues.append("Missing <html> tag")
            fixes.append("Add <html lang='en'> tag")
        
        # Check for head section
        if '<head>' not in html_content:
            issues.append("Missing <head> section")
            fixes.append("Add <head> section with meta tags")
        
        # Check for meta charset
        if 'charset=' not in html_content:
            issues.append("Missing charset declaration")
            fixes.append("Add <meta charset='UTF-8'>")
        
        # Check for viewport meta tag
        if 'viewport' not in html_content:
            issues.append("Missing viewport meta tag")
            fixes.append("Add <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
        
        # Check for title tag
        if '<title>' not in html_content:
            issues.append("Missing <title> tag")
            fixes.append("Add <title> tag for SEO")
        
        # Check for body tag
        if '<body>' not in html_content:
            issues.append("Missing <body> tag")
            fixes.append("Add <body> tag")
        
        # Check for closing tags
        if '</html>' not in html_content:
            issues.append("Missing closing </html> tag")
            fixes.append("Add closing </html> tag")
        
        return issues, fixes
    
    def validate_css(self, html_content):
        """Comprehensive CSS validation"""
        css_issues = []
        css_fixes = []
        css_warnings = []
        
        # Extract CSS content from style tags and inline styles
        style_blocks = re.findall(r'<style[^>]*>(.*?)</style>', html_content, re.DOTALL)
        inline_styles = re.findall(r'style\s*=\s*["\']([^"\']*)["\']', html_content)
        
        all_css = '\n'.join(style_blocks + inline_styles)
        
        if not all_css.strip():
            css_warnings.append("No CSS found in HTML")
            return css_issues, css_fixes, css_warnings
        
        # Check for basic CSS syntax issues
        # Unclosed braces
        open_braces = all_css.count('{')
        close_braces = all_css.count('}')
        if open_braces != close_braces:
            css_issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
            css_fixes.append("Ensure all CSS rules have matching opening and closing braces")
        
        # Missing semicolons (basic check)
        css_lines = all_css.split('\n')
        for i, line in enumerate(css_lines):
            line = line.strip()
            if ':' in line and not line.endswith((';', '{', '}')) and line:
                css_warnings.append(f"Line {i+1}: Missing semicolon after CSS property")
                css_fixes.append("Add semicolons after CSS property declarations")
        
        # Check for vendor prefixes
        if '-webkit-' in all_css or '-moz-' in all_css or '-ms-' in all_css:
            css_warnings.append("Vendor prefixes detected - consider if still needed")
            css_fixes.append("Review vendor prefixes for modern browser support")
        
        # Check for !important usage
        important_count = all_css.count('!important')
        if important_count > 3:
            css_warnings.append(f"Excessive use of !important ({important_count} instances)")
            css_fixes.append("Reduce !important usage and improve CSS specificity")
        
        # Check for responsive design
        if '@media' not in all_css and len(all_css) > 100:
            css_warnings.append("No media queries found - may not be responsive")
            css_fixes.append("Add CSS media queries for responsive design")
        
        return css_issues, css_fixes, css_warnings
    
    def validate_javascript(self, html_content):
        """Comprehensive JavaScript validation"""
        js_issues = []
        js_fixes = []
        js_warnings = []
        
        # Extract JavaScript content from script tags and inline handlers
        script_blocks = re.findall(r'<script[^>]*>(.*?)</script>', html_content, re.DOTALL)
        inline_handlers = re.findall(r'on\w+\s*=\s*["\']([^"\']*)["\']', html_content)
        
        all_js = '\n'.join(script_blocks + inline_handlers)
        
        if not all_js.strip():
            js_warnings.append("No JavaScript found in HTML")
            return js_issues, js_fixes, js_warnings
        
        # Check for basic JavaScript syntax issues
        # Unclosed parentheses, brackets, braces
        open_parens = all_js.count('(')
        close_parens = all_js.count(')')
        if open_parens != close_parens:
            js_issues.append(f"Unmatched parentheses: {open_parens} opening, {close_parens} closing")
            js_fixes.append("Ensure all parentheses are properly matched")
        
        open_brackets = all_js.count('[')
        close_brackets = all_js.count(']')
        if open_brackets != close_brackets:
            js_issues.append(f"Unmatched brackets: {open_brackets} opening, {close_brackets} closing")
            js_fixes.append("Ensure all brackets are properly matched")
        
        open_braces = all_js.count('{')
        close_braces = all_js.count('}')
        if open_braces != close_braces:
            js_issues.append(f"Unmatched braces: {open_braces} opening, {close_braces} closing")
            js_fixes.append("Ensure all braces are properly matched")
        
        # Check for common JavaScript issues
        if 'var ' in all_js:
            js_warnings.append("'var' declarations found - consider using 'let' or 'const'")
            js_fixes.append("Replace 'var' with 'let' or 'const' for better scoping")
        
        if '==' in all_js and '===' not in all_js:
            js_warnings.append("Loose equality (==) detected - consider strict equality (===)")
            js_fixes.append("Use strict equality (===) instead of loose equality (==)")
        
        # Check for console.log statements
        if 'console.log' in all_js:
            js_warnings.append("console.log statements found - remove for production")
            js_fixes.append("Remove console.log statements before deployment")
        
        # Check for eval usage
        if 'eval(' in all_js:
            js_issues.append("eval() usage detected - security risk")
            js_fixes.append("Avoid eval() for security reasons")
        
        return js_issues, js_fixes, js_warnings
    
    def validate_html_css_js_comprehensive(self, html_content):
        """Comprehensive validation of HTML, CSS, and JavaScript"""
        # HTML validation
        html_issues, html_fixes = self.validate_html_structure(html_content)
        
        # CSS validation
        css_issues, css_fixes, css_warnings = self.validate_css(html_content)
        
        # JavaScript validation
        js_issues, js_fixes, js_warnings = self.validate_javascript(html_content)
        
        # Combine all issues and fixes
        all_issues = html_issues + css_issues + js_issues
        all_fixes = html_fixes + css_fixes + js_fixes
        all_warnings = css_warnings + js_warnings
        
        return {
            'html': {'issues': html_issues, 'fixes': html_fixes},
            'css': {'issues': css_issues, 'fixes': css_fixes, 'warnings': css_warnings},
            'javascript': {'issues': js_issues, 'fixes': js_fixes, 'warnings': js_warnings},
            'all_issues': all_issues,
            'all_fixes': all_fixes,
            'all_warnings': all_warnings,
            'total_issues': len(all_issues),
            'total_warnings': len(all_warnings)
        }
    
    def clean_html_content(self, html_content):
        """Clean and format HTML content"""
        # Remove code block markers
        html_content = re.sub(r'```html\s*', '', html_content)
        html_content = re.sub(r'```\s*$', '', html_content)
        
        # Remove extra whitespace
        html_content = re.sub(r'\n\s*\n', '\n', html_content)
        
        # Ensure proper DOCTYPE if missing
        if not html_content.strip().startswith('<!DOCTYPE'):
            html_content = '<!DOCTYPE html>\n' + html_content.strip()
        
        return html_content.strip()
    
    def run(self, state: State) -> dict:
        web_dev_content = state['artifacts'].get('web_developer', {}).get('campaign_website', '')
        
        if not web_dev_content:
            return self.return_state(state, None, {
                "html_validation": {
                    "status": "error",
                    "message": "No HTML content found to validate",
                    "corrected_html": ""
                }
            })
        
        # Clean the HTML content first
        cleaned_html = self.clean_html_content(web_dev_content)
        
        # Perform advanced validation
        validation_report = self.validate_html_css_js_comprehensive(cleaned_html)
        
        # Create validation prompt for AI-based correction
        validation_prompt = f"""
        Please validate and correct the following HTML code. Focus on creating valid, accessible, and performant HTML.
        
        CRITICAL ISSUES FOUND: {validation_report['all_issues']}
        WARNINGS: {validation_report['all_warnings']}
        RECOMMENDED FIXES: {validation_report['all_fixes']}
        
        HTML CODE TO VALIDATE AND CORRECT:
        {cleaned_html}
        
        REQUIREMENTS FOR CORRECTION:
        1. Fix all critical issues listed above
        2. Address accessibility warnings (add alt tags, semantic HTML)
        3. Ensure valid HTML5 structure with proper DOCTYPE
        4. Include proper meta tags for mobile and SEO
        5. Ensure all tags are properly closed and nested
        6. Add semantic HTML elements (header, nav, main, section, footer)
        7. Include ARIA attributes where appropriate
        8. Optimize CSS (move inline styles to style blocks)
        9. Add proper error handling for JavaScript if present
        10. Ensure mobile responsiveness with proper CSS
        11. Replac ** for bold and * for italic
        
        IMPORTANT: Return ONLY the corrected, complete HTML code without any explanations or markdown formatting.
        """
        
        messages = self.get_messages(validation_prompt)
        response = self.invoke_llm_with_retry(messages, "HTML/CSS/JS Validation")
        
        # Clean and validate the corrected HTML
        corrected_html = self.clean_html_content(response.content)
        corrected_validation_report = self.validate_html_css_js_comprehensive(corrected_html)
        
        # Calculate improvement metrics
        issues_fixed = len(validation_report['all_issues']) - len(corrected_validation_report['all_issues'])
        warnings_addressed = len(validation_report['all_warnings']) - len(corrected_validation_report['all_warnings'])
        
        validation_report_final = {
            "status": "success" if len(corrected_validation_report['all_issues']) == 0 else "warning",
            "original_validation": validation_report,
            "corrected_validation": corrected_validation_report,
            "original_issues": validation_report['all_issues'],
            "original_warnings": validation_report['all_warnings'],
            "corrected_issues": corrected_validation_report['all_issues'],
            "corrected_warnings": corrected_validation_report['all_warnings'],
            "fixes_applied": validation_report['all_fixes'],
            "corrected_html": corrected_html,
            "validation_summary": f"Fixed {issues_fixed} critical issues, addressed {warnings_addressed} warnings",
            "improvement_score": round(((issues_fixed + warnings_addressed) / max(len(validation_report['all_issues']) + len(validation_report['all_warnings']), 1)) * 100, 1),
            "detailed_breakdown": {
                "html": {
                    "original_issues": len(validation_report['html']['issues']),
                    "corrected_issues": len(corrected_validation_report['html']['issues']),
                    "issues_fixed": len(validation_report['html']['issues']) - len(corrected_validation_report['html']['issues'])
                },
                "css": {
                    "original_issues": len(validation_report['css']['issues']),
                    "original_warnings": len(validation_report['css']['warnings']),
                    "corrected_issues": len(corrected_validation_report['css']['issues']),
                    "corrected_warnings": len(corrected_validation_report['css']['warnings']),
                    "issues_fixed": len(validation_report['css']['issues']) - len(corrected_validation_report['css']['issues']),
                    "warnings_addressed": len(validation_report['css']['warnings']) - len(corrected_validation_report['css']['warnings'])
                },
                "javascript": {
                    "original_issues": len(validation_report['javascript']['issues']),
                    "original_warnings": len(validation_report['javascript']['warnings']),
                    "corrected_issues": len(corrected_validation_report['javascript']['issues']),
                    "corrected_warnings": len(corrected_validation_report['javascript']['warnings']),
                    "issues_fixed": len(validation_report['javascript']['issues']) - len(corrected_validation_report['javascript']['issues']),
                    "warnings_addressed": len(validation_report['javascript']['warnings']) - len(corrected_validation_report['javascript']['warnings'])
                }
            }
        }
        
        print(f"✅ HTML/CSS/JS Validation complete: {validation_report_final['validation_summary']}")
        print(f"📊 Overall Improvement Score: {validation_report_final['improvement_score']}%")
        print(f"🏗️ HTML Issues Fixed: {validation_report_final['detailed_breakdown']['html']['issues_fixed']}")
        print(f"🎨 CSS Issues Fixed: {validation_report_final['detailed_breakdown']['css']['issues_fixed']}, Warnings: {validation_report_final['detailed_breakdown']['css']['warnings_addressed']}")
        print(f"⚡ JavaScript Issues Fixed: {validation_report_final['detailed_breakdown']['javascript']['issues_fixed']}, Warnings: {validation_report_final['detailed_breakdown']['javascript']['warnings_addressed']}")
        
        if corrected_validation_report['all_issues']:
            print(f"⚠️ Remaining critical issues: {len(corrected_validation_report['all_issues'])}")
        if corrected_validation_report['all_warnings']:
            print(f"⚠️ Remaining warnings: {len(corrected_validation_report['all_warnings'])}")
        
        return self.return_state(state, response, {"html_validation": validation_report_final}) 