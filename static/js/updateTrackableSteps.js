const UPDATE_FREQUENCY_MS = 2500;
const FADE_TIME_MS = 500;

const STEPS = [
    "Track car maintenance records",
    "Track gym sessions",
    "Track food diary",
    "Track your haircuts",
    "Track your reading list",
    "Track sleep quality",
    "Track medical appointments",
    "Track pet care routines",
    "Track household chores",
    "Track your weight",
    "Track kids' activities",
    "Track movies and shows you've watched",
    "Track personal goals and habits",
    "Track gratitude journaling",
    "Track project milestones",
    "Track home improvement tasks",
    "Track medication schedules"
];

document.addEventListener("DOMContentLoaded", function() {
    const dynamicTextElement = document.getElementById("trackable_steps");

    function updateText() {
        // Fade out the current text
        dynamicTextElement.style.transition = "opacity 0.5s ease-out";
        dynamicTextElement.style.opacity = 0;

        setTimeout(() => {
            // Update the text with a random element and fade in
            const randomIndex = Math.floor(Math.random() * STEPS.length);
            dynamicTextElement.textContent = STEPS[randomIndex];
            dynamicTextElement.style.opacity = 1;
            dynamicTextElement.style.transition = "opacity 0.5s ease-in";
        }, FADE_TIME_MS);
    }

    setInterval(updateText, UPDATE_FREQUENCY_MS);
    updateText();
});