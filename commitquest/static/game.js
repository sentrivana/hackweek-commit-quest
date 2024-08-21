"use strict";
let canvas;
let context;

let secondsPassed = 0;
let oldTimestamp = 0;
const scaleFactor = 3.0;

let fetchedState;
let characters;
let boss;
let level;

let repoOwner;
let repoName;

const sprites = ['Orc-Idle', 'Soldier-Idle'];


window.onload = init;

function init() {
    canvas = document.getElementById('game');
    context = canvas.getContext('2d');
    context.imageSmoothingEnabled = false;

    repoOwner = document.getElementById('repo-owner').innerText;
    repoName = document.getElementById('repo-name').innerText;

    initGameState();

    // window.requestAnimationFrame(gameLoop);
}

async function fetchGameState() {
    // Fetch game state
    console.log(`Fetching game state for ${repoOwner}/${repoName}`);
    const res = await fetch(`/api/${repoOwner}/${repoName}/state`)
    fetchedState = await res.json();
    console.log(fetchedState);
}

function initGameState() {
    fetchGameState();

    // Init characters
    let id = 0;
    characters = {};

    for (const character in fetchedState) {
        const spriteName = sprites[Math.floor(Math.random() * sprites.length)];
        characters[character] = {
            "id": id,
            "name": character,
            "commits": fetchedState[character],
            "sprite": {
                "image": loadSprite(spriteName),
                "id": spriteName,
                "frame": 0,
                "maxFrame": 6,
            },
        };
        id += 1;
    }

    console.log(characters);
}

function gameLoop(timestamp) {
    secondsPassed = Math.min(timestamp - oldTimestamp / 1000, 0.1);
    oldTimestamp = timestamp;

    update();
    draw();

    window.requestAnimationFrame(gameLoop);
}

function update(secondsPassed) {
    for (const character in characters) {
        let charState = characters[character];
        charState["sprite"]["frame"] = (charState["sprite"]["frame"] + 1) % charState["sprite"]["maxFrame"];
    }
}

function draw() {
    context.clearRect(0, 0, canvas.width, canvas.height);

    drawEnvironment();
    drawBoss();

    for (const character in characters) {
        drawCharacter(character);
    }
}

function loadSprite(url) {
    let image = new Image();
    image.onload = function() {
        context.drawImage(image, 10, 10);
    };
    image.src = `/static/images/${url}.png`;
    return image;
}

function drawCharacter(character) {
    const charState = characters[character];

    let numColumns = 6;
    let numRows = 1;

    let frameWidth = charState["sprite"]["image"].width / numColumns;
    let frameHeight = charState["sprite"]["image"].height / numRows;

    let column = charState["sprite"]["frame"] % numColumns;
    let row = Math.floor(charState["sprite"]["frame"] / numColumns);

    context.drawImage(
        // source
        charState["sprite"]["image"],
        column * frameWidth,
        row * frameHeight,
        frameWidth,
        frameHeight,
        // destination
        charState["id"] * 50,
        100,
        frameWidth * scaleFactor,
        frameHeight * scaleFactor
    );
}

function drawBoss() {

}

function drawEnvironment() {

}
