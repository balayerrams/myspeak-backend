import asyncio

from dotenv import load_dotenv
from openai import AsyncOpenAI


load_dotenv()

async def main():
    client = AsyncOpenAI()

    response = await client.responses.create(
        model="gpt-5-mini",
        instructions="Respond briefly and directly.",
        input="Reply with exactly: MySpeak AI Connected",
        reasoning={"effort": "minimal"},
        max_output_tokens=300,
        store=False,
    )

    print("Status:", response.status)
    print("Response:", repr(response.output_text))
    print("Input tokens:", response.usage.input_tokens)
    print("Output tokens:", response.usage.output_tokens)
    print("Output details:", response.usage.output_tokens_details)

asyncio.run(main())