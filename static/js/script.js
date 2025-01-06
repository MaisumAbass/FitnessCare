const formContainer = document.getElementById('form-container');
const weightInputGroup = document.getElementById('weight_lose/gain');
const nameInput = formContainer.querySelector('#name');
function showLoading() {
    // Display user name and hide the form
    document.querySelector('.user').innerText = 'Hello ' + nameInput.value;
    document.querySelector('.form-container').style.display = 'none';
    document.getElementById('loading').style.display = 'block';

    // Collect input values
    const height = document.getElementById('height').value;
    const weight = document.getElementById('weight').value;
    const diet = document.querySelector('input[name="diet"]:checked').value;
    const location = document.getElementById('location').value;
    const goal = document.querySelector('input[name="goal"]:checked').value;
    const age = document.getElementById('age').value;
    const activityLevel = document.getElementById('activity-level').value;

    // Send data to backend
    fetch('/get_plan', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            height: height,
            weight: weight,
            diet: diet,
            location: location,
            goal: goal,
            age: age,
            activityLevel: activityLevel
        })
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`Server returned status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        // Process and render diet plan
        if (data.diet_plan) {
            const dietTableHTML = generateDietPlanHTML(data.diet_plan);
            document.getElementById('diet_plan').innerHTML = dietTableHTML;
        } else {
            document.getElementById('diet_plan').innerHTML = "<p>No diet plan available.</p>";
        }

        // Process and render workout plan
        if (data.workout_plan) {
            const workoutTableHTML = generateWorkoutPlanHTML(data.workout_plan);
            document.getElementById('workout_plan').innerHTML = workoutTableHTML;
        } else {
            document.getElementById('workout_plan').innerHTML = "<p>No workout plan available.</p>";
        }

        // Hide loading spinner and show homepage
        document.getElementById('loading').style.display = 'none';
        document.getElementById('homepage').style.display = 'block';
    })
    .catch(error => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('homepage').style.display = 'block';
        document.getElementById('diet_plan').innerHTML = error;
        alert('Failed to fetch the plan. Please try again later.');
    });
}

function generateDietPlanHTML(dietPlan) {
    let tableHTML = "<table><thead><tr><th>Day</th><th>Breakfast</th><th>Lunch</th><th>Snack</th><th>Dinner</th></tr></thead><tbody>";

    for (const [day, meals] of Object.entries(dietPlan)) {
        tableHTML += `<tr><td>${capitalize(day)}</td>`;
        tableHTML += `<td>${meals.breakfast || '-'}</td>`;
        tableHTML += `<td>${meals.lunch || '-'}</td>`;
        tableHTML += `<td>${meals.snack || '-'}</td>`;
        tableHTML += `<td>${meals.dinner || '-'}</td></tr>`;
    }

    tableHTML += "</tbody></table>";
    return tableHTML;
}

function generateWorkoutPlanHTML(workoutPlan) {
    let tableHTML = "<table><thead><tr><th>Day</th><th>Exercises</th></tr></thead><tbody>";

    for (const [day, exercises] of Object.entries(workoutPlan)) {
        tableHTML += `<tr><td>${capitalize(day)}</td><td>`;
        for (const [exercise, description] of Object.entries(exercises)) {
            tableHTML += `<p>${exercise}: ${description}</p>`;
        }
        tableHTML += "</td></tr>";
    }

    tableHTML += "</tbody></table>";
    return tableHTML;
}

function capitalize(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
