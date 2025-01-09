const formContainer = document.getElementById('form-container');
const weightInputGroup = document.getElementById('weight_lose/gain');
const nameInput = formContainer.querySelector('#name');
function toggleDesiredWeight() {
    const goal = document.querySelector('input[name="goal"]:checked').value;
    const desiredWeightGroup = document.getElementById('desired-weight-group');
    if (goal === 'lose' || goal === 'gain') {
        desiredWeightGroup.style.display = 'block';
    } else {
        desiredWeightGroup.style.display = 'none';
    }
}

function toggleOtherSport() {
    const otherSport = document.getElementById('other-sport');
    const otherSportInput = document.getElementById('other-sport-input');
    if (otherSport.checked) {
        otherSportInput.style.display = 'inline-block';
    } else {
        otherSportInput.style.display = 'none';
    }
}

function validateForm() {
    const goal = document.querySelector('input[name="goal"]:checked');
    const currentWeight = parseFloat(document.getElementById('weight').value);
    const desiredWeight = parseFloat(document.getElementById('desired_weight').value);
    const days = parseInt(document.getElementById('days').value);

    if (goal && (goal.value === 'lose' || goal.value === 'gain')) {
        if ((goal.value === 'lose' && desiredWeight >= currentWeight) || 
            (goal.value === 'gain' && desiredWeight <= currentWeight)) {
            alert(`You want to ${goal.value} weight, but your desired weight doesn't match your goal.`);
            return; // Exit the function if the goal doesn't match the desired weight
        }

        const maxRatePerDay = 0.1; // 200 grams per day
        const weightDifference = Math.abs(currentWeight - desiredWeight);
        let maxDays;
        
        // Check if the user is trying to lose or gain weight
        if (desiredWeight < currentWeight) {
            // Weight loss scenario
            maxDays = weightDifference / maxRatePerDay;
            if (days < maxDays) {
                alert("The number of days is too short to safely achieve your desired weight. Please adjust.");
                return; // Exit the function if validation fails
            }
        } else if (desiredWeight > currentWeight) {
            // Weight gain scenario
            maxDays = weightDifference / maxRatePerDay;
            if (days < maxDays) {
                alert("The number of days is too short to safely achieve your desired weight. Please adjust.");
                return; // Exit the function if validation fails
            }
        } else {
            // No change in weight required
            alert("Your current weight is already at the desired weight!");
            return; // Exit the function if no change is needed
        }

        // If everything is valid, call the showLoading function
        showLoading(); // Now show loading if all conditions are met
    }
}

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
    const gym = document.querySelector('input[name="gym"]:checked').value; // Gym data
    const desiredWeight = document.getElementById('desired_weight') ? document.getElementById('desired_weight').value : ''; // Desired weight
    const days = document.getElementById('days') ? document.getElementById('days').value : ''; // Days to reach desired weight
    const sport = document.querySelector('input[name="sport"]:checked') ? document.querySelector('input[name="sport"]:checked').value : ''; // Sport preference
    const description = document.getElementById('description').value; // Description

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
            activityLevel: activityLevel,
            gym: gym,
            desiredWeight: desiredWeight, // Desired weight
            days: days, // Number of days to achieve goal
            sport: sport, // Sport preference
            description: description // Description
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
