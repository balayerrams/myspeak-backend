
import asyncio

from app.services.reminder_refinement_service import (
    ReminderRefinementService,
)


async def main():
    service = ReminderRefinementService()

    test_cases = [
        {
            "name": "Time-specific reminder",
            "original": "Take your medicine at 8 PM",
            "translated": "రాత్రి 8 గంటలకు మీ మందులు తీసుకోండి",
            "language": "te",
        },
        {
            "name": "Negative instruction",
            "original": "Do not take medicine before breakfast",
            "translated": "అల్పాహారానికి ముందు మందులు తీసుకోకండి",
            "language": "te",
        },
        {
            "name": "Hindi reminder",
            "original": "It's time to drink water",
            "translated": "पानी पीने का समय हो गया है",
            "language": "hi",
        },
    ]

    for case in test_cases:
        print("\n------------------------------")
        print("Test:", case["name"])
        print("Original:", case["original"])
        print("Google Translation:", case["translated"])

        refined = await service.refine(
            original_message=case["original"],
            translated_message=case["translated"],
            target_language=case["language"],
        )

        print("AI Refined:", refined)


if __name__ == "__main__":
    asyncio.run(main())
