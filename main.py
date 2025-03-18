import asyncio
from lead_gen import LeadGenerator
import nest_asyncio

nest_asyncio.apply()


async def main():
    """Main function to demonstrate usage."""
    keywords = ['real estate company in germany', 'construction company in germany', 'realtor in berlin', 
                'real estate agent in berlin', 'interior designers and decor', 'property developer in berlin']
    lead_gen = LeadGenerator(keywords)

    try:
        # Process leads sequentially
        async for lead_result in lead_gen.fetch_search_results():
            try:
                # Fetch contact information for each lead
                contacts = [contact async for contact in lead_gen.fetch_contact_results(lead_result.get('Website', ''))]
                
                if contacts and contacts[0].get('email'):
                    lead_result.update(contacts[0])
                    output = lead_gen.generate_email_content(lead_result)
                    if output:
                        lead_gen.send_email(lead_result['email'],output['subject'], output['body'])
                        print(f"Email Sent Successfully to {lead_result['Company Name']}")
                    else:
                        continue
                else:
                    continue
            except Exception as e:
                lead_gen.logger.error(
                    f"Error processing {lead_result['Website']}: {str(e)}"
                )
                continue
        return lead_result

    except Exception as e:
        lead_gen.logger.error(f"Main function error: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main())