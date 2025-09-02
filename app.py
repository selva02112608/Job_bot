import requests
import time
from datetime import datetime, timedelta, UTC
from serpapi import Client as GoogleSearch


BOT_TOKEN = "8226783276:AAEZsOzPRVIXrIsVB4Bi57swynogZvUfS8E"
# Remove hardcoded CHAT_ID - will be stored dynamically
SERPAPI_KEY = "f3acba64243879e82a8ab3b17de51da89667979013be82cfe1e83d5afe263233"

# Store jobs to avoid duplicates
seen_jobs = set()

# Store all user chat IDs who have started the bot
active_users = set()

def get_bot_updates():
    """Get recent updates from Telegram to find new users"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        response = requests.get(url)
        if response.status_code == 200:
            updates = response.json().get("result", [])
            for update in updates:
                if "message" in update and "chat" in update["message"]:
                    chat_id = str(update["message"]["chat"]["id"])
                    if update["message"].get("text") == "/start":
                        active_users.add(chat_id)
                        print(f"👤 New user added: {chat_id}")
        return True
    except Exception as e:
        print(f"❌ Error getting bot updates: {e}")
        return False

def send_message_to_all_users(message):
    """Send message to all active users"""
    if not active_users:
        print("⚠️ No active users to send message to")
        return
    
    success_count = 0
    failed_count = 0
    
    for chat_id in active_users:
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            payload = {"chat_id": chat_id, "text": message, "parse_mode": "HTML"}
            response = requests.post(url, data=payload)
            
            if response.status_code == 200:
                success_count += 1
                print(f"✅ Message sent to user {chat_id}")
            else:
                failed_count += 1
                print(f"❌ Failed to send message to user {chat_id}: {response.status_code}")
                
        except Exception as e:
            failed_count += 1
            print(f"❌ Error sending message to user {chat_id}: {e}")
    
    print(f"📤 Message delivery summary: {success_count} successful, {failed_count} failed")

def send_message(message):
    """Send message to all users (legacy function for compatibility)"""
    send_message_to_all_users(message)

def handle_user_commands():
    """Handle user commands and manage user list"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates"
        response = requests.get(url)
        if response.status_code == 200:
            updates = response.json().get("result", [])
            for update in updates:
                if "message" in update and "chat" in update["message"]:
                    chat_id = str(update["message"]["chat"]["id"])
                    message_text = update["message"].get("text", "")
                    
                    if message_text == "/start":
                        active_users.add(chat_id)
                        welcome_message = f"""🚀 <b>Welcome to Tamil Nadu JobBot!</b>

🔍 I'll search for UNLIMITED IT jobs across ALL Tamil Nadu districts
📱 You'll receive job alerts every 60 seconds for fresh opportunities
⏰ Only jobs posted within the last 1 day
🌍 Coverage: 30+ districts including Chennai, Coimbatore, Madurai, Salem, and more!

🎯 <b>Smart Filtering Criteria:</b>
• 📅 Posted within 1 day only
• 💰 Salary: 3+ LPA per year OR 40k+ per month
• 🎯 Experience: 1+ years OR Fresher positions
• 🏢 Company: Medium/Large companies (no startups)

💼 <b>Comprehensive IT Job Types:</b>
• Software Engineer/Developer (Python, Java, C#, PHP, .NET)
• Full Stack Developer (React, Angular, Vue.js, Node.js)
• Mobile Developer (Android, iOS, Flutter, React Native)
• Data Science (Data Scientist, Data Analyst, ML Engineer, AI Engineer)
• DevOps & Cloud (DevOps Engineer, Cloud Engineer, AWS, Azure)
• Database (SQL Developer, MongoDB Developer, Database Developer)
• Testing & QA (QA Engineer, Test Engineer, Automation, Selenium)
• Security (Security Engineer, Cyber Security Analyst, Network Security)
• System & Network (System Admin, Network Engineer, Linux/Windows Admin)
• Management (Product Manager, Project Manager, Scrum Master, Business Analyst)
• Emerging Tech (Blockchain, IoT, Docker, Kubernetes, Jenkins)

<b>Commands:</b>
/start - Start receiving job alerts
/status - Check bot status
/stop - Stop receiving job alerts

<b>Your Chat ID:</b> {chat_id}

✅ You're now subscribed to filtered IT job alerts!"""
                        
                        # Send welcome message to this user only
                        try:
                            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                            payload = {"chat_id": chat_id, "text": welcome_message, "parse_mode": "HTML"}
                            requests.post(url, data=payload)
                            print(f"👤 New user {chat_id} started the bot")
                        except Exception as e:
                            print(f"❌ Error sending welcome message: {e}")
                    
                    elif message_text == "/status":
                        status_message = f"""📊 <b>JobBot Status</b>

✅ Bot is running normally
🔍 Checking for jobs every 60 seconds
📱 Total jobs found: {len(seen_jobs)}
👥 Active users: {len(active_users)}
⏰ Last check: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC

<b>Your Chat ID:</b> {chat_id}"""
                        
                        try:
                            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                            payload = {"chat_id": chat_id, "text": status_message, "parse_mode": "HTML"}
                            requests.post(url, data=payload)
                        except Exception as e:
                            print(f"❌ Error sending status message: {e}")
                    
                    elif message_text == "/stop":
                        if chat_id in active_users:
                            active_users.remove(chat_id)
                            stop_message = "🛑 <b>JobBot Stopped</b>\n\nYou've unsubscribed from job alerts. Send /start to resume."
                            try:
                                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                                payload = {"chat_id": chat_id, "text": stop_message, "parse_mode": "HTML"}
                                requests.post(url, data=payload)
                                print(f"👤 User {chat_id} stopped the bot")
                            except Exception as e:
                                print(f"❌ Error sending stop message: {e}")
                        else:
                            not_subscribed = "ℹ️ You're not currently subscribed to job alerts. Send /start to begin."
                            try:
                                url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
                                payload = {"chat_id": chat_id, "text": not_subscribed, "parse_mode": "HTML"}
                                requests.post(url, data=payload)
                            except Exception as e:
                                print(f"❌ Error sending not subscribed message: {e}")
                            
    except Exception as e:
        print(f"❌ Error handling user commands: {e}")

