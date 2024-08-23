"use strict";
let canvas;
let ctx;

const spriteRows = 1;
const frameWidth = 100;
const frameHeight = 100;
const scaleFactor = 5;
const border = 25;

let secondsPassed = 0;
let lastUpdate = 0;

let repoOwner;
let repoName;

// Game state as fetched from BE
const stateUpdateInterval = 10000;
let state;

// FE game state / consts
const drawUpdateInterval = 250;
let heroes;
let boss;
let level;


window.onload = init;

async function init() {
    canvas = document.getElementById('game');
    ctx = canvas.getContext('2d');
    ctx.imageSmoothingEnabled = false;

    repoOwner = document.getElementById('repo-owner').innerText;
    repoName = document.getElementById('repo-name').innerText;

    await fetchGameState();

    setTimeout(gameLoop, drawUpdateInterval);
}


async function fetchGameState() {
    console.log(`Fetching game state for ${repoOwner}/${repoName}`);
    const res = await fetch(`/api/${repoOwner}/${repoName}/state`);
    state = await res.json();
    console.log(state);

    setTimeout(fetchGameState, stateUpdateInterval);
}


function gameLoop() {
    update();
    draw();

    setTimeout(gameLoop, drawUpdateInterval);
}


function update() {
    const newLevel = updateLevel();
    updateHeroes(newLevel);
    updateBoss(newLevel);
}


function updateHeroes(reinit) {
    if (reinit || typeof heroes === "undefined") {
        heroes = {};
    }

    let existing = [];
    for (const hero in heroes) {
        existing.push(hero);
    }

    for (const hero in state.heroes) {
        if (!existing.includes(hero)) {
            const image = loadSprite("heroes", state.heroes[hero].sprite);
            image.onload = function() {
                const maxFrame = image.width / frameWidth;
                heroes[hero] = {
                    image: image,
                    frame: Math.floor(Math.random() * maxFrame),
                    maxFrame: maxFrame,
                };
            };
        }
    }

    let i = 0;
    for (const hero in heroes) {
        heroes[hero].frame = (heroes[hero].frame + 1) % heroes[hero].maxFrame;
        heroes[hero].pos = i;
        i += 1;
    }
}


function updateLevel() {
    if (typeof level === 'undefined') {
        level = state.level;
        level.image = loadSprite('bgs', level.environment);
    };

    if (state.level.seq != level.seq) {
        // new level
        console.log('New level!');
        level = state.level;
        level.image = loadSprite('bgs', level.environment);
        return true;
    };

    return false;
}


function updateBoss(reinit) {
    if (reinit || typeof boss === "undefined") {
        const image = loadSprite("bosses", state.boss.sprite);
        image.onload = function() {
            boss.maxFrame = image.width / frameWidth;
            boss.frame = Math.floor(Math.random() * boss.maxFrame);
        };
        boss = state.boss;
        boss.image = image;
    };

    boss.frame = (boss.frame + 1) % boss.maxFrame;
}

function draw() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    drawEnvironment();
    drawBoss();
    drawHeroes();
}


function loadSprite(type, filename) {
    let image = new Image();
    image.src = `/static/images/${type}/${filename}`;
    console.log(`Loaded sprite ${image.src}`);
    return image;
}


function drawHeroes() {
    for (const hero in heroes) {
        drawHero(hero);
    }

    if (Object.keys(heroes).length === 0) {
        let text = "<Go make some commits to fight the boss!>";
        ctx.fillStyle = "white";
        ctx.font = "20px serif";
        ctx.fillText(
            text,
            200,
            canvas.height - 200,
        );
    }
}

function drawHero(hero) {
    const heroInfo = heroes[hero];

    const destX = (heroInfo.pos % 8) * frameWidth / 4 * scaleFactor;
    const row = Math.floor(heroInfo.pos / 8);
    const destY = canvas.height - 1.25 * frameHeight * scaleFactor + row * frameHeight / 3 * scaleFactor;

    ctx.drawImage(
        // source
        heroInfo.image,
        heroInfo.frame * frameWidth,
        0,
        frameWidth,
        frameHeight,
        // destination
        destX,
        destY,
        frameWidth * scaleFactor,
        frameHeight * scaleFactor,
    );

    const name = state.heroes[hero].name;
    const effectiveSpriteDim = frameWidth / 3 * scaleFactor;
    const textWidth = ctx.measureText(name).width;

    ctx.fillStyle = "white";
    ctx.font = "20px serif";
    ctx.fillText(
        name,
        destX + effectiveSpriteDim + Math.max((effectiveSpriteDim - textWidth) / 2, 0),
        destY + frameHeight / 1.55 * scaleFactor,
    );
}


function drawBoss() {
    const padding = 100;
    const x = canvas.width - 500 - padding;
    const bossScaleFactor = scaleFactor * 3;

    // Sprite

    ctx.scale(-1, 1);
    ctx.drawImage(
        // source
        boss.image,
        boss.frame * frameWidth,
        0,
        frameWidth,
        frameHeight,
        // destination
        -1 * (x + (canvas.width - x - padding - frameWidth * bossScaleFactor) / 2),
        -frameHeight * bossScaleFactor / 7,
        -1 * frameWidth * bossScaleFactor,
        frameHeight * bossScaleFactor,
    );
    ctx.scale(-1, 1);

    // Name

    ctx.fillStyle = "white";
    ctx.font = "50px serif";

    const name = state.boss.name;
    const nameTextWidth = ctx.measureText(name).width;

    ctx.fillText(
        name,
        x + (canvas.width - x - padding - nameTextWidth) / 2,
        canvas.height - 250,
    );

    ctx.fillStyle = "white";
    ctx.font = "30px serif";

    const attribute = state.boss.attribute;
    const attributeTextWidth = ctx.measureText(attribute).width;

    ctx.fillText(
        attribute,
        x + (canvas.width - x - padding - attributeTextWidth) / 2,
        canvas.height - 250 + 40,
    );

    // Health bar

    const healthPercent = state.boss.health / state.boss.max_health;
    const healthBarHeight = 50;
    const healthBarWidth = Math.floor(500 * healthPercent);
    const healthBarY = canvas.height - healthBarHeight - padding;
    const healthBarBorder = 3;

    ctx.fillStyle = "black";
    ctx.fillRect(
        x - healthBarBorder * 2,
        healthBarY - healthBarBorder * 2,
        healthBarWidth + 4 * healthBarBorder,
        healthBarHeight + 4 * healthBarBorder,
    );
    ctx.fillStyle = "white";
    ctx.fillRect(
        x - healthBarBorder,
        healthBarY - healthBarBorder,
        healthBarWidth + 2 * healthBarBorder,
        healthBarHeight + 2 * healthBarBorder,
    );

    if (healthPercent > 0.63) {
        ctx.fillStyle = "green";
    } else if (healthPercent > 0.37) {
        ctx.fillStyle = "gold";
    } else if (healthPercent > 0.13) {
        ctx.fillStyle = "orange";
    } else {
        ctx.fillStyle = "red";
    }
    ctx.fillRect(
        x,
        healthBarY,
        healthBarWidth,
        healthBarHeight,
    );
}


function drawEnvironment() {
    ctx.drawImage(level.image, 0, 0, canvas.width, canvas.height);
}
