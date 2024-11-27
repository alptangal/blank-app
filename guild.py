import asyncio


async def getBasic(guild):
    obj={}
    try:
        for category in guild.categories:
            if 'rtmp-servers' in category.name:
                for channel in category.channels:
                    if 'trovo' in channel.name.lower():
                        obj['forum']=channel
                break
        #print([msg async for msg in obj['streamlit']['rawCh'].history()])
        return obj
    except Exception as err:
        print(err)
        return False