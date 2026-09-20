const conversation = document.querySelector('#conversation');
const form = document.querySelector('#chatForm');
const input = document.querySelector('#messageInput');
const clearChat = document.querySelector('#clearChat');
const conversationHistory = [];

async function askTutor() {
  const response = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ messages: conversationHistory })
  });

  const responseBody = await response.text();
  let data = {};

  try {
    data = JSON.parse(responseBody);
  } catch {
    if (!response.ok) {
      throw new Error('The tutor server did not return a valid response.');
    }
    throw new Error('The tutor server returned an invalid response.');
  }

  if (!response.ok) {
    throw new Error(data.error || 'The tutor could not respond.');
  }

  if (!data.text) {
    throw new Error('The tutor returned no answer.');
  }

  conversationHistory.push({ role: 'assistant', content: data.text });
  return data.text;
}

async function addMessage(question) {
  const userRow = document.createElement('div');
  userRow.className = 'message-row user-row';
  userRow.innerHTML = `<div class="avatar">you</div><div class="message-content"><div class="message-bubble user-bubble"></div></div>`;
  userRow.querySelector('.user-bubble').textContent = question;
  conversation.appendChild(userRow);

  conversationHistory.push({ role: 'user', content: question });
  const tutorRow = document.createElement('div');
  tutorRow.className = 'message-row tutor-row';
  tutorRow.innerHTML = `<div class="avatar tutor-avatar">∑</div><div class="message-content"><div class="message-bubble tutor-bubble">Thinking through your problem...</div><div class="hint-card"><p></p></div><div class="guided-actions"><button class="chip-button next-hint" type="button" disabled>Next hint</button><button class="chip-button" type="button" data-prompt="I tried that step, can you check my reasoning?">Check my reasoning</button></div></div>`;
  const hint = tutorRow.querySelector('.hint-card p');
  const nextButton = tutorRow.querySelector('.next-hint');
  conversation.appendChild(tutorRow);

  try {
    hint.textContent = await askTutor();
    tutorRow.querySelector('.tutor-bubble').textContent = 'Here’s your first foothold. I’m holding back the answer so you get a chance to make the connection:';
    nextButton.disabled = false;
    nextButton.addEventListener('click', async () => {
      nextButton.disabled = true;
      nextButton.textContent = 'Thinking...';
      conversationHistory.push({ role: 'user', content: 'Give me exactly one more hint. Do not reveal the final answer yet.' });
      try {
        hint.textContent = await askTutor();
        nextButton.textContent = 'That’s enough for now';
      } catch (error) {
        hint.textContent = error.message;
        nextButton.textContent = 'Try again';
        nextButton.disabled = false;
      }
    }, { once: true });
  } catch (error) {
    tutorRow.querySelector('.tutor-bubble').textContent = 'The tutor is unavailable right now.';
    hint.textContent = error.message;
    nextButton.remove();
  }
  tutorRow.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function submitQuestion(question) {
  const cleanQuestion = question.trim();
  if (!cleanQuestion) return;
  addMessage(cleanQuestion);
  input.value = '';
  input.style.height = 'auto';
}

form.addEventListener('submit', (event) => {
  event.preventDefault();
  submitQuestion(input.value);
});

document.addEventListener('click', (event) => {
  const promptButton = event.target.closest('[data-prompt]');
  if (promptButton) submitQuestion(promptButton.dataset.prompt);
});

input.addEventListener('input', () => {
  input.style.height = 'auto';
  input.style.height = `${Math.min(input.scrollHeight, 120)}px`;
});

input.addEventListener('keydown', (event) => {
  if (event.key === 'Enter' && !event.shiftKey) {
    event.preventDefault();
    form.requestSubmit();
  }
});

clearChat.addEventListener('click', () => {
  conversation.querySelectorAll('.user-row, .tutor-row:not(.initial-message)').forEach((message) => message.remove());
  conversationHistory.length = 0;
  input.focus();
});
