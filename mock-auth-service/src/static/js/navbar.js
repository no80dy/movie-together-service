document.addEventListener('DOMContentLoaded', function() {
    async function getUser() {
        const response = await fetch("http://localhost:8000/auth/api/v1/users/protected", {});
        const data = await response.json();
        return data['username'];
    };

    getUser().then((username) => {
        let bar = document.querySelector('#navbarTogglerTQL');
        if (username !== null) {
            bar.innerHTML =
                '<ul class="nav navbar-nav ms-auto justify-content-end>\n' +
                    '<li class="nav-item">\n' +
                        `<a href="#" onclick="return false;" class="nav-link">[${username}]</a>\n` +
                    '</li>\n' +
                    '<li class="nav-item"">\n' +
                        '<a href="http://localhost:8000/auth/api/v1/users/logout" class="nav-link">Logout</a>\n' +
                    '</li>\n' +
                '</ul>\n'
        } else {
            bar.innerHTML =
                '<ul class="nav navbar-nav ms-auto" justify-content-end>\n' +
                    '<li class="nav-item">\n' +
                        '<a href="http://localhost:8000/auth/api/v1/users/login" class="nav-link">Login</a>\n' +
                    '</li>\n' +
                    '<li class="nav-item">\n' +
                        '<a href="#" onclick="return false;" class="nav-link">Register</a>\n' +
                    '</li>\n' +
                '</ul>\n'
        }
    });
});