/* UPDATE THESE VALUES TO MATCH YOUR SETUP */

const PROCESSING_STATS_API_URL = "http://microservice-3855.westus2.cloudapp.azure.com:8100/stats"
const ANALYZER_API_URL = {
    stats: "http://microservice-3855.westus2.cloudapp.azure.com:8200/stats",
    ship: "http://microservice-3855.westus2.cloudapp.azure.com:8200/ship_arrival",
    container: "http://microservice-3855.westus2.cloudapp.azure.com:8200/container_processing"
}

// This function fetches and updates the general statistics
const makeReq = (url, cb) => {
    fetch(url)
        .then(res => res.json())
        .then((result) => {
            console.log("Received data: ", result)
            cb(result);
        }).catch((error) => {
            updateErrorMessages(error.message)
        })
}

const updateCodeDiv = (result, elemId) => document.getElementById(elemId).innerText = JSON.stringify(result)

const getLocaleDateStr = () => (new Date()).toLocaleString()

const getStats = () => {
    document.getElementById("last-updated-value").innerText = getLocaleDateStr()
    
    makeReq(PROCESSING_STATS_API_URL, (result) => {
        const output = `Heaviest Container: ${result.heaviest_container}\n` +
                   `Lightest Container: ${result.lightest_container}\n` +
                   `Last Updated: ${result.last_updated}\n` +
                   `Max Containers Onboard: ${result.max_containers_onboard}\n` +
                   `Containers Processed: ${result.num_containers_proccessed}\n` +
                   `Ships Arrived: ${result.num_ships_arrived}`;

        document.getElementById("processing-stats").innerText = output;
    });




    makeReq(ANALYZER_API_URL.stats, (result) => {
        const output = `Container Events: ${result.num_container_events}\n` +
                   `Ship Events: ${result.num_ship_events}`;
                   
        document.getElementById("analyzer-stats").innerText = output;

    });
    // makeReq(ANALYZER_API_URL.ship, (result) => updateCodeDiv(result, "event-ship"))
    // makeReq(ANALYZER_API_URL.container, (result) => updateCodeDiv(result, "event-container"))

    const randomIndex = Math.floor(Math.random() * 25);
    const containerURL = `${ANALYZER_API_URL.container}?index=${randomIndex}`;
    const shipURL = `${ANALYZER_API_URL.ship}?index=${randomIndex}`;

    makeReq(containerURL, (result) => updateCodeDiv(result, "event-container"));
    makeReq(shipURL, (result) => updateCodeDiv(result, "event-ship"));


}

const updateErrorMessages = (message) => {
    const id = Date.now()
    console.log("Creation", id)
    msg = document.createElement("div")
    msg.id = `error-${id}`
    msg.innerHTML = `<p>Something happened at ${getLocaleDateStr()}!</p><code>${message}</code>`
    document.getElementById("messages").style.display = "block"
    document.getElementById("messages").prepend(msg)
    setTimeout(() => {
        const elem = document.getElementById(`error-${id}`)
        if (elem) { elem.remove() }
    }, 7000)
}

const setup = () => {
    getStats()
    setInterval(() => getStats(), 4000) // Update every 4 seconds
}

document.addEventListener('DOMContentLoaded', setup)