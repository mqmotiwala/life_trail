const UPDATE_FREQUENCY_MS = 2500;
const FADE_TIME_MS = 500;

const STEPS = [
    "car maintenance records",
    "gym sessions",
    "your food diary",
    "haircuts",
    "books you've read",
    "sleep quality and duration",
    "medical appointments",
    "pet care routines",
    "household chores",
    "your weight over time",
    "kids' activities",
    "movies and shows you've watched",
    "personal goals and progress",
    "gratitude journaling entries",
    "project milestones",
    "home improvement tasks",
    "meal times",
    "workouts and exercise routines",
    "daily water intake",
    "caffeine consumption",
    "medications taken",
    "hygiene routines",
    "grooming and skincare",
    "hobbies and activities",
    "purchases and spending habits",
    "events you've attended",
    "travel experiences",
    "mood changes and mental health",
    "meditation sessions",
    "commuting times",
    "gaming sessions",
    "TV shows you've watched",
    "movies you've watched",
    "volunteer activities",
    "intermittent fasting schedules",
    "pet feeding times",
    "laundry cycles",
    "sleep disruptions",
    "work shifts",
    "health symptoms",
    "dentist visits",
    "grocery shopping frequency",
    "physical therapy exercises",
    "energy levels",
    "new recipes tried",
    "bike rides",
    "car refueling",
    "friend catch-ups",
    "flu shots or vaccinations",
    "therapist sessions",
];

document.addEventListener("DOMContentLoaded", function() {
    const dynamicTextElement = document.getElementById("exampleStepsToTrack");
    let isFirstUpdate = true;

    function updateText() {
        if (!isFirstUpdate) {
            // Fade out the current text
            dynamicTextElement.style.transition = "opacity 0.5s ease-out";
            dynamicTextElement.style.opacity = 0;
        }

        setTimeout(() => {
            // Update the text with a random element and fade in
            const randomIndex = Math.floor(Math.random() * STEPS.length);
            dynamicTextElement.textContent = STEPS[randomIndex];
            dynamicTextElement.style.opacity = 1;
            dynamicTextElement.style.transition = "opacity 0.5s ease-in";
            isFirstUpdate = false;
        }, isFirstUpdate ? 0 : FADE_TIME_MS);
    }

    setInterval(updateText, UPDATE_FREQUENCY_MS);
    updateText();
});