// script.js

document.getElementById('githubForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const username = document.getElementById('username').value;
    const resultDiv = document.getElementById('result');

    try {
        const response = await fetch(`/get_github_stats/${username}`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json'
            }
        });

        if (response.status === 200) {
            const data = await response.json();
            resultDiv.innerHTML = `
                <h2>${data.name}</h2>
                <p>Followers: ${data.followers}</p>
                <p>Following: ${data.following}</p>
                <p>Public Repositories: ${data.public_repos}</p>
            `;
        } else if (response.status === 404) {
            resultDiv.innerHTML = '<p>User not found.</p>';
        } else {
            resultDiv.innerHTML = '<p>An error occurred. Please try again later.</p>';
        }
    } catch (error) {
        resultDiv.innerHTML = '<p>An error occurred. Please try again later.</p>';
    }
});

