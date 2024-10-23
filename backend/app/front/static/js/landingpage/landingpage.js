$(function () {

  // scroll

  $(".scroll-link").on("click", function (t) {
      var o = $(this);
      $("html, body").stop().animate({
          scrollTop: $(o.attr("href")).offset().top - 160
      }, 1e3), t.preventDefault()
  })

  // fixed header

  $(window).scroll(function () {
      if ($(window).scrollTop() >= 60) {
          $('header').addClass('fixed-header');
      } else {
          $('header').removeClass('fixed-header');
      }
  });

  // Aos

  AOS.init({
      once: true,
  });


  // Review Slider

  $('.review-slider .owl-carousel').owlCarousel({
      loop: true,
      margin: 0,
      dots: true,
      autoplay: true,
      autoplayTimeout: 5000,
      autoplayHoverPause: true,
      responsive: {
          0: {
              items: 1
          },
          1024: {
              items: 2
          },
          1200: {
              items: 3
          }
      }
  })

});