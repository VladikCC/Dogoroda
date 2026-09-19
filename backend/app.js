const express = require('express');
const app = express();
const cors = require('cors');
app.use(cors());

app.get('/secretmessage', (req, res) => {
  res.send('The martians are hiding underground!');
})

app.listen(8080)

// Adds an event listener to the button that sends a GET request to the backend when clicked
document.querySelector('button').addEventListener('click', () => {
    // URL where the GET request will be sent
    fetch('http://localhost:8080secretmessage')
    // Obtains the text of the response in the form of a promise
    .then(res => res.text())
    // Changes the text of the paragraph to the response text
    .then(msg => document.querySelector('p').innerText = msg)
})