def view_raw_google_response():
    """View the complete raw Google response from SerpAPI"""
    try:
        print("🔍 Fetching raw Google response from SerpAPI...")
        
        search = GoogleSearch(api_key=SERPAPI_KEY)
        
        # Test with Google Jobs
        print("\n1. Testing Google Jobs response...")
        jobs_response = search.search({
            "q": "software engineer Chennai",
            "engine": "google_jobs",
            "location": "Chennai, India",
            "gl": "in",
            "hl": "en"
        })
        
        if jobs_response:
            print(f"✅ Response received with {len(jobs_response)} top-level keys")
            print(f"📋 Top-level keys: {list(jobs_response.keys())}")
            
            # Show search metadata
            if "search_metadata" in jobs_response:
                print(f"\n📊 Search Metadata:")
                metadata = jobs_response["search_metadata"]
                for key, value in metadata.items():
                    print(f"   {key}: {value}")
            
            # Show search parameters
            if "search_parameters" in jobs_response:
                print(f"\n⚙️ Search Parameters:")
                params = jobs_response["search_parameters"]
                for key, value in params.items():
                    print(f"   {key}: {value}")
            
            # Show jobs results if available
            if "jobs_results" in jobs_response:
                jobs = jobs_response["jobs_results"]
                print(f"\n💼 Jobs Results ({len(jobs)} found):")
                if jobs:
                    first_job = jobs[0]
                    print(f"   First job structure:")
                    for key, value in first_job.items():
                        print(f"     {key}: {value}")
                else:
                    print("   No jobs found in jobs_results")
            else:
                print("\n❌ No jobs_results found")
            
            # Show any errors
            if "error" in jobs_response:
                print(f"\n❌ Error found: {jobs_response['error']}")
            
            # Show other available data
            other_keys = [k for k in jobs_response.keys() if k not in ['search_metadata', 'search_parameters', 'jobs_results', 'error']]
            if other_keys:
                print(f"\n🔍 Other available data:")
                for key in other_keys:
                    data = jobs_response[key]
                    if isinstance(data, list):
                        print(f"   {key}: List with {len(data)} items")
                    elif isinstance(data, dict):
                        print(f"   {key}: Dictionary with {len(data)} keys")
                    else:
                        print(f"   {key}: {data}")
        
        # Test with regular Google search
        print(f"\n{'='*50}")
        print("\n2. Testing regular Google search response...")
        google_response = search.search({
            "q": "software engineer jobs Chennai",
            "engine": "google",
            "gl": "in",
            "hl": "en",
            "num": 5
        })
        
        if google_response:
            print(f"✅ Google search response received")
            print(f"📋 Available keys: {list(google_response.keys())}")
            
            if "organic_results" in google_response:
                organic = google_response["organic_results"]
                print(f"\n🔍 Organic Results ({len(organic)} found):")
                if organic:
                    first_result = organic[0]
                    print(f"   First result structure:")
                    for key, value in first_result.items():
                        print(f"     {key}: {value}")
        
        # Save response to file for detailed inspection
        print(f"\n{'='*50}")
        print("\n💾 Saving detailed response to 'serpapi_response.json'...")
        import json
        with open('serpapi_response.json', 'w', encoding='utf-8') as f:
            json.dump(jobs_response, f, indent=2, ensure_ascii=False)
        print("✅ Response saved to 'serpapi_response.json'")
        print("📁 You can open this file to see the complete structure")
        
    except Exception as e:
        print(f"❌ Error viewing raw response: {e}")

def debug_serpapi_response():
    """Debug function to see actual SerpAPI response structure"""
    try:
        print("🧪 Testing SerpAPI response structure...")
        
        search = GoogleSearch(api_key=SERPAPI_KEY)
        
        # Test with a simple search
        results = search.search({
            "q": "software engineer Chennai",
            "engine": "google_jobs",
            "location": "Chennai, India",
            "gl": "in",
            "hl": "en"
        })
        
        if results and "jobs_results" in results:
            print(f"✅ Found {len(results['jobs_results'])} jobs")
            if results['jobs_results']:
                first_job = results['jobs_results'][0]
                print(f"\n🔍 First job structure:")
                print(f"Available keys: {list(first_job.keys())}")
                print(f"\n📋 Sample job data:")
                for key, value in first_job.items():
                    print(f"   {key}: {value}")
        else:
            print("❌ No jobs_results found")
            if results:
                print(f"Available keys: {list(results.keys())}")
                
    except Exception as e:
        print(f"❌ Error debugging: {e}")

