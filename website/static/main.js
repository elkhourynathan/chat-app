const socket = io();

let messageContainer = document.querySelector(".messages");
let displayMessage = document.querySelector("#displayMessage");
let messageButton = document.getElementById("messageButton");

socket.on("connect", () => {
  let p = document.createElement("p");
  p.innerText = "Connected to chat room.  ";
  messageContainer.prepend(p);
});

messageButton.addEventListener("click", () => {
  fetch("http://127.0.0.1:8000/current_user")
    .then((response) => response.json())
    .then((data) => {
      socket.emit("message", {
        userName: data["user"],
        userMessage: userMessage.value,
      });
      userMessage.value = "";
    });
});

socket.on("message", (message) => {
  let messageContent = document.createElement("li");
  messageContent.classList.add("list-group-item");
  messageContent.innerText =
    message["userName"] + ": " + message["userMessage"];
  displayMessage.prepend(messageContent);
});
