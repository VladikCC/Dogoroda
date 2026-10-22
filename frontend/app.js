console.log("Loaded")

const results = document.getElementById("results")
const loading = document.getElementById("loading")

const button = document.querySelector("button");
const input = document.querySelector("input");
button.addEventListener("click", (event) => {
    const query = input.value;
    const url = `/search/${encodeURIComponent(query)}`;

    let dots = window.setInterval(() => {
        if (loading.innerHTML.length > 2)
            loading.innerHTML = '.'
        else
            loading.innerHTML += '.'
    }, 400)

    console.log(url);
    getData(url).then(() => {
        clearInterval(dots)
        loading.innerHTML = ''
    });
})

async function getData(url) {
    try {
        const response = await fetch(url)
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }

        const result = await response.json();

        console.log(result);
        results.insertAdjacentHTML("beforeend", "<p>Results:</p>");

        result.items.forEach(item => {
            const resultHtml = `
                <div style="display: flex; ">
                    <img style="padding-right: 12px; height: 150px; width: 150px" src="${item.img}">
                    <div>
                        <a src="${item.url}"><h2>${item.title}</h2></a>
                        <h2>${item.price}</h2>
                        <p>${item.shop}</p>
                    </div>
                </div>
            `;
            results.insertAdjacentHTML("beforeend", resultHtml);
        });    
    }
    catch (error) {
        console.error(error.message);
    }
}