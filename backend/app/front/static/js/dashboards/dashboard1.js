document.addEventListener("DOMContentLoaded", function () {

  //=====================================
  // Theme Onload Toast
  //=====================================
  window.addEventListener("load", () => {
    let myAlert = document.querySelectorAll('.toast')[0];
    if (myAlert) {
      let bsAlert = new bootstrap.Toast(myAlert);
      bsAlert.show();
    }
  })

  // -----------------------------------------------------------------------
  // Customers
  // -----------------------------------------------------------------------

  var options = {
    chart: {
      id: "customers",
      type: "area",
      height: 70,
      sparkline: {
        enabled: true,
      },
      group: "sparklines",
      fontFamily: "inherit",
      foreColor: "#adb0bb",
    },
    series: [
      {
        name: "customers",
        color: "var(--bs-secondary)",
        data: [36, 45, 31, 47, 38, 43],
      },
    ],
    stroke: {
      curve: "smooth",
      width: 2,
    },
    fill: {
      type: "gradient",
      color: "var(--bs-secondary)",

      gradient: {
        shadeIntensity: 0,
        inverseColors: false,
        opacityFrom: 0.2,
        opacityTo: 0.1,
        stops: [100],
      },
    },

    markers: {
      size: 0,
    },
    tooltip: {
      theme: "dark",
      fixed: {
        enabled: true,
        position: "right",
      },
      x: {
        show: false,
      },
    },
  };
  new ApexCharts(document.querySelector("#customers"), options).render();

  // -----------------------------------------------------------------------
  // Projects
  // -----------------------------------------------------------------------
  var chart_bounce_rate = {
    series: [
      {
        name: "Project",
        labels: ["2012", "2013", "2014", "2015", "2016", "2017"],
        data: [3, 5, 5, 7, 6, 5, 3, 5, 3],
      },
    ],
    chart: {
      fontFamily: "inherit",
      height: 46,
      type: "bar",
      offsetX: -10,
      toolbar: {
        show: false,
      },
      sparkline: {
        enabled: true,
      },
    },
    colors: ["var(--bs-white)"],
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: "55%",
        endingShape: "flat",
        borderRadius: 4,
      },
    },
    tooltip: {
      theme: "dark",
      followCursor: true,
    },
  };
  var chart_line_basic = new ApexCharts(
    document.querySelector("#projects"),
    chart_bounce_rate
  );
  chart_line_basic.render();

  // -----------------------------------------------------------------------
  // Revenue Forecast
  // -----------------------------------------------------------------------

  var chart = {
    series: [
      {
        name: "2023",
        data: [50, 60, 30, 55, 75, 60, 100, 120],
      },

      {
        name: "2022",
        data: [35, 45, 40, 50, 35, 55, 40, 45],
      },
      {
        name: "2024",
        data: [100, 75, 80, 40, 20, 40, 0, 25],
      },
    ],
    chart: {
      toolbar: {
        show: false,
      },
      type: "area",
      fontFamily: "inherit",
      foreColor: "#adb0bb",
      height: 300,
      width: "100%",
      stacked: false,
      offsetX: -10,
    },
    colors: ["var(--bs-danger)", "var(--bs-secondary)", "var(--bs-primary)"],
    plotOptions: {},
    dataLabels: {
      enabled: false,
    },
    legend: {
      show: false,
    },
    stroke: {
      width: 2,
      curve: "monotoneCubic",
    },
    grid: {
      show: true,
      padding: {
        top: 0,
        bottom: 0,
      },
      borderColor: "rgba(0,0,0,0.05)",
      xaxis: {
        lines: {
          show: true,
        },
      },
      yaxis: {
        lines: {
          show: true,
        },
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        shadeIntensity: 0,
        inverseColors: false,
        opacityFrom: 0.1,
        opacityTo: 0.01,
        stops: [0, 100],
      },
    },
    xaxis: {
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      categories: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "July", "Aug"],
    },
    markers: {
      strokeColor: [
        "var(--bs-danger)",
        "var(--bs-secondary)",
        "var(--bs-primary)",
      ],
      strokeWidth: 2,
    },
    tooltip: {
      theme: "dark",
    },
  };

  var chart = new ApexCharts(
    document.querySelector("#revenue-forecast"),
    chart
  );
  chart.render();

  // =====================================
  // Your Preformance
  // =====================================

  var options = {
    series: [20, 20, 20, 20, 20],
    labels: ["245", "45", "14", "78", "95"],
    chart: {
      height: 205,
      fontFamily: "inherit",
      type: "donut",
    },
    plotOptions: {
      pie: {
        startAngle: -90,
        endAngle: 90,
        offsetY: 10,
        donut: {
          size: "90%",
        },
      },
    },
    grid: {
      padding: {
        bottom: -80,
      },
    },
    legend: {
      show: false,
    },
    dataLabels: {
      enabled: false,
      name: {
        show: false,
      },
    },
    stroke: {
      width: 2,
      colors: "var(--bs-card-bg)",
    },
    tooltip: {
      fillSeriesColor: false,
    },
    colors: [
      "var(--bs-danger)",
      "var(--bs-warning)",
      "var(--bs-warning-bg-subtle)",
      "var(--bs-secondary-bg-subtle)",
      "var(--bs-secondary)",
    ],
    responsive: [{
      breakpoint: 1400,
      options: {
        chart: {
          height: 170
        },
      },
    }],
  };

  var chart = new ApexCharts(
    document.querySelector("#your-preformance"),
    options
  );
  chart.render();

  // -----------------------------------------------------------------------
  // Customers Area
  // -----------------------------------------------------------------------
  var chart_users = {
    series: [
      {
        name: "April 07 ",
        data: [0, 20, 15, 19, 14, 25, 30],
      },
      {
        name: "Last Week",
        data: [0, 8, 19, 13, 26, 16, 25],
      },
    ],
    chart: {
      fontFamily: "inherit",
      height: 100,
      type: "line",
      toolbar: {
        show: false,
      },
      sparkline: {
        enabled: true,
      },
    },
    colors: ["var(--bs-primary)", "var(--bs-primary-bg-subtle)"],
    grid: {
      show: false,
    },
    stroke: {
      curve: "smooth",
      colors: ["var(--bs-primary)", "var(--bs-primary-bg-subtle)"],
      width: 2,
    },
    markers: {
      colors: ["var(--bs-primary)", "var(--bs-primary-bg-subtle)"],
      strokeColors: "transparent",
    },
    tooltip: {
      theme: "dark",
      x: {
        show: false,
      },
      followCursor: true,
    },
  };
  var chart_line_basic = new ApexCharts(
    document.querySelector("#customers-area"),
    chart_users
  );
  chart_line_basic.render();

  // -----------------------------------------------------------------------
  // Sales Overview
  // -----------------------------------------------------------------------
  var options = {
    series: [50, 80, 30],
    labels: ["36%", "10%", "36%"],
    chart: {
      type: "radialBar",
      height: 230,
      fontFamily: "inherit",
      foreColor: "#c6d1e9",
    },
    plotOptions: {
      radialBar: {
        inverseOrder: false,
        startAngle: 0,
        endAngle: 270,
        hollow: {
          margin: 1,
          size: "40%",
        },
        dataLabels: {
          show: false,
        },
      },
    },
    legend: {
      show: false,
    },
    stroke: { width: 1, lineCap: "round" },
    tooltip: {
      enabled: false,
      fillSeriesColor: false,
    },
    colors: ["var(--bs-primary)", "var(--bs-secondary)", "var(--bs-danger)"],
  };

  var chart = new ApexCharts(
    document.querySelector("#sales-overview"),
    options
  );
  chart.render();

  // -----------------------------------------------------------------------
  // Total settlements
  // -----------------------------------------------------------------------
  var settlements = {
    series: [
      {
        name: "settlements",
        data: [
          40, 40, 80, 80, 30, 30, 10, 10, 30, 30, 100, 100, 20, 20, 140, 140,
        ],
      },
    ],
    chart: {
      fontFamily: "inherit",
      type: "line",
      height: 300,
      toolbar: { show: !1 },
    },
    legend: { show: !1 },
    dataLabels: { enabled: !1 },
    stroke: {
      curve: "smooth",
      show: !0,
      width: 2,
      colors: ["var(--bs-primary)"],
    },
    xaxis: {
      categories: [
        "1W",
        "",
        "3W",
        "",
        "5W",
        "6W",
        "7W",
        "8W",
        "9W",
        "",
        "11W",
        "",
        "13W",
        "",
        "15W",
      ],
      axisBorder: { show: !1 },
      axisTicks: { show: !1 },
      tickAmount: 6,
      labels: {
        rotate: 0,
        rotateAlways: !0,
        style: { fontSize: "10px", colors: "#adb0bb", fontWeight: "600" },
      },
    },
    yaxis: {
      show: false,
      tickAmount: 3,
    },
    tooltip: {
      theme: "dark",
    },
    colors: ["var(--bs-primary)"],
    grid: {
      borderColor: "var(--bs-primary-bg-subtle)",
      strokeDashArray: 4,
      yaxis: { show: false },
    },
    markers: {
      strokeColor: ["var(--bs-primary)"],
      strokeWidth: 3,
    },
  };

  var chart_area_spline = new ApexCharts(
    document.querySelector("#settlements"),
    settlements
  );
  chart_area_spline.render();
});
