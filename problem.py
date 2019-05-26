
	async def fetch(url, session):
	    async with session.get(url) as response:
	        return await response.read()

	async def run (urls):
	    tasks = []

	    # Fetch all responses within one Client session,
	    # keep connection alive for all requests.
	    async with ClientSession () as session:
	        for url in urls:
	            task = asyncio.ensure_future (fetch (url, session))
	            tasks.append (task)

	        responses = await asyncio.gather(*tasks)
	        # you now have all response bodies in this variable

	    return responses
