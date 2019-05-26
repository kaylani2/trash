loop = asyncio.get_event_loop ()
responseArray = asyncio.ensure_future (run (cardUrlArray))
loop.run_until_complete (responseArray)
print ('type: ', type (responseArray))
