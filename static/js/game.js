let firstCard = null, secondCard = null, lock = false;
let moves = 0, matchedPairs = 0, startTime = null, timerInterval = null, duration = 0;
const board = document.getElementById('board');
const movesText = document.getElementById('moves') || { textContent: '0' };
const timeText = document.getElementById('time') || { textContent: '0' };

// Popup elements
const popup = document.getElementById('gamePopup');
const popupText = document.getElementById('popupText');
const replayBtn = document.getElementById('replayBtn');
const okBtn = document.getElementById('okBtn');

function showPopup(message, showReplay = true) {
  popupText.textContent = message;
  popup.style.display = 'flex';

  // Show or hide the replay button
  if (showReplay) {
    replayBtn.style.display = 'inline-block';
  } else {
    replayBtn.style.display = 'none';
  }

  // OK button always visible
  okBtn.onclick = () => {
    popup.style.display = 'none';
  };

  // Replay button refreshes page
  replayBtn.onclick = () => {
    location.reload();
  };
}


function initBoard(deck) {
  board.innerHTML = '';

  // Determine number of columns based on difficulty
  const cols = Math.ceil(Math.sqrt(deck.length));
  board.style.gridTemplateColumns = `repeat(${difficulty === 'hard' ? cols + 1 : cols}, 1fr)`;

  deck.forEach(src => {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.icon = src;

    card.innerHTML = `
      <div class="front">?</div>
      <div class="back">
        <img src="${src}" alt="icon">
      </div>
    `;

    card.addEventListener('click', flipCard);
    board.appendChild(card);
  });
}

function startTimer(){
  if (startTime === null) {
    startTime = Date.now();
    timerInterval = setInterval(() => {
      timeText.textContent = Math.floor((Date.now() - startTime) / 1000);
    }, 250);
  }
}

function stopTimer(){
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
}

function flipCard() {
  if (lock || this.classList.contains('matched') || this === firstCard) return;

  startTimer();
  this.classList.add('flipped');

  if (!firstCard) {
    firstCard = this;
  } else {
    secondCard = this;
    moves++; 
    if (movesText) movesText.textContent = moves;

    lock = true;

    checkMatch();
  }
}

function checkMatch() {
  if (firstCard.dataset.icon === secondCard.dataset.icon) {
    firstCard.classList.add('matched');
    secondCard.classList.add('matched');
    matchedPairs++;

    resetFlip();

    if (matchedPairs === (board.children.length / 2)) gameWon();
  } else {
    setTimeout(() => {
      firstCard.classList.remove('flipped');
      secondCard.classList.remove('flipped');
      resetFlip();
    }, 800);
  }
}

function resetFlip() {
  [firstCard, secondCard, lock] = [null, null, false];
}

function gameWon(){
  stopTimer();
  duration = Math.floor((Date.now() - startTime) / 1000);

  showPopup(
    `Bravo ! Vous avez gagné en ${duration}s et ${moves} coups.`,
    () => { // Rejouer
      matchedPairs = 0;
      moves = 0;
      movesText.textContent = '0';
      timeText.textContent = '0';
      startTime = null;
      initBoard(initialDeck);
    },
    () => { // OK
      console.log('User pressed OK');
    }
  );
}

// Save score endpoint
document.getElementById('saveScore').addEventListener('click', () => {
  if (!userId) { showPopup('Vous devez être connecté.'); return; }
  if (matchedPairs !== (board.children.length / 2)) { showPopup('Vous devez finir le jeu pour enregistrer.',false); return; }
  if (startTime === null) { showPopup('Vous devez jouer avant de sauvegarder.',false); return; }

  const payload = { user_id: userId, score: moves, duree: duration, difficulty };

  fetch('/save_score', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  .then(r => r.json())
  .then(j => {
    if (j.ok) showPopup('Score sauvegardé',false);
    else showPopup('Erreur: ' + (j.error || 'unknown'));
  })
  .catch(e => showPopup('Erreur: ' + e));
});

// Initialize
initBoard(initialDeck);
