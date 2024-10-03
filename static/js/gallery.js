const skippedCells = [3, 5, 9, 11, 13, 17, 19];
const availableCells = [1, 2, 4, 6, 7, 8, 10, 12, 14, 15, 16, 18, 20, 21];
let allMemories = [];
let lastNewMemoryTime = 0;

function fetchMemories() {
    /**
     * Fetch all memories from the server.
     */

    $.getJSON('/memories', function(data) {
        console.log('/memories returned ', data);

        allMemories = data;
        populateGallery();
    });
}

function displayMemory(cellNumber, imageFilename, caption) {
    /**
     * Display an image and caption in a gallery cell.
     */

    const $cell = $(`#cell-${cellNumber}`);
    $cell.empty();

    const messageHtml = `
        <img src="/static/images/generated/${imageFilename}" alt="">
        <p><em>Prompt: ${caption} --v 6.0 --ar 3:2</em></p>
    `;

    $cell.append(messageHtml);
}

function populateGallery() {
    /**
     * Populate the gallery.
     */

    let memories = allMemories.sort(() => 0.5 - Math.random()).slice(0, availableCells.length);
    let cells = availableCells.sort(() => 0.5 - Math.random()).slice(0, memories.length);

    for (let i = 0; i < memories.length; i++) {
        const memory = memories[i];
        const cellNumber = cells[i];
        displayMemory(cellNumber, memory.image_filename, memory.caption);
    }
}

function rotateImages() {
    /**
     * Rotate images in the gallery every 30 seconds. If an image is a new
     * memory and new memories were added <2 minutes ago, do not rotate
     * that image.
     */
}

function checkWorkingStatus() {
    /**
     * Check for new requests every 5 seconds. If there are new requests, 
     * add the working status to gallery cells.
     */

    const $cell = $(`#status`);

    $.getJSON('/working', function(data) {
        console.log('/working returned ', data);

        if (data === true) {
            $cell.empty();
            $cell.append('Working...');
        } else {
            $cell.empty();
        }
    });

}

function checkForNewMemories() {
    /**
     * Check for new memories every 5 seconds. If there are new memories,
     * add them to the gallery cells with working status.
     */
}

$(document).ready(function() {
    fetchMemories();
    setInterval(checkWorkingStatus, 5000);
});