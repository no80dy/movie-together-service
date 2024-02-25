import _ from "lodash";
import Hls from "hls.js"
import Plyr from "plyr"

function component() {
    const element = document.createElement('div');
    element.innerHTML = _.join(["Hello", "webpack"], " ");
    return element;
}

document.body.appendChild(component());

// const ws = new WebSocket("ws://localhost:8000/ws");
// ws.onmessage = function (event) {
//     console.log(event.data);
// };

document.addEventListener("DOMContentLoaded", () => {
    const video = document.getElementById("video");
    const source_host = "https://test-streams.mux.dev/x36xhzz/x36xhzz.m3u8";
    if(Hls.isSupported()) {
        const hls = new Hls();
        const playerOptions = {};
        hls.loadSource(source_host);
        hls.on(Hls.Events.MANIFEST_PARSED, function (event, data) {
            const availableQualities = hls.levels.map((l) => l.height);
            playerOptions.controls = [
                "play-large", "restart", "rewind", "play", "fast-forward", "progress", "current-time", "duration",
                "mute", "volume", "captions", "settings", "pip", "airplay", "fullscreen"
            ];
            playerOptions.quality = {
                default: availableQualities[0],
                options: availableQualities,
                forced: true,
                onChange: (e) => updateQuality(e)
            };
            new Plyr(video, playerOptions);
        });
        hls.attachMedia(video);
        window.hls = hls;
    }
    function updateQuality() {
        window.hls.levels.forEach((level, levelIndex) => {
            window.hls.currentLevel = levelIndex;
        });
    }
});
