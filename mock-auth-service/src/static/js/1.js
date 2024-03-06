document.addEventListener('DOMContentLoaded', function() {
    async function createParty(event) {
        film_id = event.srcElement.id;
        console.log('film_id', film_id);
        user_id = document.querySelector('#user_id').value;
        console.log('user_id:', user_id);
    };
});
