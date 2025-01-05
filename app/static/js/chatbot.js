const chatInput = document.querySelector('.chat-input textarea');
const sendChatBtn = document.querySelector('.chat-input span');
const chatbox = document.querySelector('.chatbox');
const chatbotToggler = document.querySelector('.chatbot-toggler');
const chatbotWrapper = document.querySelector('.chatbot__wrapper');
const chatbotHeaderCloseBtn = document.querySelector('.chatbot header span') ;

let userMessage;

// vanilla js doesn't have dotenv, so flask is needed
const GEMINI_API_KEY = "AIzaSyBg2iS-gjeFujlOCrNIWQIBiMXR4fAriFE";
const inputInitHeight = chatInput.scrollHeight;

const API_URL = `https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${GEMINI_API_KEY}`

const createChatLi = (message, className) => {
  // create a chat li element with passed message and classname
  const chatLi = document.createElement("li");
  chatLi.classList.add("chat", className);

  let chatContent = className === "outgoing" ? `<p></p>` : `<span><i class="fa-solid fa-robot"></i></span><p></p>`;
  chatLi.innerHTML = chatContent;
  chatLi.querySelector("p").textContent = message
  return chatLi;
}

// Gemini AI here for now, may move it to flask backend
const generateResponse = async (incomingChatLi) => {
  const messageElement = incomingChatLi.querySelector("p")

  // post request
  try {
    const response = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        contents: [{
          parts: [{ text: userMessage }]
        }]
      })
    });

    const data = await response.json();
    const apiResponse = data?.candidates[0].content.parts[0].text;

    console.log(apiResponse)
    messageElement.textContent = apiResponse
  } catch (error) {
    console.log(error);
    // console.log('Message element:', messageElement);
    messageElement.classList.add("error");
    messageElement.textContent = "Oops! Something went wrong. Please try again.";
  } finally {
    chatbox.scrollTo(0, chatbox.scrollHeight);
  }
}

const handleChat = () => {
  userMessage = chatInput.value.trim();
  // console.log(userMessage)
  if (!userMessage) return;
  chatInput.value = "";
  chatInput.style.height = `${inputInitHeight}px` // revert back to default height once msg sent

  // append user message to chatbox
  chatbox.appendChild(createChatLi(userMessage, "outgoing"));
  chatbox.scrollTo(0, chatbox.scrollHeight);

  setTimeout(() => {
    // disiplay thinking while waiting response
    const incomingChatLi = createChatLi("Thinking...", "incoming")
    chatbox.appendChild(incomingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);
    generateResponse(incomingChatLi);
  }, 600)
}

// resize textarea height based on content
chatInput.addEventListener("input", () => {
  chatInput.style.height = `${inputInitHeight}px`
  chatInput.style.height = `${chatInput.scrollHeight}px`
});

// enter key without shift key and window width > 800
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey && window.innerWidth > 800) {
    e.preventDefault();
    handleChat();
  }
});

chatbotHeaderCloseBtn.addEventListener("click", () => {
  chatbotWrapper.classList.remove("show-chatbot");
});

// floating button actions
chatbotToggler.addEventListener("click", () => {
  chatbotWrapper.classList.toggle("show-chatbot");
});