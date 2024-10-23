var UIIdleTimeout = (function () {
  return {
    init: function () {
      var o;
      $("body").append(""),
        $.idleTimeout("#idle-timeout-dialog", ".modal-content button:last", {
          idleAfter: 5,
          timeout: 3e4,
          pollingInterval: 5,
          keepAliveURL: "/keep-alive",
          serverResponseEquals: "OK",
          onTimeout: function () {
            window.location = "authentication-two-steps.html";
          },
          onIdle: function () {
            $("#idle-timeout-dialog").modal("show"),
              (o = $("#idle-timeout-counter")),
              $("#idle-timeout-dialog-keepalive").on("click", function () {
                $("#idle-timeout-dialog").modal("hide");
              });
          },
          onCountdown: function (e) {
            o.html(e);
          },
        });
    },
  };
})();
jQuery(function () {
  UIIdleTimeout.init();
});
