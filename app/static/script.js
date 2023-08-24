const form = document.getElementById('username-form');
const userProfileDiv = document.getElementById('user-profile');
const repositoriesDiv = document.getElementById('repositories');

form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const username = document.getElementById('username').value;

    try {
        const userProfileResponse = await fetch(`/api/user/${username}`);
        const userProfileData = await userProfileResponse.json();

        const repositoriesResponse = await fetch(`/api/repositories/${username}`);
        const repositoriesData = await repositoriesResponse.json();

        // Update user profile and repositories sections
        userProfileDiv.innerHTML = `
            <img src="${userProfileData.avatar_url}" alt="${username} Avatar">
            <p>Username: ${userProfileData.login}</p>
            <p>Followers: ${userProfileData.followers}</p>
            <p>Repositories: ${userProfileData.public_repos}</p>
        `;

        repositoriesDiv.innerHTML = '';
        repositoriesData.forEach(repository => {
            repositoriesDiv.innerHTML += `
                <div class="repository">
                    <h3>${repository.name}</h3>
                    <p>${repository.description || 'No description available.'}</p>
                    <p>Stars: ${repository.stargazers_count}</p>
                    <p>Forks: ${repository.forks_count}</p>
                </div>
            `;
        });

        // Display user profile and repositories sections
        userProfileDiv.style.display = 'block';
        repositoriesDiv.style.display = 'block';
    } catch (error) {
        console.error('Error fetching data:', error);
        // Handle error and display error message
    }
});

