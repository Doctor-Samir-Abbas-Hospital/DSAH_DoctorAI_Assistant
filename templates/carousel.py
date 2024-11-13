import streamlit as st

# HTML, CSS, and JS for carousel
carousel_html = """
<div style="width: 350px; height: 250px;">
  <!-- Carousel Styles -->
  <style>
    * { margin: 0 !important; padding: 0; }
    
    /* Normal carousel non-hover styles */
    .carousel {
        position: relative;
        overflow: hidden;
        width: 350px;
        height: 250px;
        z-index: 10001;
    }
    
    .carousel-content {
        display: flex;
        margin: 150px 0 70px;
        transition: 500ms;
    }
    
    @media(max-width: 1024px) {
        .carousel-content {
            margin: 100px 0 50px;
        }
    }
    
    @media(max-width: 800px) {
        .carousel-content {
            margin: 70px 0 30px;
        }
    }
    
    .carousel-content img {
        height: 100%;
        width: 100%;
        object-fit: cover;
    }
    
    .carousel .carousel-control-left, .carousel .carousel-control-right { 
      position: absolute; top: 0; bottom: 0; width: 10%; cursor: pointer; z-index: 1; 
    }
    .carousel .carousel-control-left { left: 0; }
    .carousel .carousel-control-right { right: 0; }
  </style>

  <!-- Carousel Structure -->
  <div class="carousel" data-carousel="1" data-speed="2000">
  <span class="carousel-control-left"></span>
  <span class="carousel-control-right"></span>
  <div class="carousel-content">
    <!-- add extra last pic first and extra first pic last for hover effect to work properly  -->
    <img src="https://images.pexels.com/photos/1141853/pexels-photo-1141853.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260" alt="image 5" />
    <img src="https://images.pexels.com/photos/1714208/pexels-photo-1714208.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260" alt="image 1" />
    <img src="https://images.pexels.com/photos/1874613/pexels-photo-1874613.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260" alt="image 2" />

    <img src=" https://images.pexels.com/photos/1878715/pexels-photo-1878715.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260" alt="image 3" />

    <img src="https://images.pexels.com/photos/257360/pexels-photo-257360.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260" alt="image 4" />

    <img src="https://images.pexels.com/photos/1141853/pexels-photo-1141853.jpeg?auto=compress&cs=tinysrgb&dpr=2&h=750&w=1260" alt="image 5" />
    <video src="https://www.dsah.sa/sites/default/files/2023-03/DSAH-web-bannr-video.mp4" autoplay muted loop></video>

  </div>
</div>

  <!-- JavaScript for Carousel -->
  <script>
    if (document.querySelectorAll(".carousel").length > 0) {
  let carousels = document.querySelectorAll(".carousel");
  carousels.forEach(carousel => newCarousel(carousel));

  function newCarousel(carousel) {
    let carouselChildren = document.querySelector(
      `.carousel[data-carousel="${carousel.dataset.carousel}"]`
    ).children;
    let speed = carousel.dataset.speed;
    let carouselContent = document.querySelectorAll(`.carousel-content`)[
      carousel.dataset.carousel - 1
    ];
    const carouselLength = carouselContent.children.length;
    let width = window.innerWidth;
    let count = width;
    let counterIncrement = width;
    let int = setInterval(timer, speed);

    // initial transform
    carouselContent.style.transform = `translateX(-${width}px)`;

    function timer() {
      if (count >= (counterIncrement - 2) * (carouselLength - 2)) {
        count = 0;
        carouselContent.style.transform = `translateX(-${count}px)`;
      }
      count = count + counterIncrement;
      carouselContent.style.transform = `translateX(-${count}px)`;
    }

    function carouselClick() {
      // left click
      carouselChildren[0].addEventListener("click", function() {
        count = count - width;
        carouselContent.style.transform = `translateX(-${count - 100}px)`;
        if (count < counterIncrement) {
          count = counterIncrement * (carouselLength - 2);
          carouselContent.style.transform = `translateX(-${count - 100}px)`;
        }
      });
      // right click
      carouselChildren[1].addEventListener("click", function() {
        count = count + width;
        carouselContent.style.transform = `translateX(-${count + 100}px)`;
        if (count >= counterIncrement * (carouselLength - 1)) {
          count = counterIncrement;
          carouselContent.style.transform = `translateX(-${count + 100}px)`;
        }
      });
    }

    function carouselHoverEffect() {
      // left hover effect events
      carouselChildren[0].addEventListener("mouseenter", function() {
        carouselContent.style.transform = `translateX(-${count - 100}px)`;
        clearInterval(int);
      });
      carouselChildren[0].addEventListener("mouseleave", function() {
        carouselContent.style.transform = `translateX(-${count}px)`;
        int = setInterval(timer, speed);
      });

      // right hover effect events
      carouselChildren[1].addEventListener("mouseenter", function() {
        carouselContent.style.transform = `translateX(-${count + 100}px)`;
        clearInterval(int);
      });
      carouselChildren[1].addEventListener("mouseleave", function() {
        carouselContent.style.transform = `translateX(-${count}px)`;
        int = setInterval(timer, speed);
      });
    }

    carouselHoverEffect();
    carouselClick();
  }
}
  </script>
</div>
"""
