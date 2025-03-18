from apify_client import ApifyClientAsync
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import asyncio
import aiohttp
import ollama
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
import nest_asyncio
import os
import pandas as pd

nest_asyncio.apply()
load_dotenv()

class LeadGenerator:
    def __init__(self, keywords:List[str]): 
        self.keywords = keywords
        self.logger = logging.getLogger(__name__)
        self.apify_token = os.getenv('APIFY_KEY')
        self.client = ApifyClientAsync(self.apify_token)
        self.email_config = {
            'sender': os.getenv('SENDER_EMAIL'),
            'recipient':os.getenv('RECIPIENT'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'smtp_server': 'smtp.gmail.com',
            'port': 465
        }
        
        
            
    async def fetch_search_results(self) -> Optional[pd.DataFrame]:
        query = "\n".join(self.keywords)
        run_input = {
            "queries": query,
            "resultsPerPage": 2,
            "maxPagesPerQuery": 1,
            "languageCode": "de",
            "countryCode": 'de',
            # ... rest of config
        }
        try:
            actor_client = self.client.actor('apify/google-search-scraper')
            call_result = await actor_client.call(run_input=run_input)
            if not call_result:
                raise ValueError('Search actor run failed')
                
            dataset_client = self.client.dataset(call_result['defaultDatasetId'])
            async for item in dataset_client.iterate_items():
                for result in item.get('organicResults', []):
                    yield {
                        'Company Name': result.get('title', ''),
                        'Website': result.get('url', ''),
                        'Description': result.get('description', ''),
                    }
        except Exception as e:
            self.logger.error(f"Error fetching search results: {str(e)}")
            raise
            
    async def fetch_contact_results(self, url: str) -> Optional[pd.DataFrame]:
        # query = "\n".join(keywords)
        run_input = {
            "startUrls": [{ "url": url }],
            "maxRequestsPerStartUrl": 1,
            "maxDepth": 5,
            "maxRequests": 9999999,
            "sameDomain": True,
            "considerChildFrames": True,
            "useBrowser": False,
            "waitUntil": "domcontentloaded",
            "proxyConfig": { "useApifyProxy": True },
        }

        try:
            actor_client = self.client.actor('vdrmota/contact-info-scraper')
            call_result = await actor_client.call(run_input=run_input)
            if not call_result:
                raise ValueError('Search actor run failed')
                
            dataset_client = self.client.dataset(call_result['defaultDatasetId'])
            async for item in dataset_client.iterate_items():
                emails = item.get('emails', [])
                if emails != []:
                    yield {'email': emails[0]}
                else:
                    yield {'email': None}
        except Exception as e:
            self.logger.error(f"Error fetching contact results: {str(e)}")
            raise
    
    
    def generate_email_content(self, prospect_details: dict) -> Dict[str, str]:
        template = f"""
                You are a professional prospector representing ExposéProfi, reaching out to a potential client.  
                Using the details below, generate a personalized email outreach message in German.

                ### PROSPECTOR DETAILS:
                ----------------------
                - Website: exposéprofi.de  
                - Company Name: ExposéProfi
                - Email: contact@exposéprofi.de
                - Description:  The real estate market is constantly evolving, and customer expectations are higher than ever.  
                                    As a property developer or real estate agent, you must present projects attractively and convincingly.  
                                    Traditional abstract drawings and sketches no longer suffice—clients seek emotional, immersive representations.  
                                    ExposéProfi, a leader in high-quality 3D real estate visualization, helps you showcase projects with stunning visuals  
                                    that enhance your brand presence and set you apart from the competition.  
                                    We combine innovation and expertise to support your success in real estate marketing.  

                ### PROSPECT DETAILS:
                -------------------
                {prospect_details}

                ### EMAIL REQUIREMENTS:
                - Tone: Professional, friendly, and engaging.  
                - Content: Concise, compelling, and relevant to the prospect's needs.  
                - Value Proposition: Clearly highlight how ExposéProfi's services benefit the prospect’s business or project.  
                - Call to Action: Encourage a response or next step (e.g., a meeting, call, or demo).  
                - Closing: Include a polite sign-off with contact details.  
                - Restrictions: Do not invent names or use information beyond what is provided.  

                ### OUTPUT FORMAT:
                Return a JSON object with exactly two keys: "Subject" and "Body", where:  
                - "Subject": A compelling subject line in German.  
                - "Body": A well-structured email body in German.  

                The output must be a valid JSON object, with no extra text, commentary, or formatting outside the JSON structure.  

                #### Example Output Format:
                ```json
                {{
                    "Subject": "subject of the email",
                    "Body": "body of the email"
                }}
            """
        response = ollama.generate(model='llama3.2:latest', prompt=template)

        try:
            result = json.loads(response['response'])  # Convert string to dictionary
            return {
                'subject': result.get('Subject', ''),
                'body': result.get('Body', '')
            }
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing Ollama response: {str(e)}")
            return None


    
    def send_email(self, subject: str, body: str) -> bool:
        if not self.email_config['sender'] or not self.email_config['password']:
            self.logger.error("Email credentials missing")
            return False
            
        msg = MIMEMultipart()
        msg['From'] = self.email_config['sender']
        msg['To'] = self.email_config['recipient']
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        try:
            with smtplib.SMTP_SSL(
                self.email_config['smtp_server'],
                self.email_config['port']
            ) as server:
                server.login(
                    self.email_config['sender'],
                    self.email_config['password']
                )
                server.send_message(msg)
            return True
        except Exception as e:
            self.logger.error(f"Error sending email: {str(e)}")
            return False