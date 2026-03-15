import g4f
import logging

logger = logging.getLogger(__name__)

def generate_ai_email(company_name, status, problem):
    """
    Generates a personalized outreach email from Hussain to a business.
    """
    if status == "NO_WEBSITE":
        prompt = (
            f"Write a professional cold outreach email to {company_name}. "
            f"The sender is Hussain, a web developer. "
            f"Mention that you noticed they don't have a website and explain why having a digital presence is critical for growth. "
            f"Offer to build a fast, modern, and mobile-friendly website. "
            f"Keep it short, professional, and friendly. Sign it as 'Hussain'. "
            f"DO NOT mention being an AI or assistant. DO NOT include any ads, links, or placeholders like [Link]."
        )
    else:
        prompt = (
            f"Write a professional cold outreach email to {company_name}. "
            f"The sender is Hussain, a web developer. "
            f"Mention that you audited their website and found these specific issues: {problem}. "
            f"Explain how fixing these (e.g., speed, mobile optimization) will help them get more customers. "
            f"Offer a free 10-minute consultation. "
            f"Keep it short, professional, and friendly. Sign it as 'Hussain'. "
            f"DO NOT mention being an AI or assistant. DO NOT include any ads, links, or placeholders like [Link]."
        )

    try:
        response = g4f.ChatCompletion.create(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}],
            timeout=30
        )
        
        # Robust cleaning
        clean = response.replace("Support Pollinations.AI", "").replace("Powered by Pollinations.AI", "")
        clean = clean.replace("I am an AI", "I am Hussain").replace("As an AI", "As a developer")
        
        if "---" in clean:
            clean = clean.split("---")[0]
        
        # Remove markdown artifacts if AI returns them
        clean = clean.replace("```html", "").replace("```", "")
        
        return clean.strip()
    except Exception as e:
        logger.error(f"AI Email generation failed: {e}")
        # Improved Fallback templates
        if status == "NO_WEBSITE":
            return f"Hi {company_name} Team,\n\nI was looking for your business online and noticed you don't have a website yet. I'm Hussain, a web developer, and I help local businesses get more clients by building fast, professional websites.\n\nWould you be open to a quick chat about how a website could help your growth?\n\nBest,\nHussain"
        else:
            return f"Hi {company_name} Team,\n\nI just took a look at your website and noticed some areas for improvement, specifically: {problem}.\n\nI'm Hussain, and I specialize in optimizing business websites for speed and mobile users to ensure you don't lose potential customers. Are you available for a brief call to discuss some easy fixes?\n\nBest,\nHussain"
