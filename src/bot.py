from telethon import TelegramClient, events, Button
import os
from dotenv import load_dotenv
import requests
from io import BytesIO
import logging
from clients.met import MetMuseumClient

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

# Bot configuration
API_ID = os.getenv('TELEGRAM_API_ID')
API_HASH = os.getenv('TELEGRAM_API_HASH')
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

logger.info("Starting bot with API_ID: %s", API_ID)

# Initialize the Met Museum client
met_client = MetMuseumClient()

# Initialize the Telegram client
bot = TelegramClient('art_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

@bot.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    """Handle the /start command"""
    logger.info("Received /start command from user %s", event.sender_id)
    await event.respond(
        "Welcome to the Art Explorer Bot! 🎨\nClick the button below to get a random artwork:",
        buttons=[Button.inline("Get Artwork 🖼", b"get_artwork")]
    )

@bot.on(events.CallbackQuery(data=b"get_artwork"))
async def get_artwork_handler(event):
    """Handle the get artwork button click"""
    logger.info("Received get_artwork callback from user %s", event.sender_id)
    try:
        artwork = met_client.get_random_object()
        logger.info("Got artwork: %s", artwork.get('title', 'Untitled'))
        await send_artwork(event, artwork)
    except Exception as e:
        logger.error("Error in get_artwork_handler: %s", str(e), exc_info=True)
        await event.answer("Sorry, something went wrong. Please try again.")

async def send_artwork(event, artwork):
    """Helper function to send artwork information"""
    logger.info("Sending artwork to user %s", event.sender_id)
    
    # Create message with artwork details
    message = f"🎨 **{artwork.get('title', 'Untitled')}**\n\n"
    if artwork.get('artistDisplayName'):
        message += f"👨‍🎨 Artist: {artwork['artistDisplayName']}\n"
    if artwork.get('objectDate'):
        message += f"📅 Date: {artwork['objectDate']}\n"
    if artwork.get('medium'):
        message += f"🎯 Medium: {artwork['medium']}\n"
    if artwork.get('department'):
        message += f"🏛 Department: {artwork['department']}\n"
    
    # Add description if available
    if artwork.get('objectDescription'):
        message += f"\n📝 Description:\n{artwork['objectDescription']}\n"
    
    # Add link to the original artwork page
    if artwork.get('objectID'):
        message += f"\n🔗 [View on Met Museum Website](https://www.metmuseum.org/art/collection/search/{artwork['objectID']})"
    
    # Create button for next artwork
    buttons = [Button.inline("Get Artwork 🖼", b"get_artwork")]
    
    # Download and send the image
    image_url = artwork.get('primaryImageSmall')
    if image_url:
        try:
            logger.info("Downloading image from URL: %s", image_url)
            response = requests.get(image_url)
            if response.status_code == 200:
                image_data = BytesIO(response.content)
                image_data.name = 'artwork.jpg'  # Telegram needs a filename
                logger.info("Sending image and message to user")
                await event.respond(
                    message,
                    file=image_data,
                    buttons=buttons,
                    link_preview=True
                )
            else:
                logger.error("Failed to download image. Status code: %s", response.status_code)
                await event.respond(
                    f"{message}\n\n⚠️ Could not load the image",
                    buttons=buttons
                )
        except Exception as e:
            logger.error("Error downloading image: %s", str(e), exc_info=True)
            await event.respond(
                f"{message}\n\n⚠️ Could not load the image",
                buttons=buttons
            )
    else:
        logger.warning("No image URL available for artwork")
        await event.respond(
            f"{message}\n\n⚠️ No image available",
            buttons=buttons
        )
    
    await event.answer()

def main():
    """Start the bot"""
    logger.info("Bot started...")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
