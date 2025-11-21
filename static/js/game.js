
let firstCard=null, secondCard=null, lock=false;
let moves=0, matchedPairs=0, startTime=null, timerInterval=null , duration=0;
const board=document.getElementById('game-board');
const movesText=document.getElementById('moves');
const timeText=document.getElementById('time');

function initBoard(deck){
  board.innerHTML = '';

  const cols = Math.ceil(Math.sqrt(deck.length));
  board.style.gridTemplateColumns = `repeat(${difficulty === 'hard' ? cols+1 : cols}, 1fr)`;

  deck.forEach(src => {
    const card = document.createElement('div');
    card.className = 'card';
    card.dataset.icon = src;

    // Card container
    card.style.borderRadius = '15px';
    card.style.overflow = 'hidden';
    card.style.position = 'relative';
    card.style.perspective = '1000px';
    card.style.transformStyle = 'preserve-3d'; // crucial for flip

    card.innerHTML = `
      <div class="front" style="
          width:100%;
          height:100%;
          position:absolute;
          display:flex;
          justify-content:center;
          align-items:center;
          border-radius:15px;
          box-shadow:0 6px 12px rgba(0,0,0,0.2);
          font-family:'Patrick Hand', cursive;
          font-size:2rem;
          background: linear-gradient(145deg, #4d99dcff, #c24a72ff);
          color:#fff;
          backface-visibility:hidden;
          transition: transform 0.6s;
      ">?</div>
      <div class="back" style="
          width:100%;
          height:100%;
          position:absolute;
          display:flex;
          justify-content:center;
          align-items:center;
          border-radius:15px;
          box-shadow:0 6px 12px rgba(0,0,0,0.2);
          backface-visibility:hidden;
          transition: transform 0.6s;
      ">
          <img src="${src}" alt="icon" style="
              width:70%;
              height:70%;
              object-fit:contain;
              border-radius:12px;
          ">
      </div>
    `;

    card.addEventListener('click', flipCard);
    board.appendChild(card);
  });
}



function startTimer(){
  if(startTime === null){
    startTime = Date.now();
    timerInterval = setInterval(()=>{
      timeText.textContent = Math.floor((Date.now()-startTime)/1000);
    }, 250);
  }
}

function stopTimer(){
  if(timerInterval) clearInterval(timerInterval);
}

function flipCard(){
  if(lock || this.classList.contains('matched')) return;
  startTimer();
  this.classList.add('flipped');
  if(!firstCard) firstCard=this;
  else {
    secondCard=this; moves++; movesText.textContent=moves; checkMatch();
  }
}

function checkMatch(){
  if(firstCard.dataset.icon === secondCard.dataset.icon){
    firstCard.classList.add('matched'); secondCard.classList.add('matched'); matchedPairs++;
    if(matchedPairs === (board.children.length/2)) gameWon();
    resetFlip();
  } else {
    lock=true; setTimeout(()=>{ firstCard.classList.remove('flipped'); secondCard.classList.remove('flipped'); resetFlip(); }, 800);
  }
}

function resetFlip(){ [firstCard,secondCard,lock]=[null,null,false]; }

function gameWon(){
  stopTimer();
  duration = Math.floor((Date.now()-startTime)/1000);
  alert(`Bravo ! Vous avez gagné en ${duration}s et ${moves} coups.`);
}

document.getElementById('saveScore').addEventListener('click', ()=>{
  if(typeof userId === 'undefined' || userId === null){ alert('Vous devez être connecté.'); return; }
  if(startTime === null){ alert('Vous devez jouer avant de sauvegarder.'); return; }
  if(matchedPairs === (board.children.length/2)){
    const body = `user_id=${userId}&score=${moves}&duree=${duration}&difficulty=${encodeURIComponent(difficulty)}`;
  fetch('http://localhost/remindme/php/save_score.php', { method:'POST', headers:{'Content-Type':'application/x-www-form-urlencoded'}, body })
    .then(r=>r.json()).then(j=>alert(j.ok? 'Score sauvegardé':'Erreur: '+(j.error||''))).catch(e=>alert('Erreur: '+e));
  }else{
    alert('Vous pouvez finir le jeu pour enregistrer.')
  }
});

// initialize with deck passed from server
initBoard(initialDeck);