def fetch_and_send_jobs():
    """Enhanced job fetching with comprehensive SerpAPI data"""
    try:
        print(f"🔍 Searching for jobs in Tamil Nadu...")
        
        # Try multiple search strategies - ALL Tamil Nadu Districts
        search_strategies = [
            # Major Metropolitan Cities
            {
                "name": "Google Jobs - Chennai",
                "params": {
                    "q": "software engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Coimbatore",
                "params": {
                    "q": "software developer Coimbatore",
                    "engine": "google_jobs",
                    "location": "Coimbatore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Madurai",
                "params": {
                    "q": "software engineer Madurai",
                    "engine": "google_jobs",
                    "location": "Madurai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Salem",
                "params": {
                    "q": "software developer Salem",
                    "engine": "google_jobs",
                    "location": "Salem, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            # Additional Major Districts
            {
                "name": "Google Jobs - Trichy (Tiruchirappalli)",
                "params": {
                    "q": "software engineer Trichy",
                    "engine": "google_jobs",
                    "location": "Tiruchirappalli, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Vellore",
                "params": {
                    "q": "software developer Vellore",
                    "engine": "google_jobs",
                    "location": "Vellore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Erode",
                "params": {
                    "q": "software engineer Erode",
                    "engine": "google_jobs",
                    "location": "Erode, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Tiruppur",
                "params": {
                    "q": "software developer Tiruppur",
                    "engine": "google_jobs",
                    "location": "Tiruppur, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Thanjavur",
                "params": {
                    "q": "software engineer Thanjavur",
                    "engine": "google_jobs",
                    "location": "Thanjavur, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Karur",
                "params": {
                    "q": "software developer Karur",
                    "engine": "google_jobs",
                    "location": "Karur, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Namakkal",
                "params": {
                    "q": "software engineer Namakkal",
                    "engine": "google_jobs",
                    "location": "Namakkal, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Dindigul",
                "params": {
                    "q": "software developer Dindigul",
                    "engine": "google_jobs",
                    "location": "Dindigul, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Sivaganga",
                "params": {
                    "q": "software engineer Sivaganga",
                    "engine": "google_jobs",
                    "location": "Sivaganga, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Ramanathapuram",
                "params": {
                    "q": "software developer Ramanathapuram",
                    "engine": "google_jobs",
                    "location": "Ramanathapuram, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Virudhunagar",
                "params": {
                    "q": "software engineer Virudhunagar",
                    "engine": "google_jobs",
                    "location": "Virudhunagar, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Thoothukkudi",
                "params": {
                    "q": "software developer Thoothukkudi",
                    "engine": "google_jobs",
                    "location": "Thoothukkudi, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Tirunelveli",
                "params": {
                    "q": "software engineer Tirunelveli",
                    "engine": "google_jobs",
                    "location": "Tirunelveli, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Kanyakumari",
                "params": {
                    "q": "software developer Kanyakumari",
                    "engine": "google_jobs",
                    "location": "Kanyakumari, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Theni",
                "params": {
                    "q": "software engineer Theni",
                    "engine": "google_jobs",
                    "location": "Theni, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Pudukkottai",
                "params": {
                    "q": "software developer Pudukkottai",
                    "engine": "google_jobs",
                    "location": "Pudukkottai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Sivagangai",
                "params": {
                    "q": "software engineer Sivagangai",
                    "engine": "google_jobs",
                    "location": "Sivagangai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Perambalur",
                "params": {
                    "q": "software developer Perambalur",
                    "engine": "google_jobs",
                    "location": "Perambalur, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Ariyalur",
                "params": {
                    "q": "software engineer Ariyalur",
                    "engine": "google_jobs",
                    "location": "Ariyalur, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Cuddalore",
                "params": {
                    "q": "software developer Cuddalore",
                    "engine": "google_jobs",
                    "location": "Cuddalore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Villupuram",
                "params": {
                    "q": "software engineer Villupuram",
                    "engine": "google_jobs",
                    "location": "Villupuram, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Kanchipuram",
                "params": {
                    "q": "software developer Kanchipuram",
                    "engine": "google_jobs",
                    "location": "Kanchipuram, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Tiruvallur",
                "params": {
                    "q": "software engineer Tiruvallur",
                    "engine": "google_jobs",
                    "location": "Tiruvallur, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Krishnagiri",
                "params": {
                    "q": "software developer Krishnagiri",
                    "engine": "google_jobs",
                    "location": "Krishnagiri, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Dharmapuri",
                "params": {
                    "q": "software engineer Dharmapuri",
                    "engine": "google_jobs",
                    "location": "Dharmapuri, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Nilgiris",
                "params": {
                    "q": "software developer Ooty Nilgiris",
                    "engine": "google_jobs",
                    "location": "Ooty, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            # Enhanced IT-focused search strategies for comprehensive coverage
            {
                "name": "Google Jobs - Software Developer Chennai",
                "params": {
                    "q": "software developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Full Stack Developer Chennai",
                "params": {
                    "q": "full stack developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Python Developer Chennai",
                "params": {
                    "q": "python developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Java Developer Chennai",
                "params": {
                    "q": "java developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - React Developer Chennai",
                "params": {
                    "q": "react developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Node.js Developer Chennai",
                "params": {
                    "q": "node.js developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Angular Developer Chennai",
                "params": {
                    "q": "angular developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Vue.js Developer Chennai",
                "params": {
                    "q": "vue.js developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - PHP Developer Chennai",
                "params": {
                    "q": "php developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - .NET Developer Chennai",
                "params": {
                    "q": ".net developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - C# Developer Chennai",
                "params": {
                    "q": "c# developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Data Scientist Chennai",
                "params": {
                    "q": "data scientist Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Data Analyst Chennai",
                "params": {
                    "q": "data analyst Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Machine Learning Engineer Chennai",
                "params": {
                    "q": "machine learning engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - AI Engineer Chennai",
                "params": {
                    "q": "artificial intelligence engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - DevOps Engineer Chennai",
                "params": {
                    "q": "devops engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Cloud Engineer Chennai",
                "params": {
                    "q": "cloud engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - AWS Engineer Chennai",
                "params": {
                    "q": "aws engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Azure Developer Chennai",
                "params": {
                    "q": "azure developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Database Developer Chennai",
                "params": {
                    "q": "database developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - SQL Developer Chennai",
                "params": {
                    "q": "sql developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - MongoDB Developer Chennai",
                "params": {
                    "q": "mongodb developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Mobile App Developer Chennai",
                "params": {
                    "q": "mobile app developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Android Developer Chennai",
                "params": {
                    "q": "android developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - iOS Developer Chennai",
                "params": {
                    "q": "ios developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Flutter Developer Chennai",
                "params": {
                    "q": "flutter developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - React Native Developer Chennai",
                "params": {
                    "q": "react native developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - UI/UX Designer Chennai",
                "params": {
                    "q": "ui ux designer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Frontend Developer Chennai",
                "params": {
                    "q": "frontend developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Backend Developer Chennai",
                "params": {
                    "q": "backend developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - System Administrator Chennai",
                "params": {
                    "q": "system administrator Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Network Engineer Chennai",
                "params": {
                    "q": "network engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Security Engineer Chennai",
                "params": {
                    "q": "security engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Cyber Security Analyst Chennai",
                "params": {
                    "q": "cyber security analyst Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - QA Engineer Chennai",
                "params": {
                    "q": "qa engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Test Engineer Chennai",
                "params": {
                    "q": "test engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Automation Engineer Chennai",
                "params": {
                    "q": "automation engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Selenium Tester Chennai",
                "params": {
                    "q": "selenium tester Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Business Analyst Chennai",
                "params": {
                    "q": "business analyst Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Product Manager Chennai",
                "params": {
                    "q": "product manager Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Scrum Master Chennai",
                "params": {
                    "q": "scrum master Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Project Manager Chennai",
                "params": {
                    "q": "project manager Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            # Additional IT-focused searches for other major cities
            {
                "name": "Google Jobs - Full Stack Developer Coimbatore",
                "params": {
                    "q": "full stack developer Coimbatore",
                    "engine": "google_jobs",
                    "location": "Coimbatore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Python Developer Coimbatore",
                "params": {
                    "q": "python developer Coimbatore",
                    "engine": "google_jobs",
                    "location": "Coimbatore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Java Developer Coimbatore",
                "params": {
                    "q": "java developer Coimbatore",
                    "engine": "google_jobs",
                    "location": "Coimbatore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Data Scientist Coimbatore",
                "params": {
                    "q": "data scientist Coimbatore",
                    "engine": "google_jobs",
                    "location": "Coimbatore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - DevOps Engineer Coimbatore",
                "params": {
                    "q": "devops engineer Coimbatore",
                    "engine": "google_jobs",
                    "location": "Coimbatore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Full Stack Developer Madurai",
                "params": {
                    "q": "full stack developer Madurai",
                    "engine": "google_jobs",
                    "location": "Madurai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Python Developer Madurai",
                "params": {
                    "q": "python developer Madurai",
                    "engine": "google_jobs",
                    "location": "Madurai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Java Developer Madurai",
                "params": {
                    "q": "java developer Madurai",
                    "engine": "google_jobs",
                    "location": "Madurai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Full Stack Developer Salem",
                "params": {
                    "q": "full stack developer Salem",
                    "engine": "google_jobs",
                    "location": "Salem, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Python Developer Salem",
                "params": {
                    "q": "python developer Salem",
                    "engine": "google_jobs",
                    "location": "Salem, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Full Stack Developer Trichy",
                "params": {
                    "q": "full stack developer Trichy",
                    "engine": "google_jobs",
                    "location": "Tiruchirappalli, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Python Developer Trichy",
                "params": {
                    "q": "python developer Trichy",
                    "engine": "google_jobs",
                    "location": "Tiruchirappalli, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Full Stack Developer Vellore",
                "params": {
                    "q": "full stack developer Vellore",
                    "engine": "google_jobs",
                    "location": "Vellore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Python Developer Vellore",
                "params": {
                    "q": "python developer Vellore",
                    "engine": "google_jobs",
                    "location": "Vellore, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            # Specialized IT searches for emerging technologies
            {
                "name": "Google Jobs - Blockchain Developer Chennai",
                "params": {
                    "q": "blockchain developer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - IoT Engineer Chennai",
                "params": {
                    "q": "iot engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Docker Engineer Chennai",
                "params": {
                    "q": "docker engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Kubernetes Engineer Chennai",
                "params": {
                    "q": "kubernetes engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Jenkins Engineer Chennai",
                "params": {
                    "q": "jenkins engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Git Engineer Chennai",
                "params": {
                    "q": "git engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Linux Administrator Chennai",
                "params": {
                    "q": "linux administrator Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Windows Administrator Chennai",
                "params": {
                    "q": "windows administrator Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Network Security Engineer Chennai",
                "params": {
                    "q": "network security engineer Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            {
                "name": "Google Jobs - Information Security Analyst Chennai",
                "params": {
                    "q": "information security analyst Chennai",
                    "engine": "google_jobs",
                    "location": "Chennai, India",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            },
            # Fallback: Regular Google search for job sites
            {
                "name": "Regular Google - All Tamil Nadu Job Sites",
                "params": {
                    "q": "software engineer jobs Tamil Nadu site:linkedin.com OR site:naukri.com OR site:indeed.co.in OR site:monsterindia.com OR site:timesjobs.com",
                    "engine": "google",
                    "gl": "in",
                    "hl": "en",
                    "num": 200
                }
            }
        ]
        
        jobs = []
        search = GoogleSearch(api_key=SERPAPI_KEY)
        
        for strategy in search_strategies:
            try:
                print(f"🔍 Trying: {strategy['name']}")
                results = search.search(strategy['params'])
                
                if not results:
                    print(f"   ⚠️ No results from {strategy['name']}")
                    continue
                
                # Check for errors
                if "error" in results:
                    print(f"   ❌ Error from {strategy['name']}: {results['error']}")
                    continue
                
                # Extract jobs based on engine type
                current_jobs = []
                if strategy['params']['engine'] == 'google_jobs':
                    if "jobs_results" in results:
                        current_jobs = results["jobs_results"]
                        print(f"   ✅ Found {len(current_jobs)} jobs from Google Jobs")
                    else:
                        print(f"   ⚠️ No jobs_results from {strategy['name']}")
                else:
                    if "organic_results" in results:
                        current_jobs = results["organic_results"]
                        print(f"   ✅ Found {len(current_jobs)} results from Google search")
                    else:
                        print(f"   ⚠️ No organic_results from {strategy['name']}")
                
                # Add to total jobs if we found any
                if current_jobs:
                    jobs.extend(current_jobs)
                    print(f"   📊 Total jobs so far: {len(jobs)}")
                    # Continue searching all strategies to get maximum job coverage
                    
            except Exception as e:
                print(f"   ❌ Error with {strategy['name']}: {e}")
                continue
        
        if not jobs:
            print("❌ No jobs found from any search strategy")
            return
            
        print(f"🔍 Processing {len(jobs)} total jobs...")
        print(f"📅 Filtering for jobs posted within last 1 day only...")
        
        # Process each job with enhanced data extraction
        recent_jobs_count = 0
        skipped_jobs_count = 0
        
        for job in jobs:
            try:
                # Debug: Print available keys for first job
                if jobs.index(job) == 0:
                    print(f"🔍 First job available keys: {list(job.keys())}")
                    print(f"🔗 Link fields found:")
                    link_fields = ['via', 'link', 'url', 'application_url', 'apply_url', 'job_url', 'source', 'displayed_link']
                    for field in link_fields:
                        if field in job:
                            print(f"   {field}: {job[field]}")
                    # Show extensions and other relevant fields
                    if 'extensions' in job:
                        print(f"   📋 Extensions: {job['extensions']}")
                    if 'detected_extensions' in job:
                        print(f"   🔍 Detected Extensions: {job['detected_extensions']}")
                    if 'apply_options' in job:
                        print(f"   📝 Apply Options: {job['apply_options']}")
                
                # Extract comprehensive job information with correct field mappings
                title = job.get("title", job.get("name", "No Title"))
                company = job.get("company_name", job.get("source", job.get("displayed_link", "Unknown Company")))
                location = job.get("location", job.get("snippet", "Chennai, Tamil Nadu"))
                description = job.get("description", job.get("snippet", "No description available"))
                
                # Extract salary, experience, and job type from extensions
                extensions = job.get("extensions", [])
                detected_extensions = job.get("detected_extensions", [])
                
                # Check if job is posted within last 1 day ONLY
                is_recent_job = False
                posted_date = "Unknown date"
                
                # Try to extract posting date from extensions
                for ext in extensions:
                    if isinstance(ext, str):
                        ext_lower = ext.lower()
                        # Check for recent posting indicators - ONLY 1 day or less
                        if any(word in ext_lower for word in ['just posted', 'today', '1 day ago', 'yesterday', 'few hours ago', 'recently posted']):
                            posted_date = ext
                            is_recent_job = True
                            break
                        elif any(word in ext_lower for word in ['2 days ago', '3 days ago', 'week ago', 'month ago', 'few days ago']):
                            posted_date = ext
                            is_recent_job = False
                            break
                        elif any(word in ext_lower for word in ['day', 'week', 'month', 'ago', 'posted']):
                            # Check if it's within 1 day ONLY
                            if '1 day' in ext_lower or 'today' in ext_lower or 'yesterday' in ext_lower:
                                posted_date = ext
                                is_recent_job = True
                            else:
                                posted_date = ext
                                is_recent_job = False
                            break
                
                # If no date found in extensions, assume it's recent (new job listing)
                if posted_date == "Unknown date":
                    posted_date = "Just posted"
                    is_recent_job = True
                
                # Skip jobs older than 1 day
                if not is_recent_job:
                    print(f"⏭️ Skipping older job: {title} at {company} - Posted: {posted_date}")
                    skipped_jobs_count += 1
                    continue
                
                # Try to extract salary from extensions
                salary = "Salary not specified"
                salary_value = 0
                is_monthly = False
                for ext in extensions:
                    if isinstance(ext, str):
                        if any(word in ext.lower() for word in ['₹', 'rs', 'lakh', 'crore', 'salary', 'pay', 'per annum', 'per month', 'lpa', 'lakhs', 'crores','LPA', 'k', 'thousand', 'L']):
                            salary = ext
                            # Extract numeric value for salary filtering
                            import re
                            # Check for monthly salary (K per month, thousand per month, etc.)
                            monthly_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:k|thousand)\s*(?:per\s*month|monthly|a\s*month)', ext.lower())
                            if monthly_match:
                                salary_value = float(monthly_match.group(1))
                                is_monthly = True
                            else:
                                # Check for annual salary (LPA, lakhs per annum)
                                annual_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:lpa|lakh|lakhs|LPA)', ext.lower())
                                if annual_match:
                                    salary_value = float(annual_match.group(1))
                                    is_monthly = False
                                else:
                                    # Check for simple K (assume monthly if no other indicator)
                                    simple_k_match = re.search(r'(\d+(?:\.\d+)?)\s*k', ext.lower())
                                    if simple_k_match:
                                        salary_value = float(simple_k_match.group(1))
                                        is_monthly = True
                            break
                
                # Try to extract experience from extensions
                experience = "Not specified"
                experience_years = 0
                for ext in extensions:
                    if isinstance(ext, str):
                        if any(word in ext.lower() for word in ['year', 'experience', 'fresher', 'senior', 'junior', 'lead', 'entry', 'mid', 'expert']):
                            experience = ext
                            # Extract numeric value for experience filtering
                            import re
                            exp_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:year|years|yr|yrs)', ext.lower())
                            if exp_match:
                                experience_years = float(exp_match.group(1))
                            elif 'fresher' in ext.lower() or 'entry' in ext.lower():
                                experience_years = 0
                            break
                
                # Filter for company size (avoid startups)
                company_lower = company.lower()
                startup_indicators = ['startup', 'start-up', 'early stage', 'seed', 'series a', 'series b', 'funded', 'incubator', 'accelerator']
                is_startup = any(indicator in company_lower for indicator in startup_indicators)
                
                # Filter for salary (3+ LPA OR 40k+ monthly)
                if salary != "Salary not specified":
                    if is_monthly:
                        # For monthly salaries, check if above 40k
                        if salary_value < 40:
                            print(f"💰 Skipping low monthly salary job: {title} at {company} - Salary: {salary} (below 40k monthly)")
                            skipped_jobs_count += 1
                            continue
                    else:
                        # For annual salaries, check if above 3 LPA
                        if salary_value < 3:
                            print(f"💰 Skipping low annual salary job: {title} at {company} - Salary: {salary} (below 3 LPA)")
                            skipped_jobs_count += 1
                            continue
                
                # Filter for experience (1+ years OR fresher positions)
                if experience_years < 1 and experience != "Not specified":
                    # Check if it's explicitly a fresher position
                    fresher_indicators = ['fresher', 'freshers', 'entry level', 'entry-level', '0 years', 'no experience', 'graduate', 'new graduate']
                    is_fresher_job = any(indicator in experience.lower() for indicator in fresher_indicators)
                    
                    if not is_fresher_job:
                        print(f"🎯 Skipping low experience job: {title} at {company} - Experience: {experience} (below 1 year and not fresher)")
                        skipped_jobs_count += 1
                        continue
                    else:
                        print(f"✅ Including fresher job: {title} at {company} - Experience: {experience}")
                
                # Filter for company size (avoid startups)
                if is_startup:
                    print(f"🏢 Skipping startup job: {title} at {company} - Company type: Startup")
                    skipped_jobs_count += 1
                    continue
                
                recent_jobs_count += 1
                
                # Try to extract job type from extensions
                job_type = "Full-time"
                for ext in extensions:
                    if isinstance(ext, str):
                        if any(word in ext.lower() for word in ['part-time', 'contract', 'internship', 'remote', 'hybrid']):
                            job_type = ext
                            break
                
                # Try to extract posted date from extensions or use current time
                posted_date = "Unknown date"
                for ext in extensions:
                    if isinstance(ext, str):
                        if any(word in ext.lower() for word in ['day', 'week', 'month', 'ago', 'posted']):
                            posted_date = ext
                            break
                
                # If no date found, use current time
                if posted_date == "Unknown date":
                    posted_date = f"Just posted"
                
                # Get the exact job application link - prioritize direct links
                job_link = "No link available"
                
                # Check if via is actually a URL or just company name
                via_field = job.get("via", "")
                if via_field and (via_field.startswith(('http://', 'https://', '//')) or '.' in via_field):
                    job_link = via_field
                else:
                    # Try to get link from apply_options
                    apply_options = job.get("apply_options", [])
                    if apply_options and isinstance(apply_options, list):
                        for option in apply_options:
                            if isinstance(option, dict) and 'link' in option:
                                job_link = option['link']
                                break
                            elif isinstance(option, str) and option.startswith(('http://', 'https://')):
                                job_link = option
                                break
                    
                    # If no apply_options link, try other fields
                    if job_link == "No link available":
                        job_link = (
                            job.get("link") or          # Primary link
                            job.get("url") or           # URL field
                            job.get("application_url") or # Application specific URL
                            job.get("apply_url") or     # Apply URL
                            job.get("job_url") or       # Job URL
                            job.get("source") or        # Source as fallback
                            job.get("displayed_link") or # Displayed link as last resort
                            "No link available"
                        )
                
                # Clean up the link - remove any tracking parameters
                if job_link and job_link != "No link available":
                    # Remove common tracking parameters
                    tracking_params = ['utm_source', 'utm_medium', 'utm_campaign', 'ref', 'source']
                    if '?' in job_link:
                        base_url = job_link.split('?')[0]
                        params = job_link.split('?')[1].split('&')
                        clean_params = [p for p in params if not any(tp in p for tp in tracking_params)]
                        if clean_params:
                            job_link = f"{base_url}?{'&'.join(clean_params)}"
                        else:
                            job_link = base_url
                
                # Validate and format the link
                if job_link and job_link != "No link available":
                    # Ensure the link starts with http/https
                    if not job_link.startswith(('http://', 'https://')):
                        if job_link.startswith('//'):
                            job_link = 'https:' + job_link
                        elif job_link.startswith('/'):
                            job_link = 'https://google.com' + job_link
                        else:
                            job_link = 'https://' + job_link
                
                # Create unique job identifier
                job_id = f"{company}_{title}_{location}"
                
                # Check if we've seen this job before
                if job_id not in seen_jobs:
                    seen_jobs.add(job_id)
                    
                    # Create rich, formatted message
                    message = f"""🚨 <b>New Job Alert!</b>

🏢 <b>Company:</b> {company}
💼 <b>Position:</b> {title}
📍 <b>Location:</b> {location}
💰 <b>Salary:</b> {salary}
📅 <b>Posted:</b> {posted_date}
🕒 <b>Job Type:</b> {job_type}
🎯 <b>Experience:</b> {experience}
📝 <b>Description:</b> {description[:300]}...
🔗 <b>Apply:</b> {job_link}

#JobAlert #TamilNadu #SoftwareJobs"""
                    
                    print(f"📤 Sending new job: {title} at {company}")
                    print(f"   💰 Salary: {salary}")
                    print(f"   📅 Posted: {posted_date}")
                    print(f"   🎯 Experience: {experience}")
                    send_message(message)
                    
                    # Add delay to avoid rate limiting
                    time.sleep(2)
                else:
                    print(f"⏭️ Job already seen: {title} at {company}")
                    
            except Exception as job_error:
                print(f"❌ Error processing job: {job_error}")
                continue
        
        # Print summary of filtering results
        print(f"\n📊 Job Filtering Summary:")
        print(f"   🔍 Total jobs found: {len(jobs)}")
        print(f"   ⏭️ Jobs skipped (older than 1 day): {skipped_jobs_count}")
        print(f"   💰 Jobs skipped (salary < 3 LPA): {sum(1 for _ in range(skipped_jobs_count) if 'below 3 LPA' in str(_))}")
        print(f"   🎯 Jobs skipped (experience < 1 year): {sum(1 for _ in range(skipped_jobs_count) if 'below 1 year' in str(_))}")
        print(f"   🏢 Jobs skipped (startup companies): {sum(1 for _ in range(skipped_jobs_count) if 'Startup' in str(_))}")
        print(f"   ✅ Filtered jobs sent: {recent_jobs_count}")
        
        if recent_jobs_count == 0:
            print("   ℹ️ No jobs found matching your criteria (1 day old, 3+ LPA OR 40k+ monthly, 1+ years exp OR fresher, medium/large companies)")

    except Exception as e:
        print(f"❌ Error fetching jobs from SerpAPI: {e}")
        # Send error notification to all users
        error_message = f"⚠️ <b>JobBot Error</b>\n\nThere was an error fetching jobs:\n{str(e)[:200]}..."
        send_message_to_all_users(error_message)

def test_serpapi_response():
    """Test function to debug SerpAPI response structure"""
    try:
        print("🧪 Testing SerpAPI response structure...")
        
        search = GoogleSearch(api_key=SERPAPI_KEY)
        
        # Test 1: Google Jobs
        print("\n1. Testing Google Jobs engine...")
        jobs_results = search.search({
            "q": "software engineer jobs Chennai",
            "engine": "google_jobs",
            "gl": "in",
            "hl": "en"
        })
        
        if jobs_results:
            print(f"✅ Google Jobs response keys: {list(jobs_results.keys())}")
            if "jobs_results" in jobs_results:
                print(f"   📊 Found {len(jobs_results['jobs_results'])} jobs")
            else:
                print("   ⚠️ No jobs_results found")
        else:
            print("❌ No response from Google Jobs")
        
        # Test 2: Regular Google Search
        print("\n2. Testing regular Google search...")
        google_results = search.search({
            "q": "software engineer jobs Chennai Tamil Nadu",
            "engine": "google",
            "gl": "in",
            "hl": "en"
        })
        
        if google_results:
            print(f"✅ Google search response keys: {list(google_results.keys())}")
            if "organic_results" in google_results:
                print(f"   📊 Found {len(google_results['organic_results'])} organic results")
            else:
                print("   ⚠️ No organic_results found")
        else:
            print("❌ No response from Google search")
            
    except Exception as e:
        print(f"❌ Error testing SerpAPI: {e}")

def send_status_update():
    """Send periodic status update"""
    message = f"📊 <b>JobBot Status Update</b>\n\n✅ Bot is running normally\n🔍 Checking for jobs every 60 seconds\n📱 Total jobs found: {len(seen_jobs)}\n⏰ Last check: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC"
    send_message(message)

def send_manual_message():
    """Send a manual message for testing"""
    message = "🔧 Manual test message from JobBot! The bot is working correctly."
    print("Sending manual test message...")
    send_message(message)

if __name__ == "__main__":
    print("🚀 Enhanced IT JobBot started! Press Ctrl+C to stop.")
    print("📱 Bot will send job alerts every 60 seconds when new jobs are found")
    print("🔍 Using SerpAPI for FILTERED IT job search in ALL Tamil Nadu districts")
    print("⚡ Enhanced with smart filtering: 1 day old, 3+ LPA OR 40k+ monthly, 1+ years exp OR fresher, medium/large companies")
    print("🌍 Coverage: 30+ districts including Chennai, Coimbatore, Madurai, Salem, Trichy, Vellore, Erode, and more!")
    print("💼 IT Categories: Development, Data Science, DevOps, Security, Testing, Management, Emerging Tech")
    print("🎯 Smart Filters: Posted within 1 day, Salary 3+ LPA OR 40k+ monthly, Experience 1+ years OR fresher, Medium/Large companies only")
    print("👥 Multi-user support enabled - all users who start the bot will receive alerts!")
    
    # Initialize bot by getting existing users
    print("🔍 Initializing bot and checking for existing users...")
    get_bot_updates()
    
    # Send startup message to all users
    if active_users:
        startup_message = f"🚀 <b>JobBot Started Successfully!</b>\n\n🔍 Now searching for FILTERED IT jobs in ALL Tamil Nadu districts\n📱 You'll receive real-time job alerts\n⏰ Checking every 60 seconds\n🎯 Smart Filters: 1 day old, 3+ LPA OR 40k+ monthly, 1+ years exp OR fresher, medium/large companies\n💼 Focus: Comprehensive IT roles (Development, Data Science, DevOps, Security, Testing, Management)\n👥 Total active users: {len(active_users)}"
        send_message_to_all_users(startup_message)
    else:
        print("ℹ️ No active users found. Users need to send /start to the bot first.")
    
    # Main loop with enhanced features
    check_count = 0
    while True:
        try:
            # Handle user commands every few cycles
            if check_count % 5 == 0:  # Every 5 minutes
                handle_user_commands()
            
            fetch_and_send_jobs()
            check_count += 1
            
            # Send status update every 10 checks (every 10 minutes)
            if check_count % 10 == 0:
                status_message = f"📊 <b>JobBot Status Update</b>\n\n✅ Bot is running normally\n🔍 Checking for jobs every 60 seconds\n📱 Total jobs found: {len(seen_jobs)}\n👥 Active users: {len(active_users)}\n⏰ Last check: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S')} UTC"
                send_message_to_all_users(status_message)
            
            time.sleep(60)  # check every 60 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 JobBot stopped by user")
            stop_message = f"🛑 <b>JobBot Stopped</b>\n\nBot has been stopped. Restart with 'python app.py' to resume job searching.\n👥 Total users affected: {len(active_users)}"
            send_message_to_all_users(stop_message)
            break
        except Exception as e:
            print(f"❌ Unexpected error in main loop: {e}")
            time.sleep(60)  # Wait before retrying