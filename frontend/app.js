console.log("Loaded")

const button = document.querySelector("button");
const input = document.querySelector("input");
button.addEventListener("click", (event) => {
    const query = input.value;
    const url = `http://127.0.0.1:8001/search/${query}`;

    console.log(input.value)
    console.log(url);
    getData(url);
})

async function getData(url) {
    try {
        const response = await fetch(url)
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const result = await response.json();
        console.log(result);
    }
    catch (error) {
        console.error(error.message);
    }
}