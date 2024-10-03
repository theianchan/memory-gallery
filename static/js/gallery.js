const skippedCells = [3, 5, 9, 11, 13, 17, 19];
const availableCells = [1, 2, 4, 6, 7, 8, 10, 12, 14, 15, 16, 18, 20, 21];
let allMemories = [];
let lastNewMemoryTime = 0;

function getRandom(list, elements){
    /**
     * Get a number of elements from a list.
     */
    
    return list.sort(() => 0.5 - Math.random()).slice(0, elements);
}

function fetchMemories() {
    /**
     * Fetch all memories from the server.
     */

    $.getJSON('/memories', function(data) {
        console.log('/memories returned ', data);

        allMemories = data;
        const displayMemories = getRandom(allMemories, availableCells.length);

        populateGallery(displayMemories);
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

function populateGallery(memories) {
    /**
     * Populate the gallery.
     */

    let cells = getRandom(availableCells, memories.length);

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
     * Check for working status and display it in the status cell.
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
     * Check for new memories and add them to the gallery cells.
     */

    $.getJSON('/memories', function(data) {
        console.log('/memories returned ', data);

        if (data.length > allMemories.length) {
            const newMemories = data.slice(allMemories.length);
            allMemories = data;
            console.log('New memories:', newMemories);

            populateGallery(newMemories);
        }
    });
}

$(document).ready(function() {
    fetchMemories();
    setInterval(checkWorkingStatus, 5000);
    setInterval(checkForNewMemories, 5000);
});