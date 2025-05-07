// Список отзывов
const reviews = [
    { text: "Отличный сервис! Персонал очень вежливый, а номера уютные.", author: "Мария Иванова" },
    { text: "Прекрасный отель! Вид из окна просто восхитительный.", author: "Алексей Петров" },
    { text: "Очень чисто и комфортно. Обязательно приедем снова!", author: "Екатерина Смирнова" },
    { text: "Отличное место, как для ночёвки, так и для досуга. Заселились в номера на Новый год, цены не завышали, арендовали сауну на Новый год тоже не завышали цены. В номерах и в сауне чисто, аккуратно, приятно находится. Персонал отзывчивый.", author: "Анна Венская" },
    { text: "Место замечательное - были в сауне с хамамом на 1 этаже, есть ещё в здании сауна с джакузи и хамам большой. Цена выше средней по городу. Но некритично. Мы были на первом этаже, посещали уже несколько раз. Места достаточно, есть столовая зона, бильярд, бассейн, небольшой хамам, сауна, комната отдыха.", author: "Светлана Королёва" },
    { text: "Персонал самый добрый из всех что встречал!", author: "Михаил Вершинин" }
  ];
  
  let reviewIndex = 0;
  const reviewBlock = document.querySelector(".review");
  const reviewTextElement = document.getElementById("review-text");
  const reviewAuthorElement = document.getElementById("review-author");
  
  function updateReview() {
    if (!reviewBlock) return;
    reviewBlock.classList.remove("active");
    setTimeout(() => {
      reviewIndex = (reviewIndex + 1) % reviews.length;
      reviewTextElement.textContent = reviews[reviewIndex].text;
      reviewAuthorElement.textContent = "- " + reviews[reviewIndex].author;
      reviewBlock.classList.add("active");
    }, 500);
  }
  
  // Автоматическое обновление отзыва каждые 7 секунд
  setInterval(updateReview, 7000);
  
  // Обработка формы обратной связи
  const contactForm = document.getElementById("contact-form");
  if (contactForm) {
    contactForm.addEventListener("submit", function(event) {
      event.preventDefault();
      let form = this;
      let formData = new FormData(form);
  
      fetch(form.action, {
        method: form.method,
        body: formData,
        headers: { "Accept": "application/json" }
      })
      .then(response => {
        const message = document.getElementById("response-message");
        if (response.ok) {
          message.style.display = "block";
          message.textContent = "Ваше сообщение отправлено!";
          form.reset();
        } else {
          message.textContent = "Ошибка при отправке формы. Пожалуйста, попробуйте позже.";
          message.style.display = "block";
        }
      })
      .catch(() => {
        const message = document.getElementById("response-message");
        message.textContent = "Произошла ошибка. Пожалуйста, попробуйте позже.";
        message.style.display = "block";
      });
    });
  }
  