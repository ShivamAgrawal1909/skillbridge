import asyncio
import uuid

from sqlalchemy import text

from app.database import SessionLocal
from app.models.category import Category, Skill

categories_data = [
    {
        "name": "Website Development",
        "slug": "website-development",
        "skills": ["Landing Page", "E-commerce Site", "Custom Web App", "WordPress", "Portfolio Site"]
    },
    {
        "name": "Mobile App Development",
        "slug": "mobile-app-development",
        "skills": ["Android App", "iOS App", "React Native", "Flutter", "Cross-platform App"]
    },
    {
        "name": "Chatbot & WhatsApp Bot",
        "slug": "chatbot-whatsapp-bot",
        "skills": ["WhatsApp Bot", "Website Chatbot", "Telegram Bot", "AI Chatbot"]
    },
    {
        "name": "Digital Marketing",
        "slug": "digital-marketing",
        "skills": ["Social Media Marketing", "Google Ads", "Meta Ads", "Email Marketing", "Influencer Marketing"]
    },
    {
        "name": "SEO",
        "slug": "seo",
        "skills": ["On-page SEO", "Off-page SEO", "Technical SEO", "Local SEO", "E-commerce SEO"]
    },
    {
        "name": "Graphic Design & Branding",
        "slug": "graphic-design-branding",
        "skills": ["Logo Design", "Brand Identity", "Social Media Creatives", "Business Card", "Banner Design"]
    },
    {
        "name": "Content Writing",
        "slug": "content-writing",
        "skills": ["Blog Writing", "Copywriting", "Product Descriptions", "Social Media Content", "Script Writing"]
    },
    {
        "name": "Video Editing",
        "slug": "video-editing",
        "skills": ["Reels Editing", "YouTube Video Editing", "Product Video", "Motion Graphics", "Thumbnail Design"]
    },
    {
        "name": "UI/UX Design",
        "slug": "ui-ux-design",
        "skills": ["Figma Design", "Wireframing", "Prototyping", "User Research", "Design System"]
    },
]


async def seed():
    async with SessionLocal() as db:
        # check if already seeded
        result = await db.execute(text("SELECT COUNT(*) FROM categories"))
        count = result.scalar()
        if count > 0:
            print("Already seeded, skipping.")
            return

        for cat_data in categories_data:
            category = Category(
                id=uuid.uuid4(),
                name=cat_data["name"],
                slug=cat_data["slug"],
            )
            db.add(category)
            await db.flush()

            for skill_name in cat_data["skills"]:
                skill = Skill(
                    id=uuid.uuid4(),
                    name=skill_name,
                    category_id=category.id,
                )
                db.add(skill)

        await db.commit()
        print(f"Seeded {len(categories_data)} categories with skills.")


if __name__ == "__main__":
    asyncio.run(seed())