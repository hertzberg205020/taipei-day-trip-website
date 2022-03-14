let attraction_list = [];
let next_page = 0;
let userKeyword = null;
let isloading = false;
const URL = "/api/attractions";
async function loadAttractionsData(page = next_page, keyword = userKeyword) {
  if (next_page == null) {
    return;
  }
  if (!isloading) {
    isloading = true;
    let src =
      userKeyword != null
        ? `${URL}?page=${page}&keyword=${keyword}`
        : `${URL}?page=${page}`;
    await fetch(src)
      .then(function (response) {
        return response.json();
      })
      .then(function (result) {
        attraction_list = []; // 清空list

        if (result["data"].length == 0) {
          next_page = 0;
          attraction_list.push("未搜尋到結果");
          isloading = false;
        }

        data_list = result["data"];
        for (i = 0; i < data_list.length; i++) {
          attraction = data_list[i];
          attraction_list.push(attraction);
        }
        next_page = result["nextPage"];
      });
    isloading = false;
  }
}
function getFirstImg(index) {
  return (img_url = attraction_list[index]["images"][0]);
}
function getName(index) {
  return attraction_list[index]["name"];
}
function getMRT(index) {
  return attraction_list[index]["mrt"] != null
    ? attraction_list[index]["mrt"]
    : "附近無捷運";
}
function getCategory(index) {
  return attraction_list[index]["category"];
}

async function createBoxes() {
  let boundIndex = Math.min(12, attraction_list.length);
  let boxesContainer = document.getElementById("boxes_container");
  if (attraction_list.length == 1 && attraction_list[0] == "未搜尋到結果") {
    boxesContainer.innerHTML = "未搜尋到結果";
    attraction_list.pop();
    return;
  }

  let fragment = document.createDocumentFragment();

  attraction_list.reverse();
  for (let i = boundIndex - 1; i >= 0; i--) {
    let boxesContainer = document.getElementById("boxes_container");
    let fragment = document.createDocumentFragment();

    let box = document.createElement("div");
    box.className = "box";
    // 圖
    let picture = document.createElement("img");
    picture.src = getFirstImg(i);
    picture.className = "picture";
    // 文
    let attractionInfo = document.createElement("div");
    attractionInfo.className = "attraction_info";

    let name = document.createElement("div");
    name.className = "attreaction_name";
    let mrt = document.createElement("div");
    let category = document.createElement("div");

    name.appendChild(document.createTextNode("" + getName(i)));

    let attractionIntro = document.createElement("div");
    attractionIntro.className = "attraction_intro";
    mrt.appendChild(document.createTextNode("" + getMRT(i)));
    category.appendChild(document.createTextNode("" + getCategory(i)));

    attractionIntro.appendChild(mrt);
    attractionIntro.appendChild(category);

    attractionInfo.appendChild(name);
    attractionInfo.appendChild(attractionIntro);

    box.appendChild(picture);
    box.appendChild(attractionInfo);
    fragment.appendChild(box);
    boxesContainer.appendChild(fragment);
    attraction_list.pop();
  }
  attraction_list = [];
}

async function init() {
  await loadAttractionsData();
  createBoxes();
}

async function main() {
  const searchBtn = document.getElementById("search_btn");
  const searchContent = document.getElementById("search_content");
  const boxesContainer = document.getElementById("boxes_container");
  await init();
  // console.log(next_page);
  window.addEventListener("scroll", async function () {
    if (
      Math.ceil(window.scrollY + window.innerHeight) >=
      document.body.offsetHeight
    ) {
      if (next_page != null) {
        await loadAttractionsData();
        createBoxes();
      }
    }
  });
  searchBtn.addEventListener("click", async function (evt) {
    let inputkeyword = searchContent.value;
    boxesContainer.innerHTML = ""; // 清除原先的景點資訊
    userKeyword = inputkeyword;
    next_page = 0;
    await loadAttractionsData(0, inputkeyword);
    createBoxes();
  });
}
window.onload = main;
