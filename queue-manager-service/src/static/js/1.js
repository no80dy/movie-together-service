function isPartyReady(event) {
    fetch('http://localhost:8002/party-manager-service/api/v1/broker/party-creation', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
        if (data["redirect_url"] !== "None") {
            window.location.replace(data['redirect_url']);
        }
    })
};