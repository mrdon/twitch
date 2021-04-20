import asyncio

from wled import WLED


async def main():
    """Show example on controlling your WLED device."""
    async with WLED("10.76.5.152") as led:
        device = await led.update()
        print(device.info.version)

        await led.master(on=False)
        await asyncio.sleep(5)
        await led.master(on=True)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